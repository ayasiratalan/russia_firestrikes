
library(tidymodels)
library(stringr)
missiles <- read.csv("/Users/ayasiratalan/Desktop/ACADEMIA/Ukraine_Russia/Russian_Missile_Attacks/missile_attacks_daily_feb7.csv")

missiles <- missiles %>%
  mutate(Date = as.Date(time_end))

missiles$not_reach_goal[is.na(missiles$not_reach_goal)] <- 0


missiles$destroyed_2<- missiles$destroyed+missiles$not_reach_goal

missiles_daily_model <- missiles %>%
  group_by(Date, model) %>%
  summarize(
    launched = sum(launched, na.rm = TRUE),
    destroyed = sum(destroyed_2, na.rm = TRUE),
    .groups = 'drop'
  ) %>%
  mutate(
    model_detail = paste(model, ": Launched ", launched, ", Destroyed ", destroyed)
  )

missiles_daily_totals <- missiles_daily_model %>%
  group_by(Date) %>%
  summarize(
    total_launched = sum(launched, na.rm = TRUE),
    total_destroyed = sum(destroyed, na.rm = TRUE),
    model_details = paste(model_detail, collapse = "; "),
    .groups = 'drop'
  )

missiles_daily <- missiles_daily_totals

#write data
write.csv(missiles_daily, "/Users/ayasiratalan/Desktop/ACADEMIA/Ukraine_Russia/Russian_Missile_Attacks/deploy_python_Feb_7/missiles_daily.csv", row.names = FALSE)




dat_expanded_preprocessed <- missiles_daily %>%
  unnest(model_details) %>%
  separate_rows(model_details, sep = "; ") %>%
  mutate(
    Model = str_extract(model_details, "^[^:]+"),
    Launched = as.integer(str_match(model_details, "Launched\\s*(\\d+)")[,2]),
    Destroyed = as.integer(str_match(model_details, "Destroyed\\s*(\\d+)")[,2])
  ) %>%
  select(Date, Model, Launched, Destroyed)
#write csv
write.csv(dat_expanded_preprocessed, "/Users/ayasiratalan/Desktop/ACADEMIA/Ukraine_Russia/Russian_Missile_Attacks/deploy_python_Feb_7/dat_expanded_preprocessed.csv", row.names = FALSE)



