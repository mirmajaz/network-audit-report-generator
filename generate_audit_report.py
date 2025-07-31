import pandas as pd
import re


def map_severity(full_entry: str) -> str:
    # Try to isolate Reference block only
    reference_text = ""
    if "Reference:" in full_entry:
        reference_text = full_entry.split("Reference:")[-1]
    else:
        reference_text = full_entry  # fallback to entire entry

    reference_text = reference_text.upper()

    if "CAT|III" in reference_text:
        return "Medium"
    elif "CAT|II" in reference_text:
        return "High"
    elif "CAT|I" in reference_text:
        return "Critical"
    else:
        return "Low"


def map_control_standard(text):
    text = text.lower()
    if any(k in text for k in ["password", "authentication", "login", "mfa"]):
        return "Identification and Authentication"
    elif any(k in text for k in ["bgp", "route", "traffic", "packet", "encryption"]):
        return "System and Communications Protection"
    elif any(k in text for k in ["service", "interface", "auxiliary", "management"]):
        return "Configuration Management"
    else:
        return "Access Control"

def smarten_recommendation_enhanced(raw_solution: str) -> str:
    # Clean spacing
    raw_solution = re.sub(r'\s+', ' ', raw_solution).strip()

    # If it already starts with "It is recommended", don't touch it — just return cleaned version
    if raw_solution.lower().startswith("it is recommended"):
        return raw_solution

    # If the sentence ends mid-thought (like "as shown below"), still keep it — do not crop
    # Use raw sentence if it begins with configure/set/delete/etc.
    match = re.search(r'(Configure|Set|Delete|Disable|Deny|Enforce|Reject)[^.]+\.', raw_solution, re.IGNORECASE)
    if match:
        full_sentence = match.group(0).strip().rstrip('.')
        return f"It is recommended to {full_sentence[0].lower() + full_sentence[1:]}."

    # Fallback: use full cleaned original
    clean_fallback = raw_solution.strip().rstrip('.')
    return f"It is recommended to {clean_fallback[0].lower() + clean_fallback[1:]}."


def parse_entry(description, index):
    entry = description.replace('\n', ' ').strip()
    solution_split = entry.split("Solution:")
    before_solution = solution_split[0]
    after_solution = solution_split[1].split("See Also:")[0].strip() if len(solution_split) > 1 else ""

    # Observation
    obs_match = re.search(r'- (.*?)"?: \[FAILED\]', before_solution)
    if obs_match:
        control_text = obs_match.group(1).strip()
        if control_text.lower().startswith("the "):
            device = control_text[4:]
            observation = f"It was observed that the {device[0].lower() + device[1:]} was not configured to {device.split('must be configured to ')[-1]}."
        else:
            observation = f"It was observed that {control_text} was not properly configured."
    else:
        observation = "Observation not found."

    # Description (Impact)
    impact_text = before_solution.split(": [FAILED]")[-1].split("Solution")[0].strip().split('.')[0]
    description_impact = f"Without this configuration, {impact_text[0].lower() + impact_text[1:]}." if impact_text else "Impact not provided."

    # Recommendation
    recommendation = smarten_recommendation_enhanced(after_solution)

    # See Also
    ref_match = re.search(r'See Also:\s*(https?://\S+)', entry)
    see_also = ref_match.group(1) if ref_match else ""

    # Reference block for CAT| tags
    reference_section = entry.split("Reference:")[-1].strip() if "Reference:" in entry else ""
    reference = reference_section.split("Policy Value")[0].strip() if "Policy Value" in reference_section else reference_section

    print(f"Row {index+1} - Ref: {reference_section} → Severity: {map_severity(entry)}")

    return {
        "S. No.": index + 1,
        "Control Standard": map_control_standard(entry),
        "Configuration File": "SAMPLE ROUER CONFIG BHQ.txt",
        "Severity": map_severity(entry),
        "Observation": observation,
        "Description (Impact)": description_impact,
        "Recommendation (Solution)": recommendation,
        "Reference (See Also)": see_also
    }


def process_excel(input_file, output_file):
    df = pd.read_excel(input_file)
    results = []

    for i, row in df.iterrows():
        results.append(parse_entry(str(row["Description"]), i))

    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"✅ Report generated: {output_file}")


if __name__ == "__main__":
    #This line runs the report generation function by:

#📥 Reading the input file:
#It loads the Excel file named RawdataExcelFIleWithOnlyDescriptionColumn.xlsx from the data/ folder.
#This file must have only one column named "Description" that contains only failed configuration entries (i.e., audit entries that include : [FAILED]).

#🛠 Processing the raw data:
#It extracts key fields like severity, observation, impact, recommendation, etc., using parsing and logic rules defined in the script.

#📤 Generating an output Excel file:
#It saves the processed and formatted results into a file named Network_Audit_Report_Final.xlsx inside the output/ folder.
    process_excel("data/RawdataExcelFIleWithOnlyDescriptionColumn.xlsx", "output/Network_Audit_Report_Final.xlsx")

