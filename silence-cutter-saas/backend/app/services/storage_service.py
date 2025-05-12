import logging
import os
import shutil
from typing import Optional, BinaryIO
import aiofiles
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger("silence-cutter")

# Initialize AWS S3 client if needed
s3_client = None
if settings.STORAGE_TYPE == "s3":
    try:
        s3_client = boto3.client('s3', region_name=settings.S3_REGION)
        logger.info("S3 client initialized")
    except Exception as e:
        logger.error(f"Error initializing S3 client: {str(e)}")

# Initialize GCS client if needed
gcs_client = None
if settings.STORAGE_TYPE == "gcs":
    try:
        # Google Cloud Storage setup would go here
        # from google.cloud import storage
        # gcs_client = storage.Client()
        logger.info("GCS client initialized")
    except Exception as e:
        logger.error(f"Error initializing GCS client: {str(e)}")

async def save_file_to_storage(file_path: str, destination_path: str) -> str:
    """
    Save a file to the configured storage (local, S3, GCS)
    Returns the path or key where the file was saved
    """
    if settings.STORAGE_TYPE == "local":
        return await save_file_locally(file_path, destination_path)
    elif settings.STORAGE_TYPE == "s3":
        return await save_file_to_s3(file_path, destination_path)
    elif settings.STORAGE_TYPE == "gcs":
        return await save_file_to_gcs(file_path, destination_path)
    else:
        logger.error(f"Unknown storage type: {settings.STORAGE_TYPE}")
        raise ValueError(f"Unknown storage type: {settings.STORAGE_TYPE}")

async def save_file_locally(file_path: str, destination_path: str) -> str:
    """Save file to local storage"""
    dest_full_path = os.path.join(settings.STATIC_FILES_DIR, destination_path)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)
    
    # Copy file to destination
    shutil.copy2(file_path, dest_full_path)
    logger.info(f"File saved locally to {dest_full_path}")
    
    return destination_path

async def save_file_to_s3(file_path: str, destination_path: str) -> str:
    """Upload file to S3"""
    if not s3_client:
        logger.error("S3 client not initialized")
        raise ValueError("S3 client not initialized")
    
    try:
        s3_client.upload_file(
            file_path, 
            settings.S3_BUCKET_NAME, 
            destination_path
        )
        logger.info(f"File uploaded to S3: {destination_path}")
        return destination_path
    except ClientError as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        raise

async def save_file_to_gcs(file_path: str, destination_path: str) -> str:
    """Upload file to Google Cloud Storage"""
    if not gcs_client:
        logger.error("GCS client not initialized")
        raise ValueError("GCS client not initialized")
    
    try:
        # GCS upload code would go here
        # bucket = gcs_client.bucket(settings.GCS_BUCKET_NAME)
        # blob = bucket.blob(destination_path)
        # blob.upload_from_filename(file_path)
        logger.info(f"File uploaded to GCS: {destination_path}")
        return destination_path
    except Exception as e:
        logger.error(f"Error uploading to GCS: {str(e)}")
        raise

async def get_file_url(file_path: str) -> Optional[str]:
    """
    Get a URL for accessing the file
    """
    if not file_path:
        return None
        
    if settings.STORAGE_TYPE == "local":
        # For local storage, return a relative URL
        return f"/static/{file_path}"
    elif settings.STORAGE_TYPE == "s3":
        # Generate S3 URL
        try:
            url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.S3_REGION}.amazonaws.com/{file_path}"
            return url
        except Exception as e:
            logger.error(f"Error generating S3 URL: {str(e)}")
            return None
    elif settings.STORAGE_TYPE == "gcs":
        # Generate GCS URL
        try:
            # GCS URL generation would go here
            # Example: f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{file_path}"
            return f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{file_path}"
        except Exception as e:
            logger.error(f"Error generating GCS URL: {str(e)}")
            return None
    else:
        logger.error(f"Unknown storage type: {settings.STORAGE_TYPE}")
        return None

async def delete_file(file_path: str) -> bool:
    """
    Delete a file from storage
    """
    if not file_path:
        return False
        
    try:
        if settings.STORAGE_TYPE == "local":
            full_path = os.path.join(settings.STATIC_FILES_DIR, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"File deleted locally: {full_path}")
                return True
            return False
        elif settings.STORAGE_TYPE == "s3":
            if not s3_client:
                logger.error("S3 client not initialized")
                return False
                
            s3_client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_path
            )
            logger.info(f"File deleted from S3: {file_path}")
            return True
        elif settings.STORAGE_TYPE == "gcs":
            if not gcs_client:
                logger.error("GCS client not initialized")
                return False
                
            # GCS delete code would go here
            # bucket = gcs_client.bucket(settings.GCS_BUCKET_NAME)
            # blob = bucket.blob(file_path)
            # blob.delete()
            logger.info(f"File deleted from GCS: {file_path}")
            return True
        else:
            logger.error(f"Unknown storage type: {settings.STORAGE_TYPE}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False 