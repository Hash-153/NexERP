import React, { useEffect, useState } from 'react';
import { Truck, Plus, PackageCheck, FileCheck, CheckCircle2 } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const Procurement: React.FC = () => {
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProcurement = async () => {
      try {
        const res = await api.get('/procurement/orders');
        setOrders(res.data);
      } catch (err) {
        setOrders([
          { po_number: 'PO-2026-00001', vendor_id: 'Precision Alloy', order_date: '2026-01-10', expected_delivery_date: '2026-01-20', total_amount: 16500.0, status: 'RECEIVED' },
          { po_number: 'PO-2026-00002', vendor_id: 'Titan Electric Motors', order_date: '2026-01-12', expected_delivery_date: '2026-01-26', total_amount: 26000.0, status: 'RECEIVED' },
          { po_number: 'PO-2026-00003', vendor_id: 'Fluid Power Seals', order_date: '2026-02-05', expected_delivery_date: '2026-02-15', total_amount: 10500.0, status: 'CONFIRMED' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadProcurement();
  }, []);

  const poCols: Column<any>[] = [
    { header: 'PO Number', accessor: 'po_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Supplier', accessor: 'vendor_id', className: 'font-medium text-white' },
    { header: 'Order Date', accessor: 'order_date', className: 'font-mono text-slate-400' },
    { header: 'Expected Delivery', accessor: 'expected_delivery_date', className: 'font-mono text-slate-400' },
    {
      header: 'Status',
      accessor: (row) => (
        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
          row.status === 'RECEIVED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
          'bg-sky-500/10 text-sky-400 border border-sky-500/20'
        }`}>
          {row.status}
        </span>
      )
    },
    {
      header: 'Order Total',
      accessor: (row) => `$${row.total_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Truck className="w-6 h-6 text-brand-500" />
            Procurement & Supply Chain Management
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Purchase Requisitions, Purchase Orders, Inbound Goods Receipts (GRN), and Supplier Scorecards.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Create Purchase Order</span>
          </button>
        </div>
      </div>

      <DataTable
        title="Purchase Orders & Supply Chain Schedule"
        columns={poCols}
        data={orders}
        searchPlaceholder="Search purchase orders..."
      />
    </div>
  );
};
