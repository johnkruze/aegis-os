import os
import sys
import time
import logging
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%SZ',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("R2-UploadDaemon")

R2_BUCKET_NAME = "open-access-datasets"
WATCH_DIR = Path(os.environ.get(
    "WATCH_DIR",
    os.path.join(os.environ.get("SPECTRUM_ROOT", ""), "G^G", "genesis_core", "data", "corpus", "products")
))


def _get_r2_client():
    """Build a boto3 S3 client pointed at Cloudflare R2."""
    account_id = os.environ.get("CF_ACCOUNT_ID", "")
    access_key = os.environ.get("CF_R2_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("CF_R2_SECRET_ACCESS_KEY", "")

    if not all([account_id, access_key, secret_key]):
        raise RuntimeError(
            "CF_ACCOUNT_ID, CF_R2_ACCESS_KEY_ID, and CF_R2_SECRET_ACCESS_KEY "
            "must all be set in the environment."
        )

    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def check_bucket_exists(client) -> bool:
    try:
        client.head_bucket(Bucket=R2_BUCKET_NAME)
        return True
    except ClientError as e:
        code = e.response["Error"]["Code"]
        logger.error(f"Bucket check failed (code {code}): {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to check bucket: {e}")
        return False


def upload_and_purge(client, filepath: Path):
    object_key = filepath.name
    logger.info(f"Initiating Upload Pipeline: {filepath.name} -> r2://{R2_BUCKET_NAME}/{object_key}")

    start_time = time.time()
    try:
        client.upload_file(str(filepath), R2_BUCKET_NAME, object_key)

        duration = time.time() - start_time
        file_size_gb = filepath.stat().st_size / (1024 ** 3)
        logger.info(f"[SUCCESS] Uploaded {file_size_gb:.2f} GB to R2 in {duration:.1f}s.")

        # Purge local buffer once confirmed in R2
        logger.warning(f"Purging local buffer for {filepath.name}...")
        filepath.unlink()
        logger.info("Local storage reclaimed. Ready for next stream.")

    except NoCredentialsError:
        logger.error("R2 credentials missing or invalid. Check env vars.")
    except Exception as e:
        logger.error(f"Critical error during upload pipeline: {e}")


def daemon_loop():
    logger.info("====================================")
    logger.info(" Sovereign Pipeline: INFINITE HORIZON ")
    logger.info("====================================")

    try:
        client = _get_r2_client()
    except RuntimeError as e:
        logger.error(str(e))
        return

    if not check_bucket_exists(client):
        logger.error(f"Bucket r2://{R2_BUCKET_NAME} does not exist or lacks permissions. Aborting.")
        return

    logger.info(f"Monitoring Directory: {WATCH_DIR}")
    logger.info(f"Target: r2://{R2_BUCKET_NAME}/")

    WATCH_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            for file in WATCH_DIR.glob("*.json"):
                # 60 seconds of silence = Rust chunk is finalized
                file_age = time.time() - file.stat().st_mtime
                if file_age > 60:
                    logger.info(f"Detected finalized telemetry chunk: {file.name}")
                    upload_and_purge(client, file)

            time.sleep(15)
        except KeyboardInterrupt:
            logger.info("Upload Daemon terminating...")
            break
        except Exception as e:
            logger.error(f"Daemon Loop Error: {e}")
            time.sleep(30)


if __name__ == "__main__":
    daemon_loop()
