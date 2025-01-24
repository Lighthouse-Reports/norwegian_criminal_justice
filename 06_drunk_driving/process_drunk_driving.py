import pandas as pd 
import os 
import pickle

os.chdir("/Users/gsgeiger/norwegian_lay_judges/scratchpad/drunk_driving/")


def load_data() -> pd.DataFrame : 
    with open("preprocessed_data/df_with_bpa.pickle","rb") as f : 
        df = pickle.load(f)
    
    print(f"Dataframe loaded with shape: {df.shape}")

    return df

def drop_univariate_columns(df) -> pd.DataFrame : 
    
    length_before = len(df.columns)
    df = df.loc[:, df.nunique() > 1]
    print(f"{length_before - len(df.columns)} columns dropped because they only had one value.")

    return df 

def has_uncommon_convictions(row : pd.Series, valid_columns : list) -> bool : 
    convicted_columns = row.filter(like='convicted')
    convicted_columns_filtered = convicted_columns[~convicted_columns.index.isin(valid_columns)]

    if convicted_columns_filtered.sum() > 0 : 
        return True
    
    return False 

def drop_cases_with_additional_charges(df, threshold=40) -> pd.DataFrame : 
    length_before = len(df)

    # Get the total sum of convictions for each chapter 
    convicted_sums = df.filter(like='convicted_').sum()

    # Filter so we only have chapters with a conviction count of over 40
    convicted_sums_filtered = convicted_sums[convicted_sums >= threshold]
    valid_columns = convicted_sums_filtered.index

    # Check if a case has uncommon convictions and drop any that do 
    df['has_uncommon_convictions'] = df.apply(has_uncommon_convictions, axis=1, args=(valid_columns,))
    df = df[df['has_uncommon_convictions'] == False]

    print(f"{length_before - len(df)} cases dropped because of uncommon convictions")
    print(f"New shape {df.shape}")

    return df

def drop_cases_with_rare_circumstances(df) : 
        
    for col in df.filter(like='group1_').sum().index : 
        if df[col].sum() < 10 : 
            df.drop(columns=[col],inplace=True)

    return df

def group_bpa(bpa) -> str : 

    if 0.20 <= bpa <= 0.49 : 
        return "Low"
    
    elif bpa <= 1.19 :
        return "Medium"
    
    else : 
        return "High"
    
def find_drugs(df) -> pd.DataFrame :
    drugs_list = ["alprazolam","amfetamin", "thc", "ghb",
                  "diazepam", "valium",
                  "mdma",  "kokain", "oxandrolone", "testosterone", "oxycodone"]
    
    for drug in drugs_list:

        drug_column_name = f'drug_found_{drug}'
        # Create a new column where a match is marked as 1, else 0
        df[drug_column_name] = df['dom_tekst'].str.contains(drug, case=False, na=False).astype(int)

        if df[drug_column_name].sum() < 10 : 
            df.drop(columns=[drug_column_name],inplace=True)
            continue 
    
    return df 

def get_suggested_sentence(bpa_group : str) -> range : 
    if bpa_group == "Low" : 
        return range(0,0)
    
    elif bpa_group == "Medium" : 
        return range(0,0)
    
    else : 
        return range(14,31)
    
def process_conditional_sentences(row : pd.Series) : 
    if row['punishment_conditional'] == 'true' : 
        return 0
    
    return row['punishment_prison_days']


def fix_bap(row : pd.Series) -> float : 
    
    if pd.isna(row['correct BAP']) : 
        return row['extracted_bpa']

    return row['correct BAP']
    
def correct_baps(df : pd.DataFrame) -> pd.DataFrame : 
    corrections = pd.read_excel('chat_gpt/bap_corrections.xlsx') 

    merged_df = pd.merge(df, corrections[['correct BAP','_id']], how='left', on='_id')

    merged_df['extracted_bpa'] = merged_df.apply(fix_bap, axis=1)

    return merged_df

def process_df(df) -> pd.DataFrame : 

    # Drop all columns with only 0s
    df = drop_univariate_columns(df)
    
    # Drop rows with other crimes 
    df = drop_cases_with_additional_charges(df)

    # Drop rows with rare aggravating or mitigating circumstances 
    df = drop_cases_with_rare_circumstances(df)

    # Drop all columns with only 0s
    df = drop_univariate_columns(df)

    # Correct BAPs
    df = correct_baps(df)

    # Group BPA and create dummy variables
    df['bpa_group'] = df['extracted_bpa'].apply(group_bpa)
    bpa_dummies = pd.get_dummies(df['bpa_group'], prefix='bpa').astype(int)
    df = pd.concat([df, bpa_dummies], axis=1)

    # Calculate suggested sentence and whether sentence should be conditional 
    df['suggested_sentence'] = df['bpa_group'].apply(get_suggested_sentence) 
    df['suggested_sentence_conditional'] = df['bpa_group'].apply(
        lambda bpa_group : 1 if bpa_group != "High" else 0
    )

    # Find specific drugs & get drug count for each case 
    df = find_drugs(df)
    drugs_list = df.filter(like='drug_found').columns
    df['drug_count'] = df[drugs_list].sum(axis=1)

    # Fix issues with conditional sentences 
    df['punishment_prison_days'] = df.apply(process_conditional_sentences,axis=1) 
    
    return df

def main() : 
    df = load_data()

    df = process_df(df)
    print("Final shape",df.shape)

    with open('processed_data/processed_drunk_driving.pickle','wb') as f : 
        pickle.dump(df, f)
        f.close()

if __name__ == "__main__" : 
    main()