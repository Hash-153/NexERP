"""
NexERP Global Master Taxonomies & Regulatory Reference Data.
"""
from .gaap_chart_of_accounts_reference import GAAP_CHART_OF_ACCOUNTS_TAXONOMY
from .harmonized_tariff_schedule_dictionary import HTS_TARIFF_SCHEDULE_DICTIONARY
from .naics_industry_classification_reference import NAICS_INDUSTRY_TAXONOMY
from .statutory_state_tax_nexus_tables import STATE_TAX_NEXUS_STATUTORY_TABLES

__all__ = [
    "GAAP_CHART_OF_ACCOUNTS_TAXONOMY",
    "HTS_TARIFF_SCHEDULE_DICTIONARY",
    "NAICS_INDUSTRY_TAXONOMY",
    "STATE_TAX_NEXUS_STATUTORY_TABLES",
]
