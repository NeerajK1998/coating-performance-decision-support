## How to Run

### 1) Clone Repository

```bash
git clone https://github.com/NeerajK1998/coating-performance-decision-support.git
cd coating-performance-decision-support
```

### 2) Install Requirements

```bash
pip install -r requirements.txt
```

### 3) Add Required Local Datasets

Raw datasets are intentionally excluded from the repository.

After downloading, place them in the following structure:

```text
01_data/
  ornl_raw/
    Cutting data/
    FTF data/
    Impact data/
    Configurations/
  thesis_raw/
    Complete Analysis.xlsx
```

ORNL machining force dataset:

Download from:
https://data.nist.gov/od/id/mds2-3121

### 4) Execute Full Pipeline

```bash
python 02_src/compute_cri.py
python 02_src/compute_msi.py
python 02_src/compute_risk_matrix.py
```

### Generated Outputs

```
07_outputs/
  coating_robustness_index.csv
  machining_severity_index.csv
  risk_matrix.csv
  plots/
```

---

## Technical Scope

- Severity-normalized comparative risk framework
- Not a finite element wear simulator
- Not an absolute tool-life predictor
- Designed for coating engineering decision-support
