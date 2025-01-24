#load libraries
library(ggplot2)
library(dplyr)
library(tidyr)
library(readxl)
library(openxlsx)
library(stringr)
library(rstudioapi)

#set working directory
setwd(paste0(dirname(rstudioapi::getActiveDocumentContext()$path), '/..'))

### Prep Max Prison Setence Data ###
#load penal code data (used to construct max prison time variables)
penal_code <- readxl::read_excel('02_config/penal_code_key.xlsx') %>%
  rowwise() %>%
  #construct variables we can merge with the main df
  mutate(section_convicted_var_name = paste('convicted', section_name, collapse = '_'),
         section_convicted_var_name = gsub(' ', '_', section_convicted_var_name),
         section_convicted_var_name = tolower(section_convicted_var_name),
         maximum_prison_sentence = maximum_prison_sentence * 365)
#get vector with all sections that can lead to fines 
sections_fine <- penal_code %>%
  filter(fine == TRUE)
#get vector with all sections that can lead to prison sentences
sections_prison <- penal_code %>%
  filter(prison == TRUE)
# load raw data
df_raw <- read.csv('01_preprocessed_data/hidden/preprocessed_data_mitigating_aggravating.csv')

# vector of countries; not currently used for anything
foreign_backgrounds <- c(
  "203 Algerie", "204 Angola", "216 Burundi", "239 Elfenbenskysten", "241 Eritrea",
  "246 Etiopia", "249 Egypt", "250 Djibouti", "256 Gambia", "260 Ghana",
  "270 Kamerun", "276 Kenya", "278 Kongo, Republikken", "279 Kongo, Den Demokratiske Republikken",
  "283 Liberia", "286 Libya", "303 Marokko", "313 Nigeria", "326 Zimbabwe",
  "329 Rwanda", "336 Senegal", "337 Den Sentralafrikanske Republikk", "346 Somalia", "356 Sudan",
  "359 Sør-Afrika", "369 Tanzania", "379 Tunisia", "386 Uganda", "389 Zambia",
  "404 Afghanistan", "407 Aserbajdsjan", "410 Bangladesh", "412 Bhutan", "420 Myanmar",
  "424 Sri Lanka", "426 De Forente Arabiske Emirater", "428 Filippinene", "436 Hongkong",
  "444 India", "448 Indonesia", "452 Irak", "456 Iran", "460 Israel",
  "480 Kasakhstan", "484 Kina", "492 Sør-Korea", "496 Kuwait", "508 Libanon",
  "512 Malaysia", "524 De Palestinske Territoriene", "528 Nepal", "534 Pakistan",
  "544 Saudi-Arabia", "550 Tadsjikistan", "564 Syria", "568 Thailand", "575 Vietnam",
  "578 Jemen", "616 Costa Rica", "620 Cuba", "624 Den Dominikanske Republikk",
  "632 Guatemala", "664 Nicaragua", "672 El Salvador", "705 Argentina", "715 Brasil",
  "725 Chile", "730 Colombia", "735 Ecuador", "760 Peru", "775 Venezuela", "143 Tyrkia"
)

### DERIVE DEFENDANT AND JUDGE VARIABLES ###
df_raw <- df_raw %>%
  #defendant characteristic
  dplyr::mutate(case_year = as.integer(stringr::str_extract(case_date, "\\d+")),
                defendant_age = case_year - defendant_birth_year,
                defendant_age = ifelse(defendant_age < 100, defendant_age, NA),
                defendant_age_groups = case_when(defendant_age < 40 ~ '< 40',
                                                 defendant_age >= 40 &  defendant_age < 55 ~ '40 - 55',
                                                 defendant_age >= 55 ~ '> 55',
                                                 .default = NA),
                defendant_is_woman = case_when(defendant_gender == 'K' ~ 1,
                                               defendant_gender == 'M' ~ 0,
                                               .default = NA),
                defendant_some_foreign_background = case_when(defendant_ethnic_background %in% c('a') ~ 0, 
                                                              defendant_ethnic_background %in% c('c', 'd') ~ 1, 
                                                              .default = NA),
                defendant_is_married = case_when(defendant_civil_status == 'Gift' ~ 1,
                                                 !is.na(defendant_civil_status) ~ 0,
                                                 .default = NA),
                defendant_log_net_income = log(defendant_net_income + 1), # add 1 because log(0) is undefined; also log(1) is 0 which is neat
                defendant_net_income_percentile =  rank(defendant_net_income)/length(defendant_net_income),
                defendant_net_income_quantile =  case_when(defendant_net_income_percentile < 0.25 ~ 1,
                                                           defendant_net_income_percentile >= 0.25 & defendant_net_income_percentile < 0.50 ~ 2,
                                                           defendant_net_income_percentile >= 0.50 & defendant_net_income_percentile < 0.75 ~ 3,
                                                           defendant_net_income_percentile >= 0.75 ~ 4,
                                                           .default = NA),
                case_is_not_oslo = case_when(case_district_court !=  'Oslo tingrett' ~ 1,
                                             .default = 0)
                ) %>%
  #outcomes
  dplyr::mutate(
    judgement_convicted_binary = ifelse(judgement_convicted, 1, 0),
    judgement_unanimous = case_when(is.na(judge_majority_or_minority) ~ 1,
                                    judge_majority_or_minority %in% c('Majority', 'Minority') ~ 0,
                                    .default = NA),
    #we set prison days to 0 if prison sentence was possible otherwise keep NA
    punishment_prison_days = case_when((is.na(punishment_prison_days) & judgement_convicted_binary == 1) ~ 0,
                                       .default = punishment_prison_days),
    #set up max_possible_sentence variable
    max_possible_sentence = NA,
    #similar to prison days: set variable to zero if fine was possible otherwise keep NA
    punishment_fine = case_when((is.na(punishment_fine) & rowSums(dplyr::select(., any_of(sections_fine$section_convicted_var_name))) > 0) ~ 0,
                                       .default = punishment_fine)
  )


# calculate max prison sentence (this is pretty convoluted but it works :))
#loop over rows
for(i in 1:nrow(df_raw)){
  #extract row
  cur_row_convictions <- df_raw[i,] %>%
    #keep only section variables
    dplyr::select(starts_with('convicted')) %>%
    #pivot to longer (each row is a conviction variable)
    pivot_longer(everything()) %>%
    #keep only conviction section defendants were actually convicted for
    filter(value == 1)
  
  
  max_sentence <- penal_code %>%
    #only keep penal code sections for which the current defendant was convicted and for which we have max prison time data
    filter(section_convicted_var_name %in% cur_row_convictions$name, !is.na(maximum_prison_sentence)) %>%
    ungroup() %>%
    #sum over max prison time of all sections the defendant was convicted for
    dplyr::summarize(max_prison_sentence = sum(maximum_prison_sentence, na.rm = T))
  
  #if defendant wasn't conicted for any section for which we have max sentence data, keep max_possible sentence as NA
  if(nrow(max_sentence) == 0) {
    df_raw[i,'max_possible_sentence'] <- NA
    next
  }
  #otherwise assign max prison time summed over all the defendant's convictions
  df_raw[i,'max_possible_sentence'] <- max_sentence$max_prison_sentence
  
}

#share of max prison sentence the defendant got
df_raw$punishment_share_max_prison_sentence <- df_raw$punishment_prison_days/df_raw$max_possible_sentence


### DROP RARE CONVICTIONS AND CIRCUMSTANCES ###
min_case_n <- 50 #CHECK: change if necessary
control_level <- 'group1' #CHECK: pick whether to control for minor (group2) or major (group1) level aggravating and mitigating circumstances

#function that recursively drops cases for which there less than 50 observations
drop_cases_recursively <- function(df, last_iter_row_n, control_level, min_case, counter){
  #count cases for sections and circs
  conviction_circs_counts <- df %>%
    dplyr::select(starts_with(c('convicted', control_level))) %>%
    colSums(na.rm = T)
  
  #convert counts to df
  conviction_circs_counts <- data.frame(col = names(conviction_circs_counts),
                                  count = conviction_circs_counts)
  #only keep sections/circs that will be dropped
  cols_to_drop <- conviction_circs_counts %>%
    dplyr::filter(count < min_case)
  
  #set up a variable that contains the row sum of the variable that need to be dropped
  df$count_drop <- df %>%
    dplyr::select(all_of(cols_to_drop$col)) %>%
    rowSums(na.rm = T)
  #only keep rows where this sum is 0, i.e., all cases that contain rare circs/sections are dropped
  df_result <- df %>%
    filter(count_drop == 0)
  
  #print the iteration we are in and how many cases are left
  print(paste0('Iteration: ', counter, ' Cases: ', nrow(df_result)))
  
  #good base case: no more cases were dropped from last iteration
  if(nrow(df_result) == last_iter_row_n){
    #save which circs/sections we are keeping for controls in the regression models
    circs_to_keep <- conviction_circs_counts %>%
      filter(count >= min_case & grepl(control_level, col))
    openxlsx::write.xlsx(circs_to_keep, '02_config/aggravating_mitigating_circs.xlsx')
    sections_to_keep <- conviction_circs_counts %>%
      filter(count >= min_case & grepl('convicted', col))
    openxlsx::write.xlsx(sections_to_keep, '02_config/sections.xlsx')
    #return the reduced data frame
    return(df_result)
  
  #bad base case: there are no rows left   
  } else if (nrow(df_result) == 0) {
    print('No rows left')
    
  #recursive case: the number of rows has been reduced and further reductions may be necessary because new sections
  #or circs might now be below the 50 case limit
  } else {
    return(drop_cases_recursively(df_result, nrow(df_result), control_level, min_case, counter + 1))
  }
}

#Drop cases recursively from the main DF
df_restricted <- drop_cases_recursively(df_raw, nrow(df_raw), control_level, min_case_n, 1)


### JUDGE VARIABLES AND LONG TABLE ###
#extract judge related variables
colnames_short <- names(df_restricted)
colnames_id <- colnames_short[!grepl('^lay_[[:digit:]]', colnames_short)]
colnames_judge <- colnames_short[grepl('^lay_[[:digit:]]|profess?ional_judge', colnames_short)]

#pivot df_restricted to longer (i.e. from case level to case x judge level)
df_long <- df_restricted %>%
  mutate_at(.vars = colnames_judge, as.character) %>%
  mutate(row = row_number()) %>%
  #first pivot "very long" each judge related variable gets its own row
  pivot_longer(cols = all_of(colnames_judge), names_to = 'judge_var', values_to = 'judge_val') %>%
  #extract which judge the variable applies to (professional, lay1, or lay2)
  mutate(judge_var = stringr::str_replace(judge_var, 'profesional', 'professional')) %>%
  tidyr::separate(judge_var, into = c('judge', 'judge_var'), sep = '(?<=lay_[[:digit:]]|professional_judge)_', remove = T) %>%
  mutate(judge_var = stringr::str_replace(judge_var, 'judge_id', '_id')) %>%
  #Now we that we have seperated the judge characteristic and the judge type, we can pivot wider on the judge characteristic
  pivot_wider(names_from = 'judge_var', values_from = 'judge_val', names_prefix = 'judge_') %>%
  dplyr::select(-row)

#derive judge variables
df_long <- df_long %>%
  dplyr::mutate(judge_birth_year = as.numeric(judge_birth_year),
                judge_net_income = as.numeric(judge_net_income),
                judge_net_worth = as.numeric(judge_net_worth),
                judge_calculated_tax = as.numeric(judge_calculated_tax)
  ) %>%
  #judge characteristic
  dplyr::mutate(judge_age = case_year - judge_birth_year,
                judge_age = ifelse(judge_age < 100, judge_age, NA),
                judge_age_groups = case_when(judge_age < 40 ~ '< 40',
                                                 judge_age >= 40 &  judge_age < 55 ~ '40 - 55',
                                                 judge_age >= 55 ~ '> 55',
                                                 .default = NA),
                judge_is_woman = case_when(judge_gender == 'K' ~ 1,
                                           judge_gender == 'M' ~ 0,
                                           .default = NA),
                judge_some_foreign_background = case_when(judge_ethnic_background %in% c('a') ~ 0, #changed to only a
                                                              judge_ethnic_background %in% c('c', 'd') ~ 1, #changed to only c
                                                              .default = NA),
                judge_is_married = case_when(judge_civil_status == 'Gift' ~ 1,
                                                 !is.na(judge_civil_status) ~ 0,
                                                 .default = NA),
                judge_log_net_income = log(judge_net_income + 1),
                judge_net_income_percentile =  rank(judge_net_income)/length(judge_net_income),
                judge_net_income_quantile =  case_when(judge_net_income_percentile < 0.25 ~ 1,
                                                           judge_net_income_percentile >= 0.25 & judge_net_income_percentile < 0.50 ~ 2,
                                                           judge_net_income_percentile >= 0.50 & judge_net_income_percentile < 0.75 ~ 3,
                                                           judge_net_income_percentile >= 0.75 ~ 4,
                                                           .default = NA),
                judge_is_politician_binary = case_when(judge_is_politician == 1 ~ 1,
                                                       .default = 0),
                #naming of parties was inconsistent, just meant to make the variable more consistent
                judge_party = case_when(judge_party_name %in% c('Arbeidarpartiet', 'Arbeiderpartiet') ~ 'Arbeiderpartiet',
                                        judge_party_name == 'Fremskrittspartiet' ~ 'Fremskrittspartiet',
                                        judge_party_name %in% c('Høyre', 'HØYRE') ~ 'Høyre',
                                        judge_party_name == 'Kristelig Folkeparti' ~ 'Kristelig',
                                        judge_party_name == 'Miljøpartiet De Grønne' ~ 'Grønne',
                                        judge_party_name == 'Rødt' ~ 'Rødt',
                                        judge_party_name %in% c('Senterpartiet', 'Senterpartiet og Tverrpolitisk liste') ~ 'Senterpartiet',
                                        judge_party_name == 'Sosialistisk Venstreparti' ~ 'Sosialistisk',
                                        judge_party_name == 'Venstre' ~ 'Venstre',
                                        !is.na(judge_party_name) ~ 'other party',
                                        is.na(judge_party_name) ~ 'no party',
                                        .default = NA
                                        ),
                is_professional_judge = case_when(judge %in% c('lay_1', 'lay_2') ~ 0,
                                                  judge == 'professional_judge' ~ 1,
                                                  .default = NA)
  ) 

#df_short restricted to professional judge
df_short <- df_long %>%
  filter(is_professional_judge == 1)
  

#save short (on case level, professional judges only)
openxlsx::write.xlsx(df_short, '01_preprocessed_data/hidden/full_short.xlsx', overwrite = T)
#save long (on case x judge level, includes both professional and lay judges)
write.xlsx(df_long, '01_preprocessed_data/hidden/full_long.xlsx', overwrite = T)