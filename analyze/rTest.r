library(ggplot2)
library(ordinal)
library(performance)

# show file names in current dir
list.files()

# import data
party_df_non_abs <- read.csv("analyze/party_df_non_abs.csv")

# inspect data
str(party_df_non_abs)
summary(party_df_non_abs)


# make answer an ordered factor
party_df_non_abs$answer <- factor(party_df_non_abs$answer, ordered = TRUE)
party_df_non_abs$version <- factor(party_df_non_abs$version, ordered = FALSE)

# make time a continuous variable (its currently saved as T0, T4 ... and should be 0,4 ...)
party_df_non_abs$time <- as.numeric(gsub("T", "", party_df_non_abs$time))


# Fit the model
clmm_model <- clmm(answer ~ time + party * question_index + version * question_index + (1 | repetition) + (1 | debate_with), data = party_df_non_abs)


# Summary of the model
summary(clmm_model)


# reduced without version
clmm_no_version <- clmm(answer ~ time + party * question_index + (1 | repetition) + (1 | debate_with), data = party_df_non_abs)
clmm_no_party <- clmm(answer ~ time + question_index + (1 | repetition) + (1 | debate_with), data = party_df_non_abs)
clmm_no_time <- clmm(answer ~ party * question_index + (1 | repetition) + (1 | debate_with), data = party_df_non_abs)
clmm_no_question <- clmm(answer ~ time + party + version + (1 | repetition) + (1 | debate_with), data = party_df_non_abs)


# calculate Likelihood Ratio Test to check if the full model is significantly better than the reduced model
anova(clmm_no_version, clmm_model)

# --- Calculate Pseudo R-squared for effect size ---

variance_version_explained <- r2(clmm_model)$R2_marginal - r2(clmm_no_version)$R2_marginal
variance_party_explained <- r2(clmm_model)$R2_marginal - r2(clmm_no_party)$R2_marginal
variance_time_explained <- r2(clmm_model)$R2_marginal - r2(clmm_no_time)$R2_marginal
variance_question_explained <- r2(clmm_model)$R2_marginal - r2(clmm_no_question)$R2_marginal

variance_version_explained
variance_party_explained
variance_time_explained
variance_question_explained

variance_party_explained + variance_question_explained + variance_time_explained + variance_version_explained
