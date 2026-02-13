# Coating Performance Decision-Support Tool

A Python-based computational framework for evaluating coating robustness under real machining severity conditions.

This tool bridges:

- Experimental coating characterization (wear rate + adhesion)
- Real machining force signals (ORNL cutting dataset)

to generate a severity-dependent comparative risk ranking for substrate–coating systems.

---

## Engineering Objective

To provide a structured, reproducible method for evaluating coating vulnerability under varying mechanical load regimes, supporting coating selection decisions within industrial coating engineering workflows.

---

## Methodology

### 1. Coating Robustness Index (CRI)

Derived from experimental data:

- Wear rate (inverted & normalized)
- Adhesion strength (Lc2)

\[
CRI = 0.6 \cdot WRS + 0.4 \cdot AS
\]

Higher CRI → mechanically robust coating–substrate system.

---

### 2. Machining Severity Index (MSI)

Extracted from cutting force signals:

- RMS force magnitude
- Peak force
- Crest factor

\[
MSI = 0.7 \cdot F_{rms,norm} + 0.3 \cdot Crest_{norm}
\]

Higher MSI → more severe machining condition.

---

### 3. Risk Matrix

\[
Risk = \frac{MSI}{CRI}
\]

Used to simulate coating vulnerability under:

- Low (P25)
- Medium (P50)
- High (P75)

machining severity regimes.

---

## Outputs

- `coating_robustness_index.csv`
- `machining_severity_index.csv`
- `risk_matrix.csv`
- Risk heatmap visualization

---

## Repository Structure

# Coating Performance Decision-Support Tool

A Python-based computational framework for evaluating coating robustness under real machining severity conditions.

This tool bridges:

- Experimental coating characterization (wear rate + adhesion)
- Real machining force signals (ORNL cutting dataset)

to generate a severity-dependent comparative risk ranking for substrate–coating systems.

---

## Engineering Objective

To provide a structured, reproducible method for evaluating coating vulnerability under varying mechanical load regimes, supporting coating selection decisions within industrial coating engineering workflows.

---

## Methodology

### 1. Coating Robustness Index (CRI)

Derived from experimental data:

- Wear rate (inverted & normalized)
- Adhesion strength (Lc2)

\[
CRI = 0.6 \cdot WRS + 0.4 \cdot AS
\]

Higher CRI → mechanically robust coating–substrate system.

---

### 2. Machining Severity Index (MSI)

Extracted from cutting force signals:

- RMS force magnitude
- Peak force
- Crest factor

\[
MSI = 0.7 \cdot F_{rms,norm} + 0.3 \cdot Crest_{norm}
\]

Higher MSI → more severe machining condition.

---

### 3. Risk Matrix

\[
Risk = \frac{MSI}{CRI}
\]

Used to simulate coating vulnerability under:

- Low (P25)
- Medium (P50)
- High (P75)

machining severity regimes.

---

## Outputs

- `coating_robustness_index.csv`
- `machining_severity_index.csv`
- `risk_matrix.csv`
- Risk heatmap visualization

---

## Repository Structure

02_src/
compute_cri.py
compute_msi.py
compute_risk_matrix.py
07_outputs/
CSV results
plots/


Raw datasets are excluded from the repository.

---

## Technical Scope

This is a severity-normalized comparative risk framework.
It is not an absolute tool-life predictor or finite element wear simulator.

Designed for coating engineering evaluation and decision-support.

---

## Author

Neeraj Kulkarni  
M.Sc. Mechatronics & Robotics  
Coating Engineering Research

---

## Data (not included in this repo)

Raw datasets are not stored in this repository to keep it lightweight and GitHub-friendly.

### ORNL machining force dataset
Download from the official NIST portal:
https://data.nist.gov/od/id/mds2-3121

After downloading/extracting, place the cutting dataset here:

01_data/ornl_raw/Cutting data/...

### Thesis experimental dataset
Place the excel here:
01_data/thesis_raw/Complete Analysis .xlsx
**

Expected local structure:
01_data/
  ornl_raw/
    Cutting data/
    FTF data/
    Impact data/
    Configurations/
  thesis_raw/
    Complete Analysis .xlsx

### Sample data
For quick inspection without downloading raw datasets, see:
01_data_sample/



