import io
import json
import boto3
from datetime import datetime


def handler(event, context):
    try:
        # get AWS Secrets Manager
        secret_name = "AWS_LambdaKeys"
        region_name = "eu-north-1"
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        # call secrets
        get_secrets = client.get_secret_value(SecretId=secret_name)
        secrets = get_secrets["SecretString"]
        secrets_json = json.loads(secrets)

        AWS_ACCESS_KEY_ID = secrets_json["Access_key_ID"]
        AWS_SECRET_ACCESS_KEY = secrets_json["Secret_Access_key"]

        # add runtime date to Bulk and MailBag files
        today = datetime.now()
        today = today.strftime("%d-%m-%YT%H:%M")

        bucket_name = "bolt-projects"
        input_files = [
            "purchasing-orders/zip-archive/BulkPO.zip",
            "purchasing-orders/zip-archive/MailBag.csv",
            "purchasing-orders/input/cadentar.xlsx",
            "purchasing-orders/input/emails.xlsx",
            "purchasing-orders/input/MapareFurnizori_Cadentar_WMS.xlsx",
        ]

        files = [
            [
                file,
                file.split(".")[0].replace("input", "zip-archive")
                + f"({today})."
                + file.split(".")[1],
            ]
            for file in input_files
        ]

        s3c = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

        # Change files names,save the files to archive
        for file in files:
            try:
                obj = s3c.get_object(Bucket=bucket_name, Key=file[0])
                body = io.BytesIO(obj["Body"].read())
            except:
                continue
            s3c.put_object(
                Body=body.getvalue(),
                Bucket=bucket_name,
                Key=file[1],
            )
            s3c.delete_object(Bucket=bucket_name, Key=file[0])

        # no error info
        error = False
        error_message = None

    # error info
    except Exception as e:
        error = True
        error_message = str(e)

    return {
        "function_name": "Bolt-PO-CleanUp",
        "error": error,
        "error_message": error_message
    }


