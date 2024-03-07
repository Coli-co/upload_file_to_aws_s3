from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import JSONResponse
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()


def upload_file_to_s3(file_data, bucket, object_name=None, content_type=None):
    """Upload a file to an S3 bucket
    :param file_data: Binary file data
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If you want to upload file to specific folder, assign here.
    :param content_type: upload file will be open in new page if this argument assigned,
     or upload file will de downloaded directly
    """

    # AWS S3 configuration
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("REGION_NAME"),
    )

    try:
        s3_client.put_object(Body=file_data, Bucket=bucket, Key=object_name, ContentType=content_type)
        # sets the ACL of the current version of an object.
        s3_client.put_object_acl(Bucket=bucket, Key=object_name, ACL='public-read')
    except ClientError as e:
        logging.error(e)
        return False
    return True


# API endpoint for image upload
@app.post("/upload")
async def upload_image_to_s3(
        upload_image: UploadFile = File(
            ..., description="The image uploaded to the rich menu, format: JPEG or PNG"
        ), file_name: str = Form(...),
):
    try:
        image_data = await upload_image.read()  # binary data
        content_type = upload_image.content_type
        folder_name = os.getenv("OBJECTS_NAME")

        upload_response = upload_file_to_s3(image_data, os.getenv("BUCKET_NAME"),
                                            f"{folder_name}/{file_name}",
                                            content_type)

        # # Upload the image to S3
        if upload_response is True:
            return JSONResponse(
                content={"message": "Image uploaded successfully"}, status_code=200
            )

         # upload image failed
        return JSONResponse(
            content={"message": "Error uploading image to S3"}, status_code=500
        )
    except Exception as e:
        print(f"Error uploading image to S3: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
