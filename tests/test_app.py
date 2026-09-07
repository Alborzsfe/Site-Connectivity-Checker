from unittest.mock import Mock, patch

import pytest
import requests

from app import check_many, check_site_availability, normalize_url


def test_normalize_url_adds_https_without_www():
    assert normalize_url("example.com/path") == "https://example.com/path"


@pytest.mark.parametrize("value", ["", "ftp://example.com", "https://user:pass@example.com"])
def test_normalize_url_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        normalize_url(value)


@patch("app.is_public_destination", return_value=False)
def test_private_destination_is_not_requested(_public):
    with patch("app.requests.get") as get:
        _, available, detail = check_site_availability("http://127.0.0.1")
    assert not available
    assert "Blocked" in detail
    get.assert_not_called()


@patch("app.is_public_destination", return_value=True)
@patch("app.requests.get")
def test_success_uses_one_request(get, _public):
    get.return_value = Mock(status_code=204)
    _, available, detail = check_site_availability("example.com")
    assert available
    assert detail == "HTTP 204"
    get.assert_called_once()


@patch("app.is_public_destination", return_value=True)
@patch("app.requests.get", side_effect=requests.Timeout)
def test_timeout_is_reported(_get, _public):
    _, available, detail = check_site_availability("example.com")
    assert not available
    assert detail == "Timeout"


@patch("app.check_site_availability", side_effect=lambda url: (url, True, "HTTP 200"))
def test_check_many_preserves_all_results(_check):
    results = check_many(["https://a.example", "https://b.example"])
    assert len(results) == 2
