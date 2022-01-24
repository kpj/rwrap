import pandas as pd

from rwrap import base, stats, DESeq2, biomaRt


# read data (https://trace.ncbi.nlm.nih.gov/Traces/sra/?study=SRP009615)
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
    attributes=["ensembl_gene_id_version", "description", "gene_biotype"],
    filters="ensembl_gene_id_version",
    values=df_res.index,
    mart=ensembl,
).set_index("ensembl_gene_id_version")

df_res = df_res.merge(df_anno, left_index=True, right_index=True)

# save result
(
    df_res.reset_index()
    .rename(columns={"index": "gene"})
    .to_csv("result.csv", index=False)
)
