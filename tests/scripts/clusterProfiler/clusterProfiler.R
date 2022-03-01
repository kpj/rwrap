library(clusterProfiler)


genelist <- c(8318, 991, 9133, 890, 983, 4085, 7272, 1111, 891, 4174, 9232)

res <- enrichKEGG(gene = genelist, organism = "hsa", pvalueCutoff = 0.05)
df <- as.data.frame(res)

write.csv(df, "result.csv")
