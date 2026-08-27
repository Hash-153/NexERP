import React, { useEffect, useState } from 'react';
import { FileSpreadsheet, Plus, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const AccountsReceivable: React.FC = () => {
  const [customers, setCustomers] = useState<any[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'invoices' | 'customers'>('invoices');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAR = async () => {
      try {
        const [cRes, iRes] = await Promise.all([
          api.get('/accounts-receivable/customers'),
          api.get('/accounts-receivable/invoices')
        ]);
        setCustomers(cRes.data);
        setInvoices(iRes.data);
      } catch (err) {
        setCustomers([
          { customer_number: 'CUST-001', name: 'Continental Petrochemical Refining Corp', payment_terms_days: 30, credit_limit: 250000.0, current_balance: 34698.0, email: 'procurement@continentalrefining.com' },
          { customer_number: 'CUST-002', name: 'Apex Marine & Heavy Offshore Engineering', payment_terms_days: 45, credit_limit: 500000.0, current_balance: 0.0, email: 'ap@apexmarineoffshore.com' },
        ]);
        setInvoices([
          { invoice_number: 'INV-2026-00001', customer_id: 'CUST-001', invoice_date: '2026-01-15', due_date: '2026-02-14', total_amount: 34698.0, balance_due: 34698.0, status: 'POSTED' },
          { invoice_number: 'INV-2026-00002', customer_id: 'CUST-002', invoice_date: '2026-02-01', due_date: '2026-03-18', total_amount: 64000.0, balance_due: 64000.0, status: 'POSTED' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadAR();
  }, []);

  const customerCols: Column<any>[] = [
    { header: 'Customer Code', accessor: 'customer_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Customer Name', accessor: 'name', className: 'font-medium text-white' },
    { header: 'Email', accessor: 'email', className: 'text-slate-400' },
    {
      header: 'Credit Limit',
      accessor: (row) => `$${row.credit_limit.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono text-slate-300',
    },
    {
      header: 'Receivable Balance',
      accessor: (row) => `$${row.current_balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-emerald-400 text-right',
    },
  ];

  const invoiceCols: Column<any>[] = [
    { header: 'Invoice #', accessor: 'invoice_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Date', accessor: 'invoice_date', className: 'font-mono text-slate-400' },
    { header: 'Due Date', accessor: 'due_date', className: 'font-mono text-slate-400' },
    {
      header: 'Status',
      accessor: (row) => (
        <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-semibold">
          {row.status}
        </span>
      )
    },
    {
      header: 'Total Amount',
      accessor: (row) => `$${row.total_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
    {
      header: 'Balance Due',
      accessor: (row) => `$${row.balance_due.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-emerald-400 text-right',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <FileSpreadsheet className="w-6 h-6 text-brand-500" />
            Accounts Receivable & DSO
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Customer Credit Profiles, Commercial Invoices, Receipt Allocations, and Automated Dunning.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Create Sales Invoice</span>
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('invoices')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'invoices'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Customer Invoices
        </button>
        <button
          onClick={() => setActiveTab('customers')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'customers'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Customer Master & Aging
        </button>
      </div>

      {activeTab === 'invoices' && (
        <DataTable
          title="Issued Commercial Invoices"
          columns={invoiceCols}
          data={invoices}
          searchPlaceholder="Search invoices..."
        />
      )}

      {activeTab === 'customers' && (
        <DataTable
          title="Customer Credit & Outstanding Ledger"
          columns={customerCols}
          data={customers}
          searchPlaceholder="Search customers..."
        />
      )}
    </div>
  );
};
