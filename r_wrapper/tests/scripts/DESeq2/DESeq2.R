library("DESeq2")


df.cts <- read.csv("count_data.csv", row.names=1)
df.coldata <- read.csv("col_data.csv", row.names=1)

dds <- DESeqDataSetFromMatrix(
    countData = df.cts,
    colData=df.coldata,
    design = ~ condition)

dds <- DESeq(dds)
res <- results(dds)

df.res <- as.data.frame(res)
df.res$gene <- rownames(df.res)
write.table(df.res, "result.csv", quote=FALSE, sep=",", row.names=FALSE)
