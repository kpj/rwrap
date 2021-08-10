import pandas as pd

from r_wrapper import base, stats, DESeq2


# read data
df_cts = pd.read_csv('count_data.csv', index_col=0)
df_coldata = pd.read_csv('col_data.csv', index_col=0)

# do DEA
dds = DESeq2.DESeqDataSetFromMatrix(
    countData=df_cts,
    colData=df_coldata,
    design=stats.as_formula('~ condition'))

dds = DESeq2.DESeq(dds)

res = DESeq2.results(dds)

# save result
df_res = base.as_data_frame(res)

(df_res.reset_index()
       .rename(columns={'index': 'gene'})
       .to_csv('result.csv', index=False))
