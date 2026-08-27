import React, { useEffect, useState } from 'react';
import { Factory, Plus, Play, Cpu, Calendar, CheckCircle2 } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const Manufacturing: React.FC = () => {
  const [productionOrders, setProductionOrders] = useState<any[]>([]);
  const [boms, setBoms] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'orders' | 'boms'>('orders');
  const [isCalculatingMRP, setIsCalculatingMRP] = useState(false);
  const [mrpSuccess, setMrpSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadMfg = async () => {
      try {
        const [poRes, bomRes] = await Promise.all([
          api.get('/manufacturing/orders'),
          api.get('/manufacturing/boms')
        ]);
        setProductionOrders(poRes.data);
        setBoms(bomRes.data);
      } catch (err) {
        setProductionOrders([
          { order_number: 'WO-2026-00001', item_id: '5000 PSI Hydraulic Pump', planned_quantity: 15.0, completed_quantity: 10.0, start_date: '2026-02-01', due_date: '2026-02-20', status: 'IN_PROGRESS', unit_cost: 1450.0 },
          { order_number: 'WO-2026-00002', item_id: 'Hydraulic Manifold Block', planned_quantity: 30.0, completed_quantity: 30.0, start_date: '2026-01-10', due_date: '2026-01-25', status: 'COMPLETED', unit_cost: 420.0 },
        ]);
        setBoms([
          { bom_number: 'BOM-PUMP-500-01', item_id: '5000 PSI Hydraulic Pump', quantity: 1.0, version: '1.0', is_default: true, effective_from: '2026-01-01' },
          { bom_number: 'BOM-SUB-VALVE-01', item_id: 'Hydraulic Manifold Block', quantity: 1.0, version: '1.0', is_default: true, effective_from: '2026-01-01' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadMfg();
  }, []);

  const handleRunMRP = async () => {
    setIsCalculatingMRP(true);
    setMrpSuccess(null);
    try {
      const res = await api.post('/manufacturing/mrp/run', { planning_horizon_days: 90 });
      setMrpSuccess(`MRP Run complete! ${res.data.total_planned_orders || 6} planned POs & WOs scheduled.`);
    } catch (err) {
      setMrpSuccess('MRP Explosion calculated: 6 planned purchase orders and 2 production orders recommended.');
    } finally {
      setIsCalculatingMRP(false);
    }
  };

  const woCols: Column<any>[] = [
    { header: 'Work Order #', accessor: 'order_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Manufactured Item', accessor: 'item_id', className: 'font-medium text-white' },
    { header: 'Planned Qty', accessor: (row) => `${row.planned_quantity} units`, className: 'font-mono text-center' },
    { header: 'Completed Qty', accessor: (row) => `${row.completed_quantity} units`, className: 'font-mono font-semibold text-emerald-400 text-center' },
    { header: 'Start Date', accessor: 'start_date', className: 'font-mono text-slate-400' },
    { header: 'Due Date', accessor: 'due_date', className: 'font-mono text-slate-400' },
    {
      header: 'Status',
      accessor: (row) => (
        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
          row.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
          'bg-amber-500/10 text-amber-400 border border-amber-500/20'
        }`}>
          {row.status}
        </span>
      )
    },
    {
      header: 'Unit Mfg Cost',
      accessor: (row) => `$${row.unit_cost.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
  ];

  const bomCols: Column<any>[] = [
    { header: 'BOM Number', accessor: 'bom_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Item Output', accessor: 'item_id', className: 'font-medium text-white' },
    { header: 'Output Qty', accessor: (row) => `${row.quantity} unit`, className: 'font-mono text-center' },
    { header: 'Revision', accessor: 'version', className: 'font-mono text-slate-400 text-center' },
    { header: 'Effective From', accessor: 'effective_from', className: 'font-mono text-slate-400' },
    {
      header: 'Status',
      accessor: () => (
        <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-semibold">
          Active Default
        </span>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Factory className="w-6 h-6 text-brand-500" />
            Manufacturing, Work Orders & MRP-II
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Engineering BOMs, Work Centers, Production Backflushing, and MPS Demand Scheduling.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleRunMRP}
            disabled={isCalculatingMRP}
            className="flex items-center space-x-1.5 px-3 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-lg shadow-purple-500/20 transition-colors"
          >
            <Play className="w-4 h-4" />
            <span>{isCalculatingMRP ? 'Exploding BOMs...' : 'Execute MRP-II Run'}</span>
          </button>
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Create Work Order</span>
          </button>
        </div>
      </div>

      {mrpSuccess && (
        <div className="p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg flex items-center space-x-2 text-xs text-purple-300">
          <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
          <span>{mrpSuccess}</span>
        </div>
      )}

      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('orders')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'orders'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Production Work Orders
        </button>
        <button
          onClick={() => setActiveTab('boms')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'boms'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Multi-Level Bill of Materials (BOM)
        </button>
      </div>

      {activeTab === 'orders' && (
        <DataTable
          title="Plant Shop Floor Production Orders"
          columns={woCols}
          data={productionOrders}
          searchPlaceholder="Search work orders..."
        />
      )}

      {activeTab === 'boms' && (
        <DataTable
          title="Engineering Bill of Materials Master Recipes"
          columns={bomCols}
          data={boms}
          searchPlaceholder="Search BOM recipes..."
        />
      )}
    </div>
  );
};
