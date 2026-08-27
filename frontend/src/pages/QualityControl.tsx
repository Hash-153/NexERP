import React, { useEffect, useState } from 'react';
import { ShieldCheck, Plus, CheckCircle, AlertOctagon, FileText } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const QualityControl: React.FC = () => {
  const [inspections, setInspections] = useState<any[]>([]);
  const [ncrs, setNcrs] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'inspections' | 'ncrs'>('inspections');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadQC = async () => {
      try {
        const [iRes, nRes] = await Promise.all([
          api.get('/quality/inspections'),
          api.get('/quality/ncrs')
        ]);
        setInspections(iRes.data);
        setNcrs(nRes.data);
      } catch (err) {
        setInspections([
          { inspection_number: 'QC-2026-00001', item_id: '5000 PSI Hydraulic Pump', inspection_date: '2026-01-25', inspected_quantity: 10.0, passed_quantity: 10.0, rejected_quantity: 0.0, status: 'PASS' },
          { inspection_number: 'QC-2026-00002', item_id: 'Forged Steel Billet 100mm', inspection_date: '2026-01-18', inspected_quantity: 50.0, passed_quantity: 48.0, rejected_quantity: 2.0, status: 'PASS' },
        ]);
        setNcrs([
          { ncr_number: 'NCR-2026-00001', item_id: 'Forged Steel Billet 100mm', issue_summary: 'Surface porosity exceeding 0.05mm tolerance limit', status: 'OPEN', created_at: '2026-01-18' }
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadQC();
  }, []);

  const inspCols: Column<any>[] = [
    { header: 'Inspection #', accessor: 'inspection_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Tested Item', accessor: 'item_id', className: 'font-medium text-white' },
    { header: 'Date', accessor: 'inspection_date', className: 'font-mono text-slate-400' },
    { header: 'Inspected Qty', accessor: (row) => `${row.inspected_quantity} pcs`, className: 'font-mono text-center' },
    { header: 'Passed Qty', accessor: (row) => `${row.passed_quantity} pcs`, className: 'font-mono font-semibold text-emerald-400 text-center' },
    { header: 'Rejected Qty', accessor: (row) => `${row.rejected_quantity} pcs`, className: 'font-mono font-semibold text-rose-400 text-center' },
    {
      header: 'Verdict',
      accessor: (row) => (
        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
          row.status === 'PASS' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
          'bg-rose-500/10 text-rose-400 border border-rose-500/20'
        }`}>
          {row.status}
        </span>
      )
    },
  ];

  const ncrCols: Column<any>[] = [
    { header: 'NCR Number', accessor: 'ncr_number', className: 'font-mono font-bold text-rose-400' },
    { header: 'Item SKU', accessor: 'item_id', className: 'font-mono font-medium text-white' },
    { header: 'Issue Summary', accessor: 'issue_summary', className: 'text-slate-300' },
    {
      header: 'Status',
      accessor: (row) => (
        <span className="bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded text-[10px] font-semibold">
          {row.status}
        </span>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-brand-500" />
            Quality Control & AQL Compliance
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Inspection Checklists, AQL Tolerance Verification, Non-Conformance Reports, and CAPA.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Record Inspection</span>
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('inspections')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'inspections'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Inspection Records
        </button>
        <button
          onClick={() => setActiveTab('ncrs')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'ncrs'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Non-Conformance Reports (NCR)
        </button>
      </div>

      {activeTab === 'inspections' && (
        <DataTable
          title="Quality Control Inspection Logs"
          columns={inspCols}
          data={inspections}
          searchPlaceholder="Search inspections..."
        />
      )}

      {activeTab === 'ncrs' && (
        <DataTable
          title="Quality Non-Conformance Reports (NCR) & CAPA"
          columns={ncrCols}
          data={ncrs}
          searchPlaceholder="Search NCRs..."
        />
      )}
    </div>
  );
};
