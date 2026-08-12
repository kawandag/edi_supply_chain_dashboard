# SupplyScope

An interactive Streamlit dashboard for monitoring supplier financial health, payment behavior, portfolio exposure, and risk.

**Live dashboard:** [edisupplychaindashboard.streamlit.app](https://edisupplychaindashboard.streamlit.app/)

## Launch locally

```bash
cd supply_chain_streamlit_project
python -m pip install -r requirements.txt
streamlit run app.py
```

## Publish from GitHub

GitHub Pages cannot host Streamlit because Streamlit requires a running Python server. The simplest GitHub-based deployment is Streamlit Community Cloud:

1. Create a new GitHub repository and push this project to it.
2. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Select **Create app**, then choose your repository and branch.
4. Set **Main file path** to `app.py`.
5. Select **Deploy**.

No secrets or environment variables are required. Dependencies are installed automatically from the root `requirements.txt`.

## Project structure

```text
.
├── .streamlit/config.toml
├── app.py
├── requirements.txt
├── supply_chain_streamlit_project/
│   ├── .streamlit/config.toml
│   ├── data/invoices.csv
│   ├── app.py
│   └── requirements.txt
├── .github/workflows/quality.yml
└── build_streamlit_zip.py
```

## Data

Replace `supply_chain_streamlit_project/data/invoices.csv` with your own data using these columns:

- `supplier`
- `invoice_date`
- `due_date`
- `payment_date`
- `amount`
- `dso`

Dates should use an unambiguous format such as `YYYY-MM-DD`.
