from pathlib import Path
import os
from dotenv import load_dotenv
from google.cloud import storage, bigquery
import datetime as dt
import csv


## CONFIG
load_dotenv()

# gcs config
GCP_PROJECT_ID  = os.environ['GCP_PROJECT_ID']
GCS_BUCKET      = os.environ['GCS_BUCKET']
GCS_PREFIX      = os.environ['GCS_PREFIX']
BQ_LOCATION     = os.environ['BQ_LOCATION']
BQ_DATASET_RAW  = os.environ['BQ_DATASET_RAW']
BQ_TABLE        = os.environ['BQ_TABLE']

# data_path
PATH        = Path(os.environ['DATA_PATH'])
FILE_NAME   = os.environ['FILE_NAME']

csv_path    = PATH / BQ_DATASET_RAW / FILE_NAME

## FUNCTION DEFS
def gcs_upload(project_id, bucket_name, prefix, file):
    try:
        # Initialize target blob upload
        
        # Get current date
        cur_date        = str(dt.date.today())
        blob_name       = f"{prefix}/ingest_date={cur_date}/{file.name}"
        client          = storage.Client(project=project_id)
        bucket_client   = client.bucket(bucket_name=bucket_name)
        blob_client     = bucket_client.blob(blob_name=blob_name)

        # Upload File
        blob_client.upload_from_filename(file)
        print(f'Successfully uploaded {file.name} to gcs blob.')

        # Return gs path for bigquery load
        return f"gs://{bucket_name}/{blob_name}"
    
    except Exception as e:
        print(f'Error initializing client or uploading file {file.name}')
        print(f'Error: {e}')
        raise


def bigquery_load(project_id, blob_uri, target_dataset, target_table, location, local_file_path, sensitive=False):
    try:
        # construct ds path
        ds_name = f'{project_id}.{target_dataset}'

        # create dataset if not exists yet
        bq_client           = bigquery.Client(project=project_id, location=location)
        dataset             = bigquery.Dataset(ds_name)
        dataset.location    = location # location must match bucket

        dataset.labels = {
            'layer': 'raw', 
            'contains_pii': 'true'
            }

        bq_client.create_dataset(dataset=dataset, exists_ok=True)
        bq_client.update_dataset(dataset=dataset, fields=['labels'])

        # create schema for upload based on local file
        with open(local_file_path, encoding="utf-8", newline="") as f:
            schema_headers = next(csv.reader(f))
        
        schema          = [bigquery.SchemaField(c, 'STRING') for c in schema_headers]

        # config upload job
        job_config = bigquery.LoadJobConfig(
            source_format       = bigquery.SourceFormat.CSV,
            skip_leading_rows   = 1,
            schema              = schema,
            write_disposition   = bigquery.WriteDisposition.WRITE_TRUNCATE
        )

        # load the table to bq
        table   = f'{ds_name}.{target_table}'
        job     = bq_client.load_table_from_uri(
            blob_uri, 
            table, 
            job_config=job_config
            )
        job.result()

        # quick sanity check
        t = bq_client.get_table(table=table)

        # configure and set labels
        if sensitive:
            pii             = 'true'
            classification  = 'confidential'
        else:
            pii             = 'false'
            classification  = 'internal'

        t.labels = {
            'layer': 'raw', 
            'contains_pii': pii, 
            'source':local_file_path.name.replace('.','_').lower(),
            'data_classification':classification
            }
        bq_client.update_table(t, ['labels'])

        print(f'Print some metadata of table {table}')
        print(t.num_rows, [f.name for f in t.schema])
        
        if t.num_rows < 1:
            raise ValueError(f'Table {table} has 0 rows after load. Check source file {blob_uri}.')

    except Exception as e:
        print(f'Error loading the blob {blob_uri} to Big Query')
        print(f'Error: {e}')
        raise


if __name__ == "__main__":
    uri = gcs_upload(
        GCP_PROJECT_ID, 
        GCS_BUCKET, 
        GCS_PREFIX, 
        csv_path)
    print(f'Processing {uri} from gcs to bq...')

    bigquery_load(
        project_id      = GCP_PROJECT_ID,
        blob_uri        = uri,
        target_dataset  = BQ_DATASET_RAW,
        target_table    = BQ_TABLE,
        location        = BQ_LOCATION,
        local_file_path = csv_path,
        sensitive       = True
    )