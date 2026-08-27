"""
NexERP Quality Control, SPC, AQL, and Six Sigma Test Suite.
"""

import pytest

from backend.src.modules.quality_control.services import (
    SPCControlChartService,
    AQLSamplingService,
    EightDCorrectiveActionService,
    FMEARiskService
)


def test_spc_xbar_r_chart_and_capability_indices():
    """
    Verify X-bar and R control chart calculation with 5 subgroups of size 4.
    """
    subgroups = [
        [10.1, 10.2, 10.0, 10.1],
        [10.0, 10.1, 10.3, 10.2],
        [10.2, 10.1, 10.1, 10.0],
        [10.1, 10.3, 10.2, 10.1],
        [10.0, 10.2, 10.1, 10.2],
    ]

    res = SPCControlChartService.calculate_xbar_r_control_chart(
        subgroups=subgroups,
        upper_spec_limit=10.6,
        lower_spec_limit=9.6
    )

    assert res["subgroups_count"] == 5
    assert res["subgroup_size"] == 4
    assert res["process_state"] == "STATISTICAL_CONTROL"
    assert res["process_capability"]["cpk"] is not None
    assert res["process_capability"]["cpk"] > 1.0


def test_aql_sampling_plan_generation_and_disposition():
    """
    Verify ANSI/ASQ Z1.4 lot sampling:
    Lot size: 500 units, AQL: 2.5% -> Sample size: 50 units (Code Letter H), Ac=3, Re=4.
    2 defects found -> ACCEPTED.
    5 defects found -> REJECTED.
    """
    plan = AQLSamplingService.get_sampling_plan(lot_size=500, aql_target_percent=2.5)
    assert plan["sample_size_code_letter"] == "H"
    assert plan["sample_size_units_to_pull"] == 50
    assert plan["acceptance_number_ac"] == 3
    assert plan["rejection_number_re"] == 4

    disp_pass = AQLSamplingService.evaluate_lot_disposition(lot_size=500, defects_found_count=2, aql_target_percent=2.5)
    assert disp_pass["disposition"] == "ACCEPTED"

    disp_fail = AQLSamplingService.evaluate_lot_disposition(lot_size=500, defects_found_count=5, aql_target_percent=2.5)
    assert disp_fail["disposition"] == "REJECTED_QC_HOLD"


def test_fmea_rpn_calculation_and_action_priority():
    """
    Verify FMEA Risk Priority Number:
    Severity: 8, Occurrence: 6, Detection: 5 -> RPN = 240 (Action Priority: HIGH).
    """
    res = FMEARiskService.calculate_rpn(severity=8, occurrence=6, detection=5)
    assert res["risk_priority_number_rpn"] == 240
    assert res["action_priority"] == "HIGH"
