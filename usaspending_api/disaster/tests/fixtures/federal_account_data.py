import pytest

from model_mommy import mommy


@pytest.fixture
def generic_account_data():
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        is_quarter=False,
        submission_fiscal_year=2022,
        submission_fiscal_quarter=3,
        submission_fiscal_month=7,
        submission_reveal_date="2022-6-15",
    )
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        is_quarter=True,
        submission_fiscal_year=2022,
        submission_fiscal_quarter=3,
        submission_fiscal_month=7,
        submission_reveal_date="2022-6-15",
    )
    mommy.make("references.DisasterEmergencyFundCode", code="P")
    mommy.make("references.DisasterEmergencyFundCode", code="A")
    award1 = mommy.make("awards.Award", id=111, total_loan_value=1111, type="A")
    award2 = mommy.make("awards.Award", id=222, total_loan_value=2222, type="A")
    award3 = mommy.make("awards.Award", id=333, total_loan_value=3333, type="10")
    award4 = mommy.make("awards.Award", id=444, total_loan_value=4444, type="09")
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
        reporting_period_start="2022-05-15",
        reporting_period_end="2022-05-29",
        reporting_fiscal_year=2022,
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
    mommy.make(
        "awards.FinancialAccountsByAwards",
        submission=sub1,
        piid="0wefjwe",
        parent_award_id="3443r",
        transaction_obligated_amount=100,
        gross_outlay_amount_by_award_cpe=111,
        disaster_emergency_fund__code="M",
        treasury_account=tre_acct1,
    )
    mommy.make(
        "awards.FinancialAccountsByAwards",
        submission=sub1,
        award=award1,
        piid="0wefjwe",
        parent_award_id="3443r",
        transaction_obligated_amount=200,
        gross_outlay_amount_by_award_cpe=222,
        disaster_emergency_fund__code="L",
        treasury_account=tre_acct2,
    )
    mommy.make(
        "awards.FinancialAccountsByAwards",
        submission=sub1,
        award=award2,
        uri="3298rhed",
        transaction_obligated_amount=2,
        gross_outlay_amount_by_award_cpe=2,
        disaster_emergency_fund__code="9",
        treasury_account=tre_acct2,
    )
    mommy.make(
        "awards.FinancialAccountsByAwards",
        submission=sub1,
        award=award3,
        fain="43tgfvdvfv",
        transaction_obligated_amount=1,
        gross_outlay_amount_by_award_cpe=1,
        disaster_emergency_fund__code="O",
        treasury_account=tre_acct2,
    )
    mommy.make(
        "awards.FinancialAccountsByAwards",
        submission=sub1,
        award=award4,
        fain="woefhowe",
        transaction_obligated_amount=3,
        gross_outlay_amount_by_award_cpe=333,
        disaster_emergency_fund__code="N",
        treasury_account=tre_acct3,
    )


@pytest.fixture
def unlinked_faba_account_data():
    fed_acct = mommy.make("accounts.FederalAccount", account_title="soap", federal_account_code="999-0000", id=99)
    tre_acct = mommy.make(
        "accounts.TreasuryAppropriationAccount",
        federal_account=fed_acct,
        tas_rendering_label="2020/99",
        account_title="dove",
        treasury_account_identifier=99,
        gtas__budget_authority_appropriation_amount_cpe=9939248,
    )
    sub = mommy.make(
        "submissions.SubmissionAttributes",
        reporting_period_start="2022-05-15",
        reporting_period_end="2022-05-29",
        reporting_fiscal_year=2022,
        reporting_fiscal_quarter=3,
        reporting_fiscal_period=7,
        quarter_format_flag=False,
    )
    mommy.make(
        "awards.FinancialAccountsByAwards",
        submission=sub,
        piid="weuf",
        transaction_obligated_amount=999999,
        gross_outlay_amount_by_award_cpe=9999999,
        disaster_emergency_fund__code="N",
        treasury_account=tre_acct,
    )
    mommy.make(
        "awards.FinancialAccountsByAwards",
        submission=sub,
        piid="weuf",
        parent_award_id="weuf22",
        transaction_obligated_amount=88888,
        gross_outlay_amount_by_award_cpe=888888,
        disaster_emergency_fund__code="N",
        treasury_account=tre_acct,
    )
