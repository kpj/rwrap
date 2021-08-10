library("DESeq2")


df_cts <- read.csv("count_data.csv", row.names = 1)
df_coldata <- read.csv("col_data.csv", row.names = 1)

dds <- DESeqDataSetFromMatrix(
    countData = df_cts,
    colData = df_coldata,
    design = ~ condition
)

dds <- DESeq(dds)
res <- results(dds)

df_res <- as.data.frame(res)
df_res$gene <- rownames(df_res)
write.table(df_res, "result.csv", quote = FALSE, sep = ",", row.names = FALSE)
