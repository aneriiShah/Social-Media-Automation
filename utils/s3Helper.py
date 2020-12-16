import logging
import boto3
import os
import base64

from botocore.exceptions import ClientError
class S3Helper:
    @staticmethod
    def upload_file(f, bucket, object_name):
        """Upload a file to an S3 bucket
        :return: True if file was uploaded, else False
        """
        # Upload the file
        s3_client = boto3.client('s3')
        try:
            s3_client.put_object(
                Body=base64.b64decode(f),
                Bucket= bucket,
                Key=object_name,
                ACL='public-read'
           )
        except ClientError as e:
            logging.error(e)
            return False
        return True