import boto3
from botocore.exceptions import ClientError
import os
import logging
from typing import Optional
import mimetypes


class S3FileHandler:
    """A class to handle file operations with an S3 bucket."""

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str):
        """
        Initialize the S3FileHandler with AWS credentials.

        Args:
            aws_access_key_id (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
            region_name (str): AWS region name.
        """
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.logger = logging.getLogger(__name__)

    def _get_s3_path(self, bucket_folder_dir: str, object_key: str) -> str:
        """
        Construct the full S3 path.

        Args:
            bucket_folder_dir (str): The directory in the S3 bucket.
            object_key (str): The key of the object in the S3 bucket.

        Returns:
            str: The full S3 path.
        """
        return f"{bucket_folder_dir.rstrip('/')}/{object_key.lstrip('/')}"

    def fetch_file(
        self,
        bucket_name: str,
        bucket_folder_dir: str,
        object_key: str,
        output_path: str
    ) -> Optional[str]:
        """
        Fetch a file from an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            bucket_folder_dir (str): The directory in the S3 bucket where the file is located.
            object_key (str): The key of the object in the S3 bucket.
            output_path (str): The path to save the file.

        Returns:
            Optional[str]: The path to the downloaded file if successful, None otherwise.
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            s3_path = self._get_s3_path(bucket_folder_dir, object_key)
            self.s3_client.download_file(bucket_name, s3_path, output_path)
            self.logger.info(f"Successfully downloaded file to {output_path}")
            return output_path
        except ClientError as e:
            self.logger.error(f"An error occurred while downloading: {e}")
            return None

    def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        bucket_folder_dir: str,
        object_key: str,
        overwrite: bool = True
    ) -> bool:
        """
        Upload a file to an S3 bucket.

        Args:
            file_path (str): The path to the file to upload.
            bucket_name (str): The name of the S3 bucket.
            bucket_folder_dir (str): The directory in the S3 bucket where the file will be uploaded.
            object_key (str): The key of the object in the S3 bucket.
            overwrite (bool): Whether to overwrite the file if it already exists. Default is True.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False

            s3_path = self._get_s3_path(bucket_folder_dir, object_key)

            # Check if the file already exists
            if not overwrite:
                try:
                    self.s3_client.head_object(Bucket=bucket_name, Key=s3_path)
                    self.logger.warning(f"File already exists: s3://{bucket_name}/{s3_path}")
                    return False
                except ClientError as e:
                    if e.response['Error']['Code'] != '404':
                        raise

            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'

            self.s3_client.upload_file(
                file_path,
                bucket_name,
                s3_path,
                ExtraArgs={'ContentType': content_type}
            )
            self.logger.info(f"Successfully uploaded {file_path} to s3://{bucket_name}/{s3_path}")
            return True
        except ClientError as e:
            self.logger.error(f"An error occurred while uploading: {e}")
            return False

    def get_file_lists(self, bucket_name: str, bucket_folder_dir: str, file_extension: str = '') -> list:
        """
        List all files with a specific extension in a S3 bucket directory.

        Args:
            bucket_name (str): The name of the S3 bucket.
            bucket_folder_dir (str): The directory in the S3 bucket to list files from.
            file_extension (str): The file extension to filter (e.g., '.html', '.pdf'). Default is empty string (all files).

        Returns:
            list: A list of file names in the specified directory.
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=bucket_folder_dir
            )
            files = [obj['Key'] for obj in response.get('Contents', [])
                     if obj['Key'].lower().endswith(file_extension.lower())]
            self.logger.info(f"Found {len(files)} files with extension '{file_extension}' in s3://{bucket_name}/{bucket_folder_dir}")
            files = [os.path.basename(file) for file in files]
            files.remove('')
            return files
        except ClientError as e:
            self.logger.error(f"An error occurred while listing files: {e}")
            return []