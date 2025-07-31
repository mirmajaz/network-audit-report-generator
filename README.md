# 🛡 Network Audit Report Generator (Excel/CSV)

A Python-based tool to transform raw failed network configuration findings into a structured, professional Excel audit report.

---

## ✅ Features

- Converts raw failed audit entries into structured fields:
  - Observation  
  - Impact  
  - Recommendation  
  - Severity  
- Parses CVSS/Control tags like `CAT|I`, `CAT|II`, etc.
- Smart shortening of long recommendations
- Auto-identifies control standard (access control, password, route, etc.)
- Supports `.xlsx` and `.csv` input
- Clean, Excel-formatted output report

---

## 📥 Input Format

- File: `data/Rawdatafortg.xlsx` or `.csv`
- Must have **only 1 column named `Description`**
- Each cell should contain **only failed findings**, such as:

The Juniper router must be configured to ... : [FAILED] ... Solution: ... See Also: ... Reference: CAT|II ...

yaml
Copy
Edit

📌 Copy only `FAILED` entries (ignore passed ones).

---

## 🚀 How to Run

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
Step 2: Paste Input File
Put your file into /data/Rawdatafortg.xlsx.

Step 3: Run Script
bash
Copy
Edit
python generate_audit_report.py
Step 4: Check Output
Your result will be in:

lua
Copy
Edit
output/Network_Audit_Report_Final.xlsx
📊 Output Fields
| S. No. | Control Standard | Configuration File | Severity | Observation | Description (Impact) | Recommendation (Solution) | Reference (See Also) |