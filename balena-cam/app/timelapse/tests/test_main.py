import datetime as dt
from unittest import TestCase, mock

import main


class TimelapseTestCase(TestCase):
    def test_take_a_photo(self):
        # example.jpg is 21658 bytes
        result, captured_at = main.take_a_photo(cmd=["cat", "example.jpg"])
        self.assertEqual(21658, len(result.stdout))
        self.assertIsInstance(captured_at, dt.datetime)

    def test_upload_to_s3(self):
        result, captured_at = main.take_a_photo(cmd=["cat", "example.jpg"])
        with mock.patch.object(main, "boto3") as b3:
            main.upload_to_s3(data=result.stdout, captured_at=captured_at)
        self.assertEqual(b3.client.return_value.upload_fileobj.call_count, 1)
