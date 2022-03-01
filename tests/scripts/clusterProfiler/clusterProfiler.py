from rwrap import clusterProfiler, base


genelist = [8318, 991, 9133, 890, 983, 4085, 7272, 1111, 891, 4174, 9232]

res = clusterProfiler.enrichKEGG(gene=genelist, organism="hsa", pvalueCutoff=0.05)
df = base.as_data_frame(res)

df.to_csv("result.csv")
