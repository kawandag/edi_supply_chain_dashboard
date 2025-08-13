# Supply Chain Financial Health & Risk Analytics Dashboard (Streamlit + AWS Simulation)

This repo hosts a **Streamlit app** that parses mock **EDI 810 (Invoices)** and **EDI 820 (Payments)**, computes **DSO**, flags **late payments**, and shows **supplier risk scores**. It also includes an **AWS simulation** folder with IaC and job scripts you can use later to stand up a real pipeline.

## Live Demo (Streamlit Cloud)
1. Push this folder to a **public GitHub repo**.
2. Go to https://share.streamlit.io (Streamlit Community Cloud) → New app → choose your repo & `app.py`.
3. The app will build using `requirements.txt` and run automatically.

## Local Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure
```
.
├── app.py                  # Streamlit dashboard
├── edi_generator.py        # Generates mock EDI 810/820 data
├── edi_parser.py           # Parses the mock EDI into DataFrames
├── requirements.txt
├── sample_data/            # Seed EDI files (auto-regenerated if missing)
├── aws_simulation/         # Infra & processing examples for AWS
│   ├── template.yaml       # SAM: S3 landing bucket + Lambda trigger
│   ├── lambda_ingest.py    # Lambda handler (parses pseudo-EDI → JSON)
│   ├── aws_glue_job.py     # Glue job (PySpark) to compute analytics
│   ├── redshift_setup.sql  # Redshift schema + COPY template
│   ├── quickstart.md       # How to deploy the AWS demo
│   └── simulate_upload.py  # Helper to upload .edi to S3
└── .streamlit/config.toml
```

## How It Maps to the 4 Phases
- **Phase 1 (Planning/Data)**: `edi_generator.py` creates mock 810/820 files.
- **Phase 2 (Cloud Ingestion)**: `aws_simulation/template.yaml` (S3+Lambda trigger).
- **Phase 3 (Processing/Analytics)**: `aws_simulation/aws_glue_job.py` (DSO, aggregates, risk).
- **Phase 4 (Visualization)**: `app.py` (Streamlit dashboard).

## Notes
- This is a demo using **simplified** EDI segments (BIG, N1, ITD; BPR, N1, RMR). For production, use a standards-compliant EDI parser and secure cloud storage with governance.
