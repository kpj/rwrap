import pandas as pd

from rwrap import stats


df = pd.read_csv("data.csv")
fit = stats.glm("Y ~ X0 + X1 + X2", family=stats.gaussian(), data=df)

glm_coef = stats.coef(fit)

(
    pd.DataFrame.from_dict(glm_coef, orient="index")
    .reset_index()
    .rename(columns={"index": "names", 0: "values"})
    .to_csv("result.csv", index=False)
)
