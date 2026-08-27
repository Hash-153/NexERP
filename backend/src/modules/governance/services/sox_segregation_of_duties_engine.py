"""
SOX 404 Segregation of Duties (SoD) & Conflict Detection Engine.
Enforces toxic combination rules (e.g. Can Create Vendor AND Can Post AP Payment).
"""
from typing import Dict, Any, List, Set

class SOXSegregationOfDutiesEngine:
    TOXIC_COMBINATIONS = [
        {
            "code": "SOD-FIN-01",
            "name": "Vendor Creation vs AP Disbursement",
            "perm_a": "ap:vendor:create",
            "perm_b": "ap:payment:post",
            "risk": "HIGH",
            "description": "User can create fictitious vendor and issue disbursements"
        },
        {
            "code": "SOD-FIN-02",
            "name": "General Ledger Entry vs Journal Approval",
            "perm_a": "gl:journal:create",
            "perm_b": "gl:journal:approve",
            "risk": "CRITICAL",
            "description": "User can post unreviewed adjustments to financial statements"
        },
        {
            "code": "SOD-SCM-01",
            "name": "Purchase Order Creation vs Goods Receipt",
            "perm_a": "po:create",
            "perm_b": "wms:receive",
            "risk": "MEDIUM",
            "description": "User can place purchase orders and verify unreceived inventory"
        },
        {
            "code": "SOD-HR-01",
            "name": "Employee Onboarding vs Direct Payroll Disbursement",
            "perm_a": "hr:employee:create",
            "perm_b": "hr:payroll:disburse",
            "risk": "CRITICAL",
            "description": "User can create ghost employees and issue payroll transfers"
        },
    ]

    @classmethod
    def evaluate_user_permissions(cls, user_id: str, user_permissions: List[str]) -> Dict[str, Any]:
        user_perm_set = set(user_permissions)
        detected_conflicts = []

        for rule in cls.TOXIC_COMBINATIONS:
            has_a = rule["perm_a"] in user_perm_set or "*" in user_perm_set
            has_b = rule["perm_b"] in user_perm_set or "*" in user_perm_set

            if has_a and has_b:
                detected_conflicts.append({
                    "rule_code": rule["code"],
                    "conflict_name": rule["name"],
                    "risk_severity": rule["risk"],
                    "description": rule["description"],
                    "conflicting_permissions": [rule["perm_a"], rule["perm_b"]]
                })

        return {
            "user_id": user_id,
            "total_permissions_checked": len(user_permissions),
            "conflicts_found_count": len(detected_conflicts),
            "is_sox_compliant": len(detected_conflicts) == 0,
            "conflicts": detected_conflicts
        }
