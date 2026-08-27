"""
NexERP Outside Processing & Subcontracting Service.
Manages:
- Outbound delivery of raw / semi-finished parent materials to third-party sub-contractors (e.g. Anodizing / Plating / Heat Treat)
- Subcontract Purchase Order creation with service fee per unit
- Inbound receipt of processed finished components and WIP cost capitalization.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class SubcontractingService:
    """
    Subcontracting / Outside Processing Workflow Service.
    """

    @classmethod
    def calculate_subcontract_job_cost(
        cls,
        subcontract_po_number: str,
        supplier_id: str,
        supplier_name: str,
        parent_item_sku: str,
        processed_item_sku: str,
        quantity_sent_to_subcontractor: Decimal,
        unit_service_charge: Decimal,
        parent_material_unit_cost: Decimal,
        freight_handling_charge: Decimal = Decimal("0.0")
    ) -> Dict:
        """
        Compute total capitalized inventory cost of subcontractor processed components.
        """
        service_cost_total = (quantity_sent_to_subcontractor * unit_service_charge).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        parent_material_cost_total = (quantity_sent_to_subcontractor * parent_material_unit_cost).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total_capitalized_cost = parent_material_cost_total + service_cost_total + freight_handling_charge
        new_unit_inventory_cost = (total_capitalized_cost / quantity_sent_to_subcontractor).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if quantity_sent_to_subcontractor > Decimal("0.0") else Decimal("0.0")

        return {
            "subcontract_po_number": subcontract_po_number,
            "subcontractor_id": supplier_id,
            "subcontractor_name": supplier_name,
            "input_material_sku": parent_item_sku,
            "output_processed_sku": processed_item_sku,
            "quantity_processed": float(quantity_sent_to_subcontractor),
            "parent_material_cost_total": float(parent_material_cost_total),
            "subcontract_service_cost_total": float(service_cost_total),
            "freight_handling_charge": float(freight_handling_charge),
            "total_capitalized_finished_cost": float(total_capitalized_cost),
            "new_unit_cost": float(new_unit_inventory_cost)
        }
