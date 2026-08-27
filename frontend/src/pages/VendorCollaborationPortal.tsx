import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface ASNRecord {
  id: string;
  asn_number: string;
  vendor_name: string;
  po_number: string;
  sscc_barcode: string;
  total_cartons: number;
  shipped_qty: number;
  status: string;
  arrival_est: string;
}

export function VendorCollaborationPortal() {
  const kpis: KPICardData[] = [
    { title: 'Inbound ASNs in Transit', value: '36 Shipments', change: '+8 Today', isPositive: true, icon: '📦', subtitle: 'SSCC-18 pallet barcode labeled' },
    { title: 'Supplier OTIF Scorecard', value: '96.2%', change: '+1.4%', isPositive: true, icon: '🏆', subtitle: 'On-Time In-Full aggregate' },
    { title: '3-Way Match Pass Rate', value: '98.5%', change: '+0.8%', isPositive: true, icon: '✅', subtitle: 'PO + Receipt + Digital Invoice' },
    { title: 'Supplier Discrepancy Holds', value: '2 Shipments', change: '-1 Hold', isPositive: true, icon: '⚠️', subtitle: 'Receiving dock inspection' },
  ];

  const asns: ASNRecord[] = [
    { id: '1', asn_number: 'ASN-2026-9011', vendor_name: 'Vanguard Metallurgical', po_number: 'PO-88291', sscc_barcode: '001083920192837482', total_cartons: 40, shipped_qty: 4000, status: 'TRANSMITTED', arrival_est: 'Today 15:30' },
    { id: '2', asn_number: 'ASN-2026-9012', vendor_name: 'Precision Fasteners Global', po_number: 'PO-88292', sscc_barcode: '001083920192837499', total_cartons: 12, shipped_qty: 12000, status: 'DOCK_UNLOADED', arrival_est: 'Arrived 10:15' },
    { id: '3', asn_number: 'ASN-2026-9013', vendor_name: 'Apex Semiconductor Corp', po_number: 'PO-88293', sscc_barcode: '001083920192837512', total_cartons: 8, shipped_qty: 500, status: 'RECEIVING_VERIFIED', arrival_est: 'Completed' },
  ];

  const columns: ColumnDef<ASNRecord>[] = [
    { key: 'asn_number', header: 'ASN #', width: '18%', render: a => <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{a.asn_number}</span> },
    { key: 'vendor_name', header: 'Vendor / Supplier', width: '22%' },
    { key: 'po_number', header: 'Purchase Order', width: '15%', render: a => <span className="font-mono">{a.po_number}</span> },
    { key: 'sscc_barcode', header: 'SSCC-18 Barcode', width: '20%', render: a => <span className="font-mono text-xs text-slate-500">{a.sscc_barcode}</span> },
    { key: 'shipped_qty', header: 'Shipped Qty', width: '12%', align: 'right', render: a => a.shipped_qty.toLocaleString() },
    { key: 'status', header: 'Status', width: '13%', render: a => <span className={`px-2 py-0.5 rounded text-xs font-bold ${a.status === 'RECEIVING_VERIFIED' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'}`}>{a.status}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Vendor Collaboration Portal</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Supplier self-service Advance Shipping Notices (ASN), automated 3-way invoice matching, and OTIF scorecards</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
          ➕ Submit Advance Shipping Notice (ASN)
        </button>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Electronic Inbound ASNs & SSCC Pallets"
        subtitle="Real-time EDI 856 ship notices integrated with warehouse receiving dock scheduling"
        columns={columns}
        data={asns}
      />
    </div>
  );
}
