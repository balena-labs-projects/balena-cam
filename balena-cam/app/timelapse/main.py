import datetime as dt
import io
import logging
import os
import subprocess
from suntime import Sun

LATITUDE = float(os.environ.get("LATITUDE", 52.25))
LONGITUDE = float(os.environ.get("LONGITUDE", 0.11))
SUN = Sun(LATITUDE, LONGITUDE)

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
    "95",
    "--width",
    "1440",
    "--height",
    "1080",
]

S3_BUCKET = os.getenv("S3_BUCKET", "no_bucket")


def take_a_photo(cmd=PHOTO_JPG_CMD):
    logging.info("Taking a photo...")
    captured_at = dt.datetime.now(tz=dt.timezone.utc).replace(microsecond=0)
    return subprocess.run(cmd, stdout=subprocess.PIPE, check=True), captured_at


def upload_to_s3(data, captured_at, s3_bucket=S3_BUCKET):
    s3_key = captured_at.isoformat().replace("+00:00", "Z") + ".jpg"
    logging.info("Uploading %s to s3...", s3_key)
    s3 = boto3.client("s3")
    s3.upload_fileobj(io.BytesIO(data), s3_bucket, s3_key)


def tick(source=dt.datetime.now):
    now = source(tz=dt.timezone.utc)
    logging.info("Tick at %s", now)
    earliest = SUN.get_local_sunrise_time(now.date()) - dt.timedelta(minutes=15)
    latest = SUN.get_local_sunset_time(now.date()) + dt.timedelta(minutes=45)
    if now >= earliest and now <= latest:
        result, when = take_a_photo()
        upload_to_s3(data=result.stdout, captured_at=when)
    else:
        # a dummy upload, so that monitoring still stays green
        upload_to_s3(
            data=b"abc",
            captured_at=dt.datetime(2000, 1, 1, 0, 0, tzinfo=dt.timezone.utc),
        )
