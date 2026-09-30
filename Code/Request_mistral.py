import os
import pandas as pd
import json
import re
import time
from openai import OpenAI
from Prompts_mistral import mistral_unified_correction_prompt

api_key = os.environ.get("LLM_API_KEY", "sk-1aab6c1cae9d44468e4465e3ad8dced7")

if not api_key:
    raise ValueError("LLM_API_KEY missing")

client = OpenAI(
    api_key=api_key,
    base_url="https://llm.lab.groupe-genes.fr/ollama/v1",
    timeout=60.0
)

output_file = 'results_final_flattened.csv'

if os.path.exists(output_file):
    df = pd.read_csv(output_file)
else:
    df = pd.read_csv('results_geoeconomics_analysis_precise.csv')

df_transcripts = pd.read_csv('sp500_transcripts_history_full.csv')

new_cols = [
    'mistral_audit_response', 'summary', 'eval', 
    'tariffs_correction_made', 'tariffs_correction_explanation',
    'sanctions_correction_made', 'sanctions_correction_explanation',
    'exports_correction_made', 'exports_correction_explanation',
    'global_effect_any', 'tariffs_hs_chapter', 'tariffs_hs_heading', 
    'tariffs_hs_subheading', 'sanctions_hs_chapter', 'sanctions_hs_heading', 
    'sanctions_hs_subheading', 'exports_hs_chapter', 'exports_hs_heading', 
    'exports_hs_subheading'
]

for col in new_cols:
    if col not in df.columns:
        df[col] = pd.NA

for index, row in df.iterrows():
    company_name = row.get('company', f"Ligne {index}")
    year = row.get('year', 'N/A')
    quarter = row.get('quarter', 'N/A')
    
    if pd.notna(row.get('mistral_audit_response')) and str(row.get('mistral_audit_response')).strip() != "" and not str(row.get('mistral_audit_response')).startswith("ERREUR"):
        print(f"Ignoré (déjà traité) : Index {index} - {company_name} - {year} - {quarter}")
        continue
        
    print(f"Traitement en cours : Index {index} - {company_name} - {year} - {quarter}")
    
    match = df_transcripts[(df_transcripts['company'] == row['company']) & 
                           (df_transcripts['year'] == row['year']) & 
                           (df_transcripts['quarter'] == row['quarter'])]
    
    transcript_text = str(match['content'].iloc[0]) if not match.empty else ""
    
    initial_data = row.drop(labels=new_cols, errors='ignore').to_dict()
    initial_json_str = json.dumps(initial_data, ensure_ascii=False, indent=2)
    
    user_content = f"TRANSCRIPT:\n{transcript_text}\n\nINITIAL JSON:\n{initial_json_str}"
    
    success = False
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="mistral:latest",
                messages=[
                    {"role": "system", "content": mistral_unified_correction_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0
            )
            
            print(f"  -> Succès : API contactée (tentative {attempt + 1}).")
            
            result_text = response.choices[0].message.content
            df.loc[index, 'mistral_audit_response'] = result_text
            
            json_match = re.search(r'<JSON>(.*?)</JSON>', result_text, re.DOTALL)
            summary_match = re.search(r'<SUMMARY>(.*?)</SUMMARY>', result_text, re.DOTALL)
            eval_match = re.search(r'<EVAL>(.*?)</EVAL>', result_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1).strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                elif json_str.startswith("```"):
                    json_str = json_str[3:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                    
                json_str = json_str.strip()
                
                try:
                    parsed_json = json.loads(json_str)
                    for k, v in parsed_json.items():
                        if v == "NaN":
                            v = pd.NA
                        df.loc[index, k] = v
                except json.JSONDecodeError as e:
                    print(f"  -> ERREUR DE LECTURE JSON : {e}")
            
            if summary_match:
                df.loc[index, 'summary'] = summary_match.group(1).strip()
                
            if eval_match:
                df.loc[index, 'eval'] = eval_match.group(1).strip()
                
            success = True
            break
            
        except Exception as e:
            print(f"  -> Tentative {attempt + 1} échouée : {e}")
            time.sleep(3)
    
    if not success:
        print(f"  -> Échec définitif pour l'index {index}.")
        df.loc[index, 'mistral_audit_response'] = "ERREUR: Connection error after 3 attempts"
        
    df.to_csv(output_file, index=False, encoding='utf-8')

print("Traitement terminé.")