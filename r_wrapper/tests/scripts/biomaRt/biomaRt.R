library(biomaRt)


snp_list <- c("rs7329174", "rs4948523", "rs479445")

ensembl <- biomaRt::useMart("ENSEMBL_MART_SNP", dataset="hsapiens_snp")
df <- biomaRt::getBM(
    attributes=c("refsnp_id", "chr_name", "chrom_start", "consequence_type_tv"),
    filters="snp_filter", values=snp_list, mart=ensembl)

write.csv(df, "result.csv", quote=FALSE)
