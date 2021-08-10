df <- read.csv("data.csv")
fit <- glm("Y ~ X0 + X1 + X2", family = gaussian(), data = df)

glm_coef <- coef(fit)

write.table(
    data.frame(
        names = names(glm_coef),
        values = glm_coef
    ),
    "result.csv",
    quote = FALSE, sep = ",", row.names = FALSE
)
