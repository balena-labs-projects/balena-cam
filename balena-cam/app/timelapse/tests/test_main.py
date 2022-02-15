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

    @mock.patch.object(main, "take_a_photo")
    @mock.patch.object(main, "upload_to_s3")
    def test_tick_night_time(self, upload, _m2):
        when = dt.datetime(2022, 2, 15, 21, 0, tzinfo=dt.timezone.utc)
        main.tick(source=mock.Mock(return_value=when))
        upload.assert_called_once_with(
            captured_at=dt.datetime(2000, 1, 1, 0, 0, tzinfo=dt.timezone.utc),
            data=b"abc",
        )

    @mock.patch.object(main, "take_a_photo")
    @mock.patch.object(main, "upload_to_s3")
    def test_tick_day_time(self, upload, take):
        data = b"foo"
        when = dt.datetime(2022, 2, 15, 14, 00, tzinfo=dt.timezone.utc)
        take.return_value = (mock.Mock(stdout=data), when)
        main.tick(source=mock.Mock(return_value=when))
        upload.assert_called_once_with(
            captured_at=when,
            data=data,
        )
