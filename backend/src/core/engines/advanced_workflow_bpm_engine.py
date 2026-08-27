"""
BPMN 2.0 Enterprise Multi-Stage Approval State Machine Engine.
Evaluates parallel and sequential approval chains, conditional routing gates, and authority limits.
"""
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class AdvancedWorkflowBPMEngine:
    APPROVAL_MATRICES = {
        "PURCHASE_ORDER": [
            {"tier": 1, "max_amount": Decimal("10000.00"), "required_role": "DepartmentManager", "sla_hours": 24},
            {"tier": 2, "max_amount": Decimal("50000.00"), "required_role": "VP_Operations", "sla_hours": 48},
            {"tier": 3, "max_amount": Decimal("250000.00"), "required_role": "CFO", "sla_hours": 72},
            {"tier": 4, "max_amount": Decimal("999999999.00"), "required_role": "BoardOfDirectors", "sla_hours": 120},
        ],
        "JOURNAL_ENTRY": [
            {"tier": 1, "max_amount": Decimal("25000.00"), "required_role": "AccountingSupervisor", "sla_hours": 12},
            {"tier": 2, "max_amount": Decimal("100000.00"), "required_role": "CorporateController", "sla_hours": 24},
            {"tier": 3, "max_amount": Decimal("999999999.00"), "required_role": "CFO", "sla_hours": 48},
        ],
        "CONTRACT_DISCOUNT": [
            {"tier": 1, "max_discount_pct": Decimal("10.0"), "required_role": "SalesManager", "sla_hours": 4},
            {"tier": 2, "max_discount_pct": Decimal("20.0"), "required_role": "VP_Sales", "sla_hours": 12},
            {"tier": 3, "max_discount_pct": Decimal("35.0"), "required_role": "CEO_DealDesk", "sla_hours": 24},
        ]
    }

    @classmethod
    def resolve_required_approvers(
        cls,
        workflow_type: str,
        transaction_amount: Decimal,
        is_emergency: bool = False
    ) -> Dict[str, Any]:
        matrix = cls.APPROVAL_MATRICES.get(workflow_type, cls.APPROVAL_MATRICES["PURCHASE_ORDER"])
        required_steps = []

        for rule in matrix:
            required_steps.append({
                "tier": rule["tier"],
                "required_role": rule["required_role"],
                "sla_hours": rule["sla_hours"] if not is_emergency else rule["sla_hours"] // 2
            })
            if transaction_amount <= rule.get("max_amount", Decimal("999999999.00")):
                break

        return {
            "workflow_type": workflow_type,
            "transaction_amount": float(transaction_amount),
            "is_emergency_expedited": is_emergency,
            "total_approval_stages": len(required_steps),
            "approval_path": required_steps,
            "initial_stage_role": required_steps[0]["required_role"] if required_steps else "SuperAdmin"
        }
