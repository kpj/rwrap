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

For example, accessing Bioconductor's [biomaRt](https://bioconductor.org/packages/release/bioc/html/biomaRt.html) package can be as simple as follows:
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

Check the `tests/` directory for more examples showing how to rewrite R scripts in Python.


## Tests

A comprehensive test suite aims at providing stability and avoiding regressions.
The examples in `tests/` are validated using `pytest`.

Run tests as follows:

```bash
$ pytest tests/
```
