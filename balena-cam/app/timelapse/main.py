import datetime as dt
import io
import logging
import os
import subprocess

import boto3
import schedule

PHOTO_JPG_CMD = [
    "/usr/bin/raspistill",
    "--nopreview",
    "--timeout",
    "1",
    "-o",
    "-",
    "--rotation",
    "180",
    "--quality",
    "90",
]

S3_BUCKET = os.getenv("S3_BUCKET", "no_bucket")


def take_a_photo(cmd=PHOTO_JPG_CMD):
    logging.info("Taking a photo...")
    captured_at = dt.datetime.now(tz=dt.timezone.utc).replace(microsecond=0)
    return subprocess.run(cmd, stdout=subprocess.PIPE, check=True), captured_at


def upload_to_s3(data, captured_at, s3_bucket=S3_BUCKET):
    logging.info("Uploading to s3...")
    s3_key = captured_at.isoformat().replace("+00:00", "Z") + ".jpg"
    s3 = boto3.client("s3")
    s3.upload_fileobj(io.BytesIO(data), s3_bucket, s3_key)


def tick():
    now = dt.datetime.now()
    logging.info("Tick at %s", now)
    earliest = dt.time(5, 30)
    latest = dt.time(19, 0)
    if now.time() >= earliest and now.time() <= latest:
        result, when = take_a_photo()
        upload_to_s3(data=result.stdout, captured_at=when)
