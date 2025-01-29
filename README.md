# Norwegian Criminal Justice

This repository contains the pipeline we used to analyze more than 9000 district court verdicts in Norway. Here are the published stories that are based on this analysis
- [Story 1](https://www.nrk.no/1.17178868)
- [Story 2](https://www.nrk.no/1.17176807)
- In addition, we published a [methodology](https://www.lighthousereports.com/methodology/norway_criminal_justice/) that explains our research questions and design in more detail.

This project is a collaboration between NRK and Lighthouse Reports. The data collection was primarily carried out by NRK while the data analysis was led by Lighthouse Reports. The [results folder](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/03_results) contains the results from our analysis. 

We have decided to not make the underlying dataset publicly available because of its senstivity. If you are interested in reproducing our work or carrying out further research on this data, please reach out to justin-casimir 'at' lighthousereports.com.

# Pipeline Overview

## [TODO NRK] Data collection
- [parsing.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/parsing.py)
Description
- [avsagt_dato.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/avsagt_dato.py)
Description
- [constants.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/constants.py)
Description
- [db.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/db.py)
Description
- [dom_class.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/dom_class.py)
Description
- [dom_strenghetsgrad.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/dom_strenghetsgrad.py)
Description
- [dommere_og_parter.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/dommere_og_parter.py)
Description
- [domsslutning.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/domsslutning.py)
Description
- [log.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/log.py)
Description
- [type_avjorelse.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/NRK/parsing_verdicts/helpers/type_avgjorelse.py)
Description

## [Preprocessing](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/04_preprocessing)
- [process_json_data.ipynb](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/04_preprocessing/process_json_data.ipynb)
Converts JSON of verdict data into table format.
- [aggravating_mitigating_preprocessing.R](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/04_preprocessing/aggravating_mitigating_preprocessing.R)
Standardizes variables related to mitigating and aggravating circumstances.
- [preprocessing.R](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/04_preprocessing/preprocessing.R)
Operationalizes and cleans key variables for our analysis. Removes observations that contain rare convictions or rare mitigating aggravating circumstances. Produces table on the case level (df_short) and the case x judge level (df_long). The former only contains data on professional judges while the latter includes both professional and lay judges.

## [Analysis](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/05_notebooks)
Knitted notebooks in html format are available for download in the [Analysis](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/05_notebooks) folder.
- [exploratory_analysis.Rmd](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/05_notebooks/exploratory_analysis.Rmd)
Exploratory analysis of the verdict data. Includes descriptive and regression analysis of defendant and judge characteristics, interactions between the two, and analysis by crime type. Note that we did not use standard errors clustered at the judge_id level for this analysis. Configuration of independent, depenendent and control variables based on [02_config](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/02_config). Results are available in [exploratory](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/03_results/exploratory).
- [reportable_figures.Rmd](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/05_notebooks/reportable_figures.Rmd) Notebook to produce reliable numbers that are reported in our methodology and stories. Analyzes defendant characteristics, judge characteristics, interactions between gender and individual crimes, and several interaction effects between judge and defendant characteristics. Model specifications include: complete dataset and untransformed prison day outcome variable; dataset restricted to > 0 prison days and untransformed outcome variable; and dataset restricted to > 0 prison days and logged outcome variable. Standard errors are clustered on the judge id level. Configuration of independent and control variables based on [02_config](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/02_config). Results are available in [reportable_figures](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/03_results/reportable_figures).
- [robustness_checks.Rmd](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/05_notebooks/robustness_checks.Rmd) Robustness checks as recommended by our reviewers. Includes descriptive data tables, negative binomial regression models, VIF analysis, sensitivity analysis, and extensive robustness tests of the impact of judge age on sentence length. Configuration of independent and control variables based on [02_config](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/02_config). Results are available in [robustness_checks](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/03_results/robustness_checks).

## [Driving under the influence analysis](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/tree/main/06_drunk_driving)
We ran additional analysis of driving under the influence of drugs cases, where we noticed especially high disparities between low and high income defendants. This involved extracting additional, crime-specific variables from verdicts, such as a defendant's blood alcohol content and the type of drugs they had taken. 
- [extract_bpa.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/06_drunk_driving/extract_bpa.py) Script used to extract blood alcohol content form verdicts.
- [process_drunk_driving.py](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/06_drunk_driving/process_drunk_driving.py) Runs specific prepreoccessing steps on driving under the influence dataset.
- [analyze_drunk_driving.ipynb](https://github.com/Lighthouse-Reports/norwegian_criminal_justice/blob/main/06_drunk_driving/analyze_drunk_driving.ipynb) Main analysis script that runs  various regression models and conducts descriptive analysis 



