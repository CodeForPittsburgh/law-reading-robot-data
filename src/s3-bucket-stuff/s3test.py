from dotenv import load_dotenv

import os
import boto3

load_dotenv()

client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_KEY"),
    # aws_session_token=SESSION_TOKEN
)


def write_text_to_s3(bucket_name, file_name, text_content):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=text_content)
        print(f"File '{file_name}' successfully uploaded to S3 bucket '{bucket_name}'.")
    except Exception as e:
        print(f"An error occurred while uploading the file to the S3 bucket: {e}")

if __name__ == "__main__":
    bucket_name = "your_bucket_name"
    file_name = "example.txt"
    text_content = "Hello, this is a sample text file."

    write_text_to_s3(bucket_name, file_name, text_content)