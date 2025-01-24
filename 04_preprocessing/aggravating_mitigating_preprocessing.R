library(dplyr)
library(tidyr)
library(openxlsx)
library(stringr)
library(rlang)
library(rstudioapi)

setwd(paste0(dirname(rstudioapi::getActiveDocumentContext()$path), '/..'))

output_fp <- '03_results/preprocessing/'
dir.create(output_fp, showWarnings = F)

### STEP 1: extract all the mitigating/aggravating circumstances ###
#load data
df_raw <- readxl::read_excel('01_preprocessed_data/hidden/preprocessed_data.xlsx')

#extract all mitigating and aggravating circumstances and count instances
row_sums_aggravating_mitigating <- df_raw %>%
  dplyr::select(starts_with(c('aggravating_', 'mitigating_'))) %>%
  colSums() %>%
  as.data.frame() %>%
  rename(count = '.')

row_sums_aggravating_mitigating$rowname_norwegian <- rownames(row_sums_aggravating_mitigating)

row_sums_aggravating_mitigating <- row_sums_aggravating_mitigating %>%
  mutate(type = case_when(grepl('aggravating_', rowname_norwegian) ~ 'aggravating',
                          grepl('mitigating_', rowname_norwegian) ~ 'mitigating',
                          .default = NA),
         circ_norwegian = str_replace(rowname_norwegian, 'aggravating_|mitigating_', '')) %>%
  arrange(desc(count))

#save list of mitigating and aggravating circumstances
write.csv(row_sums_aggravating_mitigating, paste0(output_fp, 'unique_circs.csv'))

### STEP 2: upload row_sums_aggravating_mitigating and manually assign them to 'major' (group1) and 'minor' (group2) groups. ###
### Major groups roughly correspond to NO penal code sections 78-79 ###

#load translated version
#set up variable names for grouped circs
unique_circs_translated <- read.csv('02_config/unique_circs_translated_grouped.csv') %>%
  rename(circ_original = 'X') %>%
  unite(circ_group_1, c('type', 'group_1'), remove = F, sep = '_') %>%
  unite(circ_group_2, c('type', 'group_1', 'group_2'), remove = F, sep = '_')

#count group 1 and group 2 circs
group_1_counts <- unique_circs_translated %>%
  filter(group_1 != '') %>%
  group_by(circ_group_1) %>%
  summarise(n = n(),
            sum = sum(count, na.rm = T))
write.csv(group_1_counts, paste0(output_fp, 'counts_group1.csv'))
group_2_counts <- unique_circs_translated %>%
  filter(group_2 != '') %>%
  group_by(circ_group_2) %>%
  summarise(n = n(),
            sum = sum(count, na.rm = T))
write.csv(group_2_counts, paste0(output_fp, 'counts_group2.csv'))


# generate new group 1 variables
unique_circs_translated <- unique_circs_translated %>%
  filter(group_1 != '', group_1 != 'DELETE')

#data frame that includes group1 aggravating/mitigating circs
df_group1 <- df_raw

#consolidate mitt/aggravating circumstances into grouped variables
for(cur_group1 in unique(unique_circs_translated$circ_group_1)){
  print(cur_group1)
  
  #variable name of grouped circ
  varname_group1 <- paste0('group1_', cur_group1)
  
  #extract all old variable names associated with the group
  cur_circs <- unique_circs_translated %>%
    filter(circ_group_1 == cur_group1)
  
  #create new grouped variable that is 1 if any of the variables in the group is 1
  df_group1[[varname_group1]] <- df_group1 %>%
    dplyr::select(all_of(cur_circs$circ_original)) %>%
    do.call(pmax, .)
}

#data frame that includes all aggravating/mitigating circs
df_all_mit_agg <- df_group1

#process same as above
for(cur_group2 in unique(unique_circs_translated$circ_group_2)){
  print(cur_group2)
  
  #variable name of grouped circ
  varname_group2 <- paste0('group2_', cur_group2)
  
  #extract all old variable names associated with the group
  cur_circs <- unique_circs_translated %>%
    filter(circ_group_2 == cur_group2)
  
  #create new grouped variable that is 1 if any of the variables in the group is 1
  df_all_mit_agg[[varname_group2]] <- df_all_mit_agg %>%
    dplyr::select(all_of(cur_circs$circ_original)) %>%
    do.call(pmax, .)
}

#save dataframe with grouped agg/mit circs
write.csv(df_all_mit_agg, '01_preprocessed_data/hidden/preprocessed_data_mitigating_aggravating.csv', row.names = F)

