# r_wrapper

[![pypi version](https://img.shields.io/pypi/v/r_wrapper.svg)](https://pypi.org/project/r_wrapper/)
[![license](https://img.shields.io/pypi/l/r_wrapper.svg)](https://pypi.org/project/r_wrapper/)

Warning: still highly experimental and likely to break.

Seamlessly integrate R packages in Python by allowing intuitive importing and providing opinionated data type conversion functions.


## Installation

```bash
pip install r_wrapper
```


## Usage

For example, accessing `biomaRt` can be as simple as follows:
```python
from r_wrapper import biomaRt

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

Check the `r_wrapper/tests/` directory for more examples showing how to rewrite R scripts in Python.


## Tests

A comprehensive test suite aims at providing stability and avoiding regressions.
The examples in `r_wrapper/tests/` are validated using `pytest`.

Run tests as follows:
```bash
$ pytest r_wrapper/
```
