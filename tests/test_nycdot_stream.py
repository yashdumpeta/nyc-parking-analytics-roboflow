from unittest.mock import patch, MagicMock
import cv2
import numpy as np
import pytest
from nycdot_stream import NYCDOTStreamReader


def _create_dummy_jpeg():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".jpg", img)
    return encoded.tobytes()


def test_nycdot_stream_reader_caching():
    dummy_jpeg = _create_dummy_jpeg()
    reader = NYCDOTStreamReader("https://fake-url.com/image", poll_interval=60.0)

    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = dummy_jpeg
        mock_get.return_value = mock_resp

        # First fetch
        frame1 = reader.get_latest_frame()
        assert frame1 is not None
        assert mock_get.call_count == 1

        # Second fetch within 60s without force should return cached frame without network call
        frame2 = reader.get_latest_frame(force=False)
        assert frame2 is not None
        assert mock_get.call_count == 1

        # Forced fetch should invoke network call
        frame3 = reader.get_latest_frame(force=True)
        assert frame3 is not None
        assert mock_get.call_count == 2


@pytest.mark.anyio
async def test_nycdot_stream_reader_async():
    dummy_jpeg = _create_dummy_jpeg()
    reader = NYCDOTStreamReader("https://fake-url.com/image", poll_interval=60.0)

    with patch("httpx.AsyncClient.get") as mock_async_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = dummy_jpeg
        mock_async_get.return_value = mock_resp

        frame = await reader.get_latest_frame_async(force=True)
        assert frame is not None
        assert frame.shape == (100, 100, 3)
