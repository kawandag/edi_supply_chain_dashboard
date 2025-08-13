# AWS Simulation Quickstart

1) Deploy S3+Lambda using SAM:
```
cd aws_simulation
sam build && sam deploy --guided
```
2) Upload `.edi` files to the bucket (prefix `raw/` optional) — Lambda writes JSON to `processed/`.
3) Run Glue job with arguments: `s3://<bucket>/processed/` and `s3://<bucket>/analytics/`.
4) Load analytics CSVs to Redshift with `redshift_setup.sql` and visualize in QuickSight.
