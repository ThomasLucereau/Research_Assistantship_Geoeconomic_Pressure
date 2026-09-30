mistral_unified_correction_prompt = """
You are assisting me in verifying and correcting data extracted from financial analyst reports concerning three geoeconomic policies: Tariffs, Sanctions, and Export Controls. The user prompt will supply both the original analyst report (Transcript) and the initially extracted JSON (Initial JSON).

## CRITICAL AUDIT DIRECTIVE ##
Your task is to verify the Initial JSON against the Transcript. You must correct any hallucinations, omissions, or confusion between the three policies (e.g., confusing a tariff with a sanction).
CONSERVATIVE MODIFICATION RULE: If you have any doubt about whether a modification is justified by the exact wording of the transcript, DO NOT change the value. You must retain the original value from the Initial JSON. However, you must explicitly write a remark explaining your doubt, your choices, and your reasoning in the corresponding "correction_explanation" field.

## Response Instructions: Part 1 (Audit Analysis) ##
Write an audit analysis evaluating the accuracy of the Initial JSON based on the Transcript for all three policies (Tariffs, Sanctions, Export Controls). Enclose this between the tags <ANALYSIS> and </ANALYSIS>. Keep your analysis to 500 words or less. Detail where the initial extraction succeeded, where it failed, note any ambiguities, and explicitly identify any products, materials, or sectors mentioned to determine their corresponding Harmonized System (HS) codes.

## Response Instructions: Part 2 (Structured JSON Output) ##
Provide a fully corrected structured output in JSON format, enclosed between the tags <JSON> and </JSON>.
The JSON must contain all the original fields from the Initial JSON for Tariffs, Sanctions, and Export Controls, maintaining the exact same keys. 
In addition to the standard data fields, you must strictly output the following correction tracking and classification fields:
1. "tariffs_correction_made": 1 if you altered any tariff-related data from the Initial JSON, and 0 if no changes were made.
2. "tariffs_correction_explanation": A concise explanation of exactly which tariff fields were changed and why. If no changes were made but you had doubts regarding tariffs, explain your doubts and why you chose not to modify the data. Report "NaN" if there are no changes and no doubts.
3. "sanctions_correction_made": 1 if you altered any sanction-related data from the Initial JSON, and 0 if no changes were made.
4. "sanctions_correction_explanation": A concise explanation of exactly which sanction fields were changed and why. If no changes were made but you had doubts regarding sanctions, explain your doubts and why you chose not to modify the data. Report "NaN" if there are no changes and no doubts.
5. "exports_correction_made": 1 if you altered any export control-related data from the Initial JSON, and 0 if no changes were made.
6. "exports_correction_explanation": A concise explanation of exactly which export control fields were changed and why. If no changes were made but you had doubts regarding export controls, explain your doubts and why you chose not to modify the data. Report "NaN" if there are no changes and no doubts.
7. "global_effect_any": 1 if the report discusses any of the three policies (tariffs, sanctions, or export controls) at any point, and 0 otherwise.
8. "tariffs_hs_chapter": The 2-digit HS Chapter code for products affected by tariffs. Report "NaN" if unknown.
9. "tariffs_hs_heading": The 4-digit HS Heading code for products affected by tariffs. Report "NaN" if unknown.
10. "tariffs_hs_subheading": The 6-digit HS Subheading code for products affected by tariffs. Report "NaN" if unknown.
11. "sanctions_hs_chapter": The 2-digit HS Chapter code for products affected by sanctions. Report "NaN" if unknown.
12. "sanctions_hs_heading": The 4-digit HS Heading code for products affected by sanctions. Report "NaN" if unknown.
13. "sanctions_hs_subheading": The 6-digit HS Subheading code for products affected by sanctions. Report "NaN" if unknown.
14. "exports_hs_chapter": The 2-digit HS Chapter code for products affected by export controls. Report "NaN" if unknown.
15. "exports_hs_heading": The 4-digit HS Heading code for products affected by export controls. Report "NaN" if unknown.
16. "exports_hs_subheading": The 6-digit HS Subheading code for products affected by export controls. Report "NaN" if unknown.

## Response Instructions: Part 3 (Summary) ##
Write a single summary of 150 words or fewer that captures only how the firm is (or may be) affected by tariffs, sanctions, and export controls. Omit all unrelated content. If the firm is not affected by any of these, write "Not affected." Enclose this analysis between the tags <SUMMARY> and </SUMMARY>.

## Response Instructions: Part 4 (Evaluation) ##
The fourth part of your response should be an evaluation of how well the fully corrected JSON structured summary agrees with your audit analysis. Keep the evaluation to 100 words or less. This part of your response should be enclosed between the tags <EVAL> and </EVAL>.

## Important Definitions for Reference ##
- Tariffs: Taxes imposed by the importing country on imported foreign goods.
- Sanctions: Government-imposed restrictions on trade or financial transactions designed to coerce, punish, or deter targeted firms or governments.
- Export Controls: Restrictions imposed by the exporting country on which countries or foreign firms a company is allowed to sell their goods or services to.
"""