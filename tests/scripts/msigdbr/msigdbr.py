from rwrap import msigdbr


df = msigdbr.msigdbr(species="Homo sapiens", category=["C2"])
df.to_csv("result.csv")
