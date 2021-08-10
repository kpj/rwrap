from r_wrapper import biomaRt


snp_list = ['rs7329174', 'rs4948523', 'rs479445']

ensembl = biomaRt.useMart('ENSEMBL_MART_SNP', dataset='hsapiens_snp')
df = biomaRt.getBM(
    attributes=['refsnp_id', 'chr_name', 'chrom_start', 'consequence_type_tv'],
    filters='snp_filter', values=snp_list, mart=ensembl)

df.to_csv('result.csv')
