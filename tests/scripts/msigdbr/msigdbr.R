library(msigdbr)

df <- msigdbr::msigdbr(species = "Homo sapiens", category = c("C2"))
write.csv(df, "result.csv")
