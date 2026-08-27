import React, { useEffect, useState } from 'react';
import { TrendingUp, Plus, UserPlus, ShoppingBag, Send } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const Sales: React.FC = () => {
  const [salesOrders, setSalesOrders] = useState<any[]>([]);
  const [leads, setLeads] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'orders' | 'leads'>('orders');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSales = async () => {
      try {
        const [soRes, lRes] = await Promise.all([
          api.get('/sales/orders'),
          api.get('/sales/leads')
        ]);
        setSalesOrders(soRes.data);
        setLeads(lRes.data);
      } catch (err) {
        setSalesOrders([
          { so_number: 'SO-2026-00001', customer_id: 'Continental Petrochemical', order_date: '2026-01-15', requested_delivery_date: '2026-02-14', total_amount: 32000.0, status: 'CONFIRMED' },
          { so_number: 'SO-2026-00002', customer_id: 'Apex Marine Offshore', order_date: '2026-01-20', requested_delivery_date: '2026-02-28', total_amount: 64000.0, status: 'PROCESSING' },
        ]);
        setLeads([
          { lead_number: 'LEAD-001', company_name: 'Gulf Coast Drilling Solutions', contact_person: 'Robert Chen', estimated_value: 120000.0, stage: 'QUALIFIED' },
          { lead_number: 'LEAD-002', company_name: 'Nordic Offshore Systems', contact_person: 'Astrid Lindqvist', estimated_value: 250000.0, stage: 'PROPOSAL_SENT' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadSales();
  }, []);

  const soCols: Column<any>[] = [
    { header: 'Order Number', accessor: 'so_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Customer', accessor: 'customer_id', className: 'font-medium text-white' },
    { header: 'Order Date', accessor: 'order_date', className: 'font-mono text-slate-400' },
    { header: 'Requested Delivery', accessor: 'requested_delivery_date', className: 'font-mono text-slate-400' },
    {
      header: 'Status',
      accessor: (row) => (
        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
          row.status === 'CONFIRMED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
          'bg-sky-500/10 text-sky-400 border border-sky-500/20'
        }`}>
          {row.status}
        </span>
      )
    },
    {
      header: 'Order Value',
      accessor: (row) => `$${row.total_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-emerald-400 text-right',
    },
  ];

  const leadCols: Column<any>[] = [
    { header: 'Lead Code', accessor: 'lead_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Company', accessor: 'company_name', className: 'font-medium text-white' },
    { header: 'Contact Person', accessor: 'contact_person', className: 'text-slate-300' },
    {
      header: 'Pipeline Stage',
      accessor: (row) => (
        <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2 py-0.5 rounded text-[10px] font-semibold">
          {row.stage}
        </span>
      )
    },
    {
      header: 'Est. Opportunity Value',
      accessor: (row) => `$${row.estimated_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-brand-500" />
            Sales & CRM Pipeline
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            CRM Leads, Sales Quotations, Customer Orders, Inventory Allocation, and Dispatch.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Create Sales Order</span>
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('orders')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'orders'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Customer Sales Orders
        </button>
        <button
          onClick={() => setActiveTab('leads')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'leads'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          CRM Opportunity Pipeline
        </button>
      </div>

      {activeTab === 'orders' && (
        <DataTable
          title="Customer Sales Order Backlog"
          columns={soCols}
          data={salesOrders}
          searchPlaceholder="Search orders..."
        />
      )}

      {activeTab === 'leads' && (
        <DataTable
          title="Active CRM Sales Opportunities"
          columns={leadCols}
          data={leads}
          searchPlaceholder="Search leads..."
        />
      )}
    </div>
  );
};
