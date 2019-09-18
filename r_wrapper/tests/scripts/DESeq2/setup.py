import numpy as np
import pandas as pd


def main():
    np.random.seed(1)

    n = 10
    p = 4

    # generate data
    df_cts = pd.DataFrame(
        np.random.negative_binomial(100, .1, size=(n, p)),
        index=[f'g{i}' for i in range(n)],
        columns=[f'V{i}' for i in range(p)])

    df_coldata = pd.DataFrame({
        'condition': ['WT'] * (p // 2) + ['MT'] * (p // 2)
    }, index=df_cts.columns)

    # save data
    df_cts.to_csv('count_data.csv')
    df_coldata.to_csv('col_data.csv')


if __name__ == '__main__':
    main()
