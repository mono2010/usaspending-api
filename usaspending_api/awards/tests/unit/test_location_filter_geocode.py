import pytest

from model_mommy import mommy
from usaspending_api.awards.models_matviews import UniversalAwardView
from usaspending_api.awards.v2.filters.location_filter_geocode import (
    create_nested_object,
    geocode_filter_locations,
    get_fields_list,
    location_error_handling,
    return_query_string,
    validate_location_keys,
)
from usaspending_api.common.exceptions import InvalidParameterException


@pytest.fixture
def award_data_fixture(db):
    mommy.make("references.LegalEntity", legal_entity_id=1)
    mommy.make(
        "awards.TransactionNormalized",
        id=1,
        action_date="2010-10-01",
        award_id=1,
        is_fpds=True,
        type="A",
    )
    mommy.make(
        "awards.TransactionFPDS",
        transaction_id=1,
        legal_entity_city_name="BURBANK",
        legal_entity_country_code="USA",
        legal_entity_state_code="CA",
        piid="piiiiid",
        place_of_perform_city_name="AUSTIN",
        place_of_performance_state="TX",
        place_of_perform_country_c="USA",
    )
    mommy.make(
        "awards.Award",
        id=1,
        is_fpds=True,
        latest_transaction_id=1,
        piid="piiiiid",
        recipient_id=1,
        type="A",
    )


def test_geocode_filter_locations(award_data_fixture, refresh_matviews):

    to = UniversalAwardView.objects

    values = [
        {"city": "HOUSTON", "state": "TX", "country": "USA"},
        {"city": "BURBANK", "state": "CA", "country": "USA"},
    ]

    assert to.filter(geocode_filter_locations("nothing", [], True)).count() == 1
    assert to.filter(geocode_filter_locations("pop", values, True)).count() == 0
    assert to.filter(geocode_filter_locations("recipient_location", values, True)).count() == 1

    values = [
        {"city": "AUSTIN", "state": "TX", "country": "USA"},
        {"city": "BURBANK", "state": "TX", "country": "USA"},
    ]

    assert to.filter(geocode_filter_locations("pop", values, True)).count() == 1
    assert to.filter(geocode_filter_locations("recipient_location", values, True)).count() == 0


def test_validate_location_keys():
    assert validate_location_keys([]) is None
    with pytest.raises(InvalidParameterException):
        assert validate_location_keys([{}]) is None
    with pytest.raises(InvalidParameterException):
        assert validate_location_keys([{"district": ""}]) is None
    with pytest.raises(InvalidParameterException):
        assert validate_location_keys([{"county": ""}]) is None
    assert validate_location_keys([{"country": "", "state": ""}]) is None
    assert validate_location_keys([{"country": "", "state": "", "feet": ""}]) is None
    assert (
        validate_location_keys(
            [
                {
                    "country": "USA",
                    "zip": "12345",
                    "city": "Chicago",
                    "state": "IL",
                    "county": "Yes",
                    "district": "Also Yes",
                },
                {"country": "USA", "zip": "12345", "city": "Chicago"},
            ]
        )
        is None
    )


def test_create_nested_object():
    with pytest.raises(InvalidParameterException):
        location_error_handling([])
    with pytest.raises(InvalidParameterException):
        location_error_handling([{"country": "", "state": ""}])
    with pytest.raises(InvalidParameterException):
        location_error_handling([{"country": "", "state": "", "feet": ""}])
    assert create_nested_object(
        [
            {
                "country": "USA",
                "zip": "12345",
                "city": "Chicago",
                "state": "IL",
                "county": "Yes",
                "district": "Also Yes",
            },
            {"country": "USA", "zip": "12345", "city": "Chicago"},
        ]
    ) == {
        "USA": {
            "city": ["Chicago"],
            "zip": ["12345", "12345"],
            "IL": {"county": ["Yes"], "district": ["Also Yes"], "city": ["Chicago"]},
        }
    }


def test_location_error_handling():
    with pytest.raises(InvalidParameterException):
        location_error_handling({})
    with pytest.raises(InvalidParameterException):
        location_error_handling({"country": "", "county": ""})
    with pytest.raises(InvalidParameterException):
        location_error_handling({"country": "", "district": ""})
    assert location_error_handling({"country": "", "state": "", "county": ""}) is None
    assert location_error_handling({"country": "", "state": "", "district": ""}) is None
    assert location_error_handling({"country": "", "state": "", "county": "", "district": ""}) is None
    assert location_error_handling({"country": "", "state": "", "county": "", "district": "", "feet": ""}) is None


def test_get_fields_list():
    assert get_fields_list("congressional_code", "01") == ["1", "01", "1.0"]
    assert get_fields_list("county_code", "01") == ["1", "01", "1.0"]
    assert get_fields_list("feet", "01") == ["01"]
    assert get_fields_list("congressional_code", "abc") == ["abc"]


def test_return_query_string():
    assert return_query_string(True) == ("{0}_{1}", "country_code")
    assert return_query_string(False) == ("{0}__{1}", "location_country_code")
