import argparse, os, boto3
s3 = boto3.client('s3')
def upload(indir, bucket):
    for fn in os.listdir(indir):
        if fn.endswith('.edi'):
            s3.upload_file(os.path.join(indir, fn), bucket, f'raw/{fn}')
            print('uploaded', fn)
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--indir', default='../sample_data')
    p.add_argument('--bucket', required=True)
    a = p.parse_args()
    upload(a.indir, a.bucket)
