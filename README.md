# r_wrapper

Seamlessly use R packages in Python.
Warning: still highly experimental and likely to break.


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
```


## Tests

A comprehensive test suite aims at providing stability and avoiding regressions.
Check the `r_wrapper/tests/` directory for explicitly supported packages.

Run tests as follows:
```bash
$ pytest r_wrapper/
```
