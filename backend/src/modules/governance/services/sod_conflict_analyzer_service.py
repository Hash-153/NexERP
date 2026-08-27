"""
NexERP Segregation of Duties (SoD) Conflict Analyzer Engine (SOX 404).
Detects incompatible toxic permission combinations:
- AP Invoice Creator + AP Payment Releaser
- Purchase Order Approver + Goods Receipt Poster
- GL Journal Entry Poster + Bank Statement Reconciler
- Master Payroll Editor + Paycheck Disbursement Releaser.
"""

from typing import Dict, List, Set


class SoDConflictAnalyzerService:
    """
    Segregation of Duties (SoD) Toxic Role Combination Audit Service.
    """

    # Incompatible Toxic Privilege Pairs
    TOXIC_CONFLICT_RULES = [
        {
            "rule_code": "SOD-FIN-01",
            "perm_a": "AP_INVOICE_CREATE",
            "perm_b": "AP_PAYMENT_RELEASE",
            "risk_level": "CRITICAL",
            "description": "User can create vendor bills and release cash disbursements, enabling fraudulent payouts."
        },
        {
            "rule_code": "SOD-SCM-02",
            "perm_a": "PURCHASE_ORDER_APPROVE",
            "perm_b": "GOODS_RECEIPT_POST",
            "risk_level": "HIGH",
            "description": "User can authorize purchase orders and confirm physical inventory receipt without independent check."
        },
        {
            "rule_code": "SOD-FIN-03",
            "perm_a": "GL_JOURNAL_POST",
            "perm_b": "BANK_RECONCILIATION_POST",
            "risk_level": "CRITICAL",
            "description": "User can post manual journal entries and clear bank reconciliation variances."
        },
        {
            "rule_code": "SOD-HR-04",
            "perm_a": "PAYROLL_MASTER_EDIT",
            "perm_b": "PAYROLL_PAYMENT_EXECUTE",
            "risk_level": "CRITICAL",
            "description": "User can alter employee salary rates and execute salary disbursements."
        }
    ]

    @classmethod
    def audit_user_role_privileges(
        cls,
        user_id: str,
        username: str,
        assigned_permissions: List[str]
    ) -> Dict:
        """
        Scan user's combined assigned privileges for toxic SoD violations.
        """
        user_perms_set = set(assigned_permissions)
        detected_conflicts = []

        for rule in cls.TOXIC_CONFLICT_RULES:
            if rule["perm_a"] in user_perms_set and rule["perm_b"] in user_perms_set:
                detected_conflicts.append({
                    "rule_code": rule["rule_code"],
                    "risk_level": rule["risk_level"],
                    "conflicting_privilege_1": rule["perm_a"],
                    "conflicting_privilege_2": rule["perm_b"],
                    "threat_description": rule["description"]
                })

        is_compliant = len(detected_conflicts) == 0

        return {
            "user_id": user_id,
            "username": username,
            "total_assigned_permissions": len(assigned_permissions),
            "is_sod_compliant": is_compliant,
            "detected_conflicts_count": len(detected_conflicts),
            "detected_conflicts": detected_conflicts,
            "audit_recommendation": "Pass - No toxic privilege combinations detected." if is_compliant else "Revoke conflicting role permissions or establish compensating managerial sign-off controls."
        }
