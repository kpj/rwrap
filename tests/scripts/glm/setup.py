import numpy as np
import pandas as pd


def main(fname_out="data.csv"):
    np.random.seed(1)

    n = 100  # observation count
    p = 3  # covariate count
    q = 1  # response count

    X = np.random.normal(size=(n, p))
    B = np.random.normal(size=(p, q))
    Y = X @ B + np.random.normal(scale=0.1, size=(n, q))

    df = pd.DataFrame(np.c_[X, Y], columns=[f"X{i}" for i in range(p)] + ["Y"])
    df.to_csv(fname_out, index=False)


if __name__ == "__main__":
    main()
