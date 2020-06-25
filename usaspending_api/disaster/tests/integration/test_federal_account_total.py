import pytest
import json
from model_mommy import mommy
from rest_framework import status

url = "/api/v2/disaster/federal_account/spending/"


@pytest.fixture
def account_data():
    mommy.make("references.DisasterEmergencyFundCode", code="A")
    fed_acct1 = mommy.make("accounts.FederalAccount", account_title="gifts", federal_account_code="000-0000", id=21)
    tre_acct1 = mommy.make(
        "accounts.TreasuryAppropriationAccount",
        federal_account=fed_acct1,
        tas_rendering_label="2020/99",
        account_title="flowers",
        treasury_account_identifier=22,
        gtas__budget_authority_appropriation_amount_cpe=4358,
    )
    tre_acct2 = mommy.make(
        "accounts.TreasuryAppropriationAccount",
        federal_account=fed_acct1,
        tas_rendering_label="2020/98",
        account_title="evergreens",
        treasury_account_identifier=23,
        gtas__budget_authority_appropriation_amount_cpe=109237,
    )
    tre_acct3 = mommy.make(
        "accounts.TreasuryAppropriationAccount",
        federal_account=fed_acct1,
        tas_rendering_label="2020/52",
        account_title="ferns",
        treasury_account_identifier=24,
        gtas__budget_authority_appropriation_amount_cpe=39248,
    )
    sub1 = mommy.make(
        "submissions.SubmissionAttributes",
        reporting_period_start="2020-05-15",
        reporting_period_end="2020-05-29",
        reporting_fiscal_year=2020,
        reporting_fiscal_quarter=3,
        reporting_fiscal_period=7,
        quarter_format_flag=False,
    )
    mommy.make(
        "financial_activities.FinancialAccountsByProgramActivityObjectClass",
        submission=sub1,
        final_of_fy=True,
        obligations_incurred_by_program_object_class_cpe=100,
        gross_outlay_amount_by_program_object_class_cpe=111,
        disaster_emergency_fund__code="M",
        treasury_account=tre_acct1,
    )
    mommy.make(
        "financial_activities.FinancialAccountsByProgramActivityObjectClass",
        submission=sub1,
        final_of_fy=True,
        obligations_incurred_by_program_object_class_cpe=200,
        gross_outlay_amount_by_program_object_class_cpe=222,
        disaster_emergency_fund__code="L",
        treasury_account=tre_acct2,
    )
    mommy.make(
        "financial_activities.FinancialAccountsByProgramActivityObjectClass",
        submission=sub1,
        final_of_fy=True,
        obligations_incurred_by_program_object_class_cpe=2,
        gross_outlay_amount_by_program_object_class_cpe=2,
        disaster_emergency_fund__code="9",
        treasury_account=tre_acct2,
    )
    mommy.make(
        "financial_activities.FinancialAccountsByProgramActivityObjectClass",
        submission=sub1,
        final_of_fy=True,
        obligations_incurred_by_program_object_class_cpe=1,
        gross_outlay_amount_by_program_object_class_cpe=1,
        disaster_emergency_fund__code="O",
        treasury_account=tre_acct2,
    )
    mommy.make(
        "financial_activities.FinancialAccountsByProgramActivityObjectClass",
        submission=sub1,
        final_of_fy=True,
        obligations_incurred_by_program_object_class_cpe=3,
        gross_outlay_amount_by_program_object_class_cpe=333,
        disaster_emergency_fund__code="N",
        treasury_account=tre_acct3,
    )


@pytest.mark.django_db
def test_federal_account_success(client, account_data, monkeypatch, helpers):
    helpers.patch_datetime_now(monkeypatch, 2020, 6, 20)
    body = {"filter": {"def_codes": ["M"]}, "spending_type": "total"}
    resp = client.post(url, content_type="application/json", data=json.dumps(body))
    expected_results = [
        {
            "children": [
                {
                    "code": "2020/99",
                    "count": 1,
                    "description": "flowers",
                    "id": 22,
                    "obligation": 100.0,
                    "outlay": 111.0,
                    "total_budgetary_resources": 4358.0,
                }
            ],
            "code": "000-0000",
            "count": 1,
            "description": "gifts",
            "id": 21,
            "obligation": 100.0,
            "outlay": 111.0,
            "total_budgetary_resources": 4358.0,
        }
    ]
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results

    body = {"filter": {"def_codes": ["M", "L", "N", "O"]}, "spending_type": "total"}
    resp = client.post(url, content_type="application/json", data=json.dumps(body))
    expected_results = [
        {
            "children": [
                {
                    "code": "2020/52",
                    "count": 1,
                    "description": "ferns",
                    "id": 24,
                    "obligation": 3.0,
                    "outlay": 333.0,
                    "total_budgetary_resources": 39248.0,
                },
                {
                    "code": "2020/98",
                    "count": 1,
                    "description": "evergreens",
                    "id": 23,
                    "obligation": 201.0,
                    "outlay": 223.0,
                    "total_budgetary_resources": 218474.0,
                },
                {
                    "code": "2020/99",
                    "count": 1,
                    "description": "flowers",
                    "id": 22,
                    "obligation": 100.0,
                    "outlay": 111.0,
                    "total_budgetary_resources": 4358.0,
                },
            ],
            "code": "000-0000",
            "count": 3,
            "description": "gifts",
            "id": 21,
            "obligation": 304.0,
            "outlay": 667.0,
            "total_budgetary_resources": 262080.0,
        }
    ]
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results


@pytest.mark.django_db
def test_federal_account_empty(client, account_data):
    body = {"filter": {"def_codes": ["A"]}, "spending_type": "total"}
    resp = client.post(url, content_type="application/json", data=json.dumps(body))
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["results"]) == 0
