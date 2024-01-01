library(lme4) # for the analysis
library(tidyverse) # needed for data manipulation.
library(lmerTest)# to get p-value estimations that are not part of the standard lme4 packages

chicago_df <- read.csv('chicago_comple_df.csv')
chicago_df$period <- as.factor(chicago_df$period)
model_chicago <- lmer(formula = comples ~ diversity + num_venue + diversity:num_venue + density + diversity:density + postal_distances + diversity:postal_distances + (1|period), data=chicago_df )
summary(model_chicago)

nyc_df <- read.csv('nyc_comple_df.csv')
nyc_df$period <- as.factor(nyc_df$period)
model_nyc <- lmer(formula = comples ~ diversity + num_venue + diversity:num_venue + density + diversity:density + postal_distances + diversity:postal_distances + (1|period), data=nyc_df )
summary(model_nyc)

la_df <- read.csv('la_comple_df.csv')
la_df$period <- as.factor(la_df$period)
model_la <- lmer(formula = comples ~ diversity + num_venue + diversity:num_venue + density + diversity:density + postal_distances + diversity:postal_distances + (1|period), data=la_df )
summary(model_la)

whole_df <- read.csv('/bgfs/kpelechrinis/xil178/Documents/fcc/simulations/6_comple_df.csv')
whole_df$c_p <- as.factor(whole_df$c_p)
model_whole <- lmer(formula = comples ~ diversity + num_venue + diversity:num_venue + density + diversity:density + postal_distances + diversity:postal_distances + (1|c_p), data=whole_df )
summary(model_whole)

