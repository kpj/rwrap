# rwrap

[![PyPI](https://img.shields.io/pypi/v/rwrap.svg?style=flat)](https://pypi.python.org/pypi/rwrap)
[![Tests](https://github.com/kpj/rwrap/actions/workflows/main.yml/badge.svg)](https://github.com/kpj/rwrap/actions/workflows/main.yml)

A thin wrapper around [rpy2](https://rpy2.github.io/doc/latest/html/index.html) with strong opinions on how data types should be converted. This enables easy usage of R packages from Python with no boilerplate code.

> Warning: still work-in-progress, issues and PRs welcome


## Installation

```bash
pip install rwrap
```


## Usage

### Genomic Annotations

Accessing Bioconductor's [biomaRt](https://bioconductor.org/packages/release/bioc/html/biomaRt.html) package can be as simple as follows:
```python
from rwrap import biomaRt

biomaRt
## <module 'biomaRt' from '/Library/Frameworks/R.framework/Versions/4.1/Resources/library/biomaRt'>

snp_list = ["rs7329174", "rs4948523", "rs479445"]
ensembl = biomaRt.useMart("ENSEMBL_MART_SNP", dataset="hsapiens_snp")

df = biomaRt.getBM(
    attributes=["refsnp_id", "chr_name", "chrom_start", "consequence_type_tv"],
    filters="snp_filter", values=snp_list, mart=ensembl
)

print(df)  # pandas.DataFrame
##    refsnp_id  chr_name  chrom_start     consequence_type_tv
## 1   rs479445         1     60875960          intron_variant
## 2   rs479445         1     60875960  NMD_transcript_variant
## 3  rs4948523        10     58579338          intron_variant
## 4  rs7329174        13     40983974          intron_variant
```

### Differential Gene Expression analysis workflow

Differentially expressed genes between conditions can be determined using [DESeq2](https://bioconductor.org/packages/release/bioc/html/DESeq2.html) and annotated with [biomaRt](https://bioconductor.org/packages/release/bioc/html/biomaRt.html):

```python
import pandas as pd
from rwrap import DESeq2, biomaRt, base, stats


DESeq2
## <module 'DESeq2' from '/Library/Frameworks/R.framework/Versions/4.1/Resources/library/DESeq2'>
biomaRt
## <module 'biomaRt' from '/Library/Frameworks/R.framework/Versions/4.1/Resources/library/biomaRt'>


# retrieve count data (https://trace.ncbi.nlm.nih.gov/Traces/sra/?study=SRP009615)
df_counts = pd.read_csv(
    "http://duffel.rail.bio/recount/v2/SRP009615/counts_gene.tsv.gz", sep="\t"
).set_index("gene_id")
df_design = pd.DataFrame(
    {"condition": ["1", "2", "1", "2", "3", "4", "3", "4", "5", "6", "5", "6"]}
)

# run differential gene expression analysis
dds = DESeq2.DESeqDataSetFromMatrix(
    countData=df_counts, colData=df_design, design=stats.as_formula("~ condition")
)
dds = DESeq2.DESeq(dds)

res = DESeq2.results(dds, contrast=("condition", "1", "2"))
df_res = base.as_data_frame(res)

# annotate result
ensembl = biomaRt.useEnsembl(biomart="genes", dataset="hsapiens_gene_ensembl")
df_anno = biomaRt.getBM(
    attributes=["ensembl_gene_id_version", "gene_biotype"],
    filters="ensembl_gene_id_version",
    values=df_res.index,
    mart=ensembl,
).set_index("ensembl_gene_id_version")

df_res = df_res.merge(df_anno, left_index=True, right_index=True).sort_values("padj")
print(df_res.head())  # pd.DataFrame
##                      baseMean  log2FoldChange     lfcSE      stat        pvalue          padj          gene_biotype
## ENSG00000222806.1  158.010377       22.137400  2.745822  8.062214  7.492501e-16  2.853744e-11       rRNA_pseudogene
## ENSG00000255099.1   65.879611       21.835651  2.915452  7.489627  6.906949e-14  1.315359e-09  processed_pseudogene
## ENSG00000261065.1   92.351998       22.273400  3.144991  7.082182  1.419019e-12  1.351190e-08                lncRNA
## ENSG00000249923.1  154.037908       18.364027  2.636083  6.966407  3.251381e-12  2.476772e-08                lncRNA
## ENSG00000267658.1   64.371181      -19.545702  3.041247 -6.426871  1.302573e-10  8.268736e-07                lncRNA
```

### Geneset Enrichment Analysis

Geneset enrichment analyses can be conducted using [clusterProfiler](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html):

```python
from rwrap import clusterProfiler, base


clusterProfiler
## <module 'clusterProfiler' from '/Library/Frameworks/R.framework/Versions/4.1/Resources/library/clusterProfiler'>


genelist = [8318, 991, 9133, 890, 983, 4085, 7272, 1111, 891, 4174, 9232]

res = clusterProfiler.enrichKEGG(gene=genelist, organism="hsa", pvalueCutoff=0.05)
df = base.as_data_frame(res)

print(df.head())  # pd.DataFrame
##                 ID                              Description GeneRatio   BgRatio        pvalue      p.adjust        qvalue                                             geneID  Count
## hsa04110  hsa04110                               Cell cycle     11/11  126/8115  8.124144e-21  1.462346e-19  6.841384e-20  8318/991/9133/890/983/4085/7272/1111/891/4174/...     11
## hsa04114  hsa04114                           Oocyte meiosis      6/11  131/8115  6.823856e-09  6.141470e-08  2.873202e-08                         991/9133/983/4085/891/9232      6
## hsa04914  hsa04914  Progesterone-mediated oocyte maturation      5/11  102/8115  1.237164e-07  7.266746e-07  3.399647e-07                              9133/890/983/4085/891      5
## hsa05166  hsa05166  Human T-cell leukemia virus 1 infection      6/11  222/8115  1.614832e-07  7.266746e-07  3.399647e-07                        991/9133/890/4085/1111/9232      6
## hsa04218  hsa04218                      Cellular senescence      5/11  156/8115  1.036418e-06  3.731103e-06  1.745545e-06                              9133/890/983/1111/891      5
```

### More examples

Check the `tests/scripts` directory for more examples showing how to rewrite R scripts in Python.


## Tests

A comprehensive test suite aims at providing stability and avoiding regressions.
The examples in `tests/` are validated using `pytest`.

Run tests as follows:

```bash
$ pytest tests/
```
