import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface EmissionLogItem {
  id: string;
  facility_name: string;
  scope: string;
  energy_type: string;
  consumed: string;
  tco2e: number;
}

export function ESGComplianceReporting() {
  const kpis: KPICardData[] = [
    { title: 'Total GHG Footprint (YTD)', value: '1,420 tCO2e', change: '-8.5%', isPositive: true, icon: '🌱', subtitle: 'Scope 1, 2 & 3 emissions' },
    { title: 'Renewable Energy Share', value: '64.2%', change: '+12.4%', isPositive: true, icon: '☀️', subtitle: 'Solar rooftop + PPA green grid' },
    { title: 'Water Recycling Ratio', value: '78.5%', change: '+5.1%', isPositive: true, icon: '💧', subtitle: 'Closed-loop industrial coolant' },
    { title: 'Supplier ESG Score Average', value: '82 / 100', change: '+4 pts', isPositive: true, icon: '📋', subtitle: 'CSRD supply chain audited' },
  ];

  const emissions: EmissionLogItem[] = [
    { id: '1', facility_name: 'Austin Advanced Manufacturing Hub', scope: 'SCOPE_2_MARKET_BASED', energy_type: 'Purchased Grid Electricity', consumed: '1,250,000 kWh', tco2e: 425.5 },
    { id: '2', facility_name: 'Austin Advanced Manufacturing Hub', scope: 'SCOPE_1_DIRECT', energy_type: 'Natural Gas Industrial Furnace', consumed: '4,500 MMBtu', tco2e: 238.9 },
    { id: '3', facility_name: 'Dallas Distribution Logistics DC', scope: 'SCOPE_1_DIRECT', energy_type: 'Fleet Diesel Combustion', consumed: '85,000 Liters', tco2e: 227.8 },
    { id: '4', facility_name: 'Global Supply Chain Value Chain', scope: 'SCOPE_3_VALUE_CHAIN', energy_type: 'Freight Logistics & Packaging', consumed: 'Activity Spend', tco2e: 527.8 },
  ];

  const columns: ColumnDef<EmissionLogItem>[] = [
    { key: 'facility_name', header: 'Facility / Source', width: '30%' },
    { key: 'scope', header: 'GHG Scope', width: '22%', render: e => <span className="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800 font-bold font-mono">{e.scope}</span> },
    { key: 'energy_type', header: 'Activity Type', width: '24%' },
    { key: 'consumed', header: 'Consumption', width: '12%', align: 'right' },
    { key: 'tco2e', header: 'Emissions (tCO2e)', width: '12%', align: 'right', render: e => <span className="font-bold text-slate-900 dark:text-white">{e.tco2e} t</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Compliance & ESG Reporting</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">GHG Protocol Scope 1, 2, and 3 carbon accounting, CSRD ESRS disclosures, and supplier audits</p>
        </div>
        <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
          📄 Export CSRD / GRI Disclosure Report
        </button>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Verified Carbon Emissions Activity Log"
        subtitle="Continuous activity data ingestion mapped to IPCC / EPA regional emission factors"
        columns={columns}
        data={emissions}
      />
    </div>
  );
}
