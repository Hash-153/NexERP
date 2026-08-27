"""
Intercompany Consolidation & Elimination Journal Engine.
Eliminates intercompany AR/AP balances, intercompany sales/COGS, and unrealized inventory profits.
"""
from decimal import Decimal
from typing import Dict, Any, List

class IntercompanyEliminationsEngine:
    @staticmethod
    def eliminate_intercompany_transactions(
        entity_a_id: str,
        entity_b_id: str,
        ic_sales_revenue: Decimal,
        ic_purchased_inventory_cost: Decimal,
        unrealized_profit_margin_pct: Decimal = Decimal("20.0")
    ) -> Dict[str, Any]:
        """
        Generates consolidation elimination entries:
        Debit: Intercompany Sales Revenue
        Credit: Intercompany Cost of Goods Sold (COGS)
        Credit: Inventory (Unrealized Intercompany Profit)
        """
        unrealized_profit = (ic_purchased_inventory_cost * (unrealized_profit_margin_pct / Decimal("100.0"))).quantize(Decimal("0.01"))
        eliminated_cogs = ic_sales_revenue - unrealized_profit

        journal_lines = [
            {"account_code": "49000", "account_name": "Intercompany Sales Revenue", "debit": float(ic_sales_revenue), "credit": 0.0},
            {"account_code": "59000", "account_name": "Intercompany COGS", "debit": 0.0, "credit": float(eliminated_cogs)},
            {"account_code": "14900", "account_name": "Inventory - Intercompany Profit Reserve", "debit": 0.0, "credit": float(unrealized_profit)},
        ]

        return {
            "entity_parent": entity_a_id,
            "entity_subsidiary": entity_b_id,
            "gross_intercompany_sales": float(ic_sales_revenue),
            "eliminated_cogs": float(eliminated_cogs),
            "unrealized_inventory_profit_eliminated": float(unrealized_profit),
            "elimination_journal_voucher": journal_lines
        }
