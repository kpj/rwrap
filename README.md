# rwrap

[![PyPI](https://img.shields.io/pypi/v/rwrap.svg?style=flat)](https://pypi.python.org/pypi/rwrap)
[![Tests](https://github.com/kpj/rwrap/workflows/Tests/badge.svg)](https://github.com/kpj/rwrap/actions)

> Warning: still a work-in-progress, always happy about issues and PRs

A thin wrapper around rpy2 with strong opinions on how data types should be converted.


## Installation

```bash
pip install rwrap
```


## Usage

For example, accessing `biomaRt` can be as simple as follows:
```python
from rwrap import biomaRt

snp_list = ['rs7329174', 'rs4948523', 'rs479445']
ensembl = biomaRt.useMart('ENSEMBL_MART_SNP', dataset='hsapiens_snp')

df = biomaRt.getBM(
    attributes=['refsnp_id', 'chr_name', 'chrom_start', 'consequence_type_tv'],
    filters='snp_filter', values=snp_list, mart=ensembl)

print(df)  # pandas.DataFrame
#    refsnp_id  chr_name  chrom_start     consequence_type_tv
# 1   rs479445         1     60875960          intron_variant
# 2   rs479445         1     60875960  NMD_transcript_variant
# 3  rs4948523        10     58579338          intron_variant
# 4  rs7329174        13     40983974          intron_variant
```

Check the `tests/` directory for more examples showing how to rewrite R scripts in Python.


## Tests

A comprehensive test suite aims at providing stability and avoiding regressions.
The examples in `tests/` are validated using `pytest`.

Run tests as follows:

```bash
$ pytest tests/
```
