import pandas as pd

from r_wrapper import stats


df = pd.read_csv('data.csv')
fit = stats.glm('Y ~ X0 + X1 + X2', family=stats.gaussian(), data=df)

glm_coef = stats.coef(fit)

(glm_coef.reset_index()
         .rename(columns={'index': 'names', 0: 'values'})
         .to_csv('result.csv', index=False))
