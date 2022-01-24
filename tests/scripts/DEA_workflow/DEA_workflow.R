library(DESeq2)
library(biomaRt)
library(tidyverse)


# read data (https://trace.ncbi.nlm.nih.gov/Traces/sra/?study=SRP009615)
df_counts <- read_tsv(
    "http://duffel.rail.bio/recount/v2/SRP009615/counts_gene.tsv.gz"
) %>%
    column_to_rownames("gene_id")
df_design <- data.frame(
    condition = c("1", "2", "1", "2", "3", "4", "3", "4", "5", "6", "5", "6")
)

# run differential gene expression analysis
dds <- DESeqDataSetFromMatrix(
    countData = df_counts,
    colData = df_design,
    design = ~ condition
)
dds <- DESeq(dds)

res <- results(dds, contrast = c("condition", "1", "2"))
df_res <- as.data.frame(res)

# annotate result
ensembl <- useEnsembl(biomart = "genes", dataset = "hsapiens_gene_ensembl")
df_anno <- getBM(
    attributes = c("ensembl_gene_id_version", "description", "gene_biotype"),
    filters = "ensembl_gene_id_version",
    values = rownames(df_res),
    mart = ensembl,
)

df_res <- df_res %>%
    rownames_to_column("ensembl_gene_id_version") %>%
    inner_join(df_anno, by = "ensembl_gene_id_version")

# save result
df_res <- df_res %>%
    rename(gene = ensembl_gene_id_version)

df_res %>%
    write_csv("result.csv")
