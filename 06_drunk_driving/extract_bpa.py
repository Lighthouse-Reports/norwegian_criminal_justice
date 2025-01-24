import pandas as pd 
import pickle 
import os 
import re

os.chdir("/Users/gsgeiger/norwegian_lay_judges")

PATH_TO_DUI = os.getcwd() + "/scratchpad/drunk_driving/"

BENCHMARK = True 


def load_data() -> pd.DataFrame : 
    with open(PATH_TO_DUI + "data_pickle.pickle","rb") as f : 
        df = pickle.load(f)
    
    print(f"Data loaded with shape {df.shape}")

    return df

def load_verdict_json() -> pd.DataFrame : 
    verdict_df = pd.read_json(PATH_TO_DUI + "pulled_cases.json")

    return verdict_df

def filter_verdict_json(drunk_driving_case_list : list, verdict_df : pd.DataFrame) -> pd.DataFrame : 
    filtered_verdict_df = verdict_df[verdict_df['_id'].isin(drunk_driving_case_list)] 
    print(f"Shape of filtered verdict df {filtered_verdict_df.shape}")

    return filtered_verdict_df

def find_charges(text : str) -> str : 

    # This assumes sentences end with a period, exclamation mark, or question mark.
    # Regex pattern to capture everything under "Grunnlag:"
    pattern = r'Grunnlag:\s*(.*?)(?=\n\n|\Z)'

    # Find matches
    matches = re.findall(pattern, text, flags=re.DOTALL)

    if len(matches) == 0 : 
        raise Exception("No charges found.")
    
    return ''.join(matches)

def find_bap(charges : str) -> list : 

    # Regex to match sentences containing 'promille'
    # This assumes sentences end with a period, exclamation mark, or question mark.
    pattern = r'[^.!?]*\b(?:promille|alkoholpromille)\b[^.!?]*(?:[.!?](?!\d)|$)'

    # Find all matches
    matches = re.findall(pattern, charges, flags=re.IGNORECASE)
    
    return matches

def find_highest_bap(floats : list) : 

    floated_list = []
    for float_str in floats : 
        float_str_replaced_comma = float_str.replace(",",".")
        floated_list.append(float(float_str_replaced_comma))
    
    maximum_number = max(floated_list)

    # Remove any numbers larger than 4, because there are false positives
    while maximum_number >= 4.0 : 
        floated_list.remove(maximum_number)
        maximum_number = max(floated_list)
    
    return str(max(floated_list))

def parse_bap(bap_mention) : 

    # Clean out any mikromil floats from the mention 
    bap_mention = re.sub(r'\b\d+,\d+\b(?=\s+mikromol)', '', bap_mention)

    # Regex to find only floats
    floats = re.findall(r'\d+,\d+', bap_mention)

    # Norwegian words for greater than 
    greater_than_word = ["høyere", "over", "mer"]

    parsed_bap = "None"
    if len(floats) == 1 : 
        if ("tilsvarende" in bap_mention) and (any(word in bap_mention for word in greater_than_word)) : 
            parsed_bap = ">" + floats[0]

        elif "tilsvarende" in bap_mention : 
            parsed_bap = floats[0]

        elif any(word in bap_mention for word in greater_than_word) : 
            parsed_bap = ">" + floats[0]
        
        else : 
            parsed_bap = floats[0]
    
    if len(floats) > 1 : 
        if "mellom" in bap_mention : 
            parsed_bap = ">" + floats[0]
        
        elif "til og med" in bap_mention : 
            parsed_bap = ">" + floats[0]

        elif "alkoholpromille på" in bap_mention : 
            split_bap_mention = bap_mention.split("alkoholpromille på")[1]
            floats_after_split = re.findall(r'\d+,\d+', split_bap_mention)

            if len(floats_after_split) == 0 : 
                parsed_bap = find_highest_bap(floats)
            
            else : 
                parsed_bap = floats_after_split[0]
        
        elif "tilsvarende" in bap_mention : 
            split_bap_mention = bap_mention.split("tilsvarende",1)[1]
            floats_after_split = re.findall(r'\d+,\d+', split_bap_mention)
            
            if len(floats_after_split) == 0 : 
                parsed_bap = find_highest_bap(floats)
            
            else : 
                parsed_bap = floats_after_split[0]
        
        elif " svar " in bap_mention : 
            split_bap_mention = bap_mention.split(" svar ",1)[1]
            floats_after_split = re.findall(r'\d+,\d+', split_bap_mention)
            
            if len(floats_after_split) == 0 : 
                parsed_bap = find_highest_bap(floats)
            
            else : 
                parsed_bap = floats_after_split[0]
        
        else : 
            parsed_bap = find_highest_bap(floats)

    text_no_newlines = re.sub(r'\n+', ' ', bap_mention)
    text_no_extra_spaces = re.sub(r'\s+', ' ', text_no_newlines).strip()
    text_no_extra_spaces = text_no_extra_spaces.replace("\r","")

    if BENCHMARK : 
        with open(PATH_TO_DUI + "benchmark.csv", "a") as f : 
            f.write(text_no_extra_spaces + ";" + str(floats) + ";" + str(len(floats)) + ";" + parsed_bap + "\n")
    
    return parsed_bap


def extract_bap(row : pd.Series) -> str : 

    extracted_baps = []

    if row['bap_mentions_charges'] != [] : 

        for bap_mention in row['bap_mentions_charges'] : 
            parsed_bap = parse_bap(bap_mention)
            extracted_baps.append(parsed_bap)
    
    elif row['bap_mentions_all'] != [] : 
        for bap_mention in row['bap_mentions_all'] : 
            parsed_bap = parse_bap(bap_mention)
            extracted_baps.append(parsed_bap)
    
    else : 
        return None 
    
    float_list = []
    for bap in extracted_baps : 
        if bap == "None" : 
            continue 
        
        bap_formatted = bap.replace(",",".").replace(">","")
        bap_float = float(bap_formatted)
        float_list.append(bap_float)
    
    if len(float_list) == 0 : 
        return None

    return max(float_list)
        

def main() : 
    df = load_data() 

    # Filter DF 
    df = df[(df["convicted_acquisition_possession_and_use_of_drugs"] == 1) & 
            (df['convicted_general_violation_of_traffic_act_1'] == 1)]

    # Load verdict df
    verdict_df = load_verdict_json()

    # Filter for drunk driving cases
    verdict_df = filter_verdict_json(df['X_id'].to_list(), verdict_df)

    # Extract charges
    verdict_df['charges'] = verdict_df['dom_tekst'].apply(find_charges)

    # Extract lines about bap from charges
    verdict_df['bap_mentions_charges'] = verdict_df['charges'].apply(find_bap)

    # Filter for only verdicts where we didn't find a BAP 
    verdict_df['bap_mentions_all'] = verdict_df['dom_tekst'].apply(find_bap)

    # Create benchmarking file 
    if BENCHMARK : 
        with open(PATH_TO_DUI + "benchmark.csv","w") as f: 
            f.write("bap_mention;exctracted_floats;num_floats;parsed_bap\n")
            f.close()

    verdict_df['extracted_bpa'] = verdict_df.apply(extract_bap, axis=1)

    # Save benchmarking file as an Excel 
    csv = pd.read_csv(PATH_TO_DUI + "benchmark.csv", delimiter=";")
    csv.to_excel('benchmarking.xlsx',index=False)

    # Merge with dataframe
    verdict_df = pd.merge(verdict_df, df, how='left', left_on='_id', right_on='X_id')

    # Drop intermediate columns 
    verdict_df.drop(columns=['charges','bap_mentions_charges','bap_mentions_all'],inplace=True)

    # Save dataframe with extracted bpa 
    with open(PATH_TO_DUI + "preprocessed_data/df_with_bpa.pickle","wb") as f : 
        pickle.dump(verdict_df,f)
        f.close()


if __name__ == "__main__" : 
    main()