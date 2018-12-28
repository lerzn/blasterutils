import pytest

from web import change_params_in_url

url = "https://www.etsy.com/your/shops/me/stats/traffic?ref=seller-platform-mcnav&start_date=2018-12-24&end_date=2018-12-25"
test_result_url = "https://www.etsy.com/your/shops/me/stats/traffic?ref=seller-platform-mcnav&start_date=2018-01-01&end_date=2018-12-25"


def test_change_params_in_url_basic():
    assert change_params_in_url(url, {"start_date": "2018-01-01"}) == test_result_url


def test_change_params_in_url_keyerror():
    with pytest.raises(Exception) as exc_info:
        change_params_in_url(url, {"no_key": "any_value"})
    assert exc_info.type == KeyError


def test_change_params_in_url_not_strict():
    expected_result = url + "&test=passed"
    actual_result = change_params_in_url(url, {"test": "passed"}, False)
    assert expected_result == actual_result
