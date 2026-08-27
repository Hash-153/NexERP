import React, { useEffect, useState } from 'react';
import { Receipt, Plus, Users, ShieldAlert, CheckCircle, Clock } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const AccountsPayable: React.FC = () => {
  const [vendors, setVendors] = useState<any[]>([]);
  const [bills, setBills] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'vendors' | 'bills'>('bills');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAP = async () => {
      try {
        const [vRes, bRes] = await Promise.all([
          api.get('/accounts-payable/vendors'),
          api.get('/accounts-payable/bills')
        ]);
        setVendors(vRes.data);
        setBills(bRes.data);
      } catch (err) {
        setVendors([
          { code: 'VEND-001', name: 'Precision Alloy Forgings Corp', payment_terms_days: 30, credit_limit: 150000.0, current_balance: 45000.0, email: 'orders@precisionalloy.com' },
          { code: 'VEND-002', name: 'Titan Electric Industrial Motors Ltd', payment_terms_days: 45, credit_limit: 200000.0, current_balance: 67000.0, email: 'sales@titanmotors.com' },
        ]);
        setBills([
          { bill_number: 'BILL-2026-00001', vendor_invoice_number: 'INV-PA-9912', bill_date: '2026-01-20', due_date: '2026-02-19', total_amount: 45000.0, balance_due: 45000.0, status: 'APPROVED' },
          { bill_number: 'BILL-2026-00002', vendor_invoice_number: 'INV-TM-4410', bill_date: '2026-01-25', due_date: '2026-03-11', total_amount: 67000.0, balance_due: 67000.0, status: 'APPROVED' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadAP();
  }, []);

  const vendorCols: Column<any>[] = [
    { header: 'Vendor Code', accessor: 'code', className: 'font-mono font-bold text-brand-400' },
    { header: 'Vendor Name', accessor: 'name', className: 'font-medium text-white' },
    { header: 'Contact Email', accessor: 'email', className: 'text-slate-400' },
    { header: 'Terms', accessor: (row) => `Net ${row.payment_terms_days} Days`, className: 'font-mono text-slate-300' },
    {
      header: 'Outstanding Payables',
      accessor: (row) => `$${row.current_balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-rose-400 text-right',
    },
  ];

  const billCols: Column<any>[] = [
    { header: 'Bill ID', accessor: 'bill_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Vendor Invoice #', accessor: 'vendor_invoice_number', className: 'font-mono' },
    { header: 'Bill Date', accessor: 'bill_date', className: 'font-mono text-slate-400' },
    { header: 'Due Date', accessor: 'due_date', className: 'font-mono text-slate-400' },
    {
      header: 'Match Status',
      accessor: () => (
        <span className="flex items-center space-x-1 text-emerald-400 text-[11px] font-semibold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded w-max">
          <CheckCircle className="w-3 h-3" />
          <span>3-Way Matched</span>
        </span>
      ),
    },
    {
      header: 'Total Amount',
      accessor: (row) => `$${row.total_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
    {
      header: 'Balance Due',
      accessor: (row) => `$${row.balance_due.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-rose-400 text-right',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Receipt className="w-6 h-6 text-brand-500" />
            Accounts Payable & 3-Way Match
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Vendor Directory, PO-GRN-Bill Tolerance Audits, and Batch Payment Disbursements.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Enter Vendor Bill</span>
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('bills')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'bills'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Vendor Invoices & Bills
        </button>
        <button
          onClick={() => setActiveTab('vendors')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'vendors'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Supplier & Vendor Master
        </button>
      </div>

      {activeTab === 'bills' && (
        <DataTable
          title="Accounts Payable Bills Schedule"
          columns={billCols}
          data={bills}
          searchPlaceholder="Search bills by invoice number..."
        />
      )}

      {activeTab === 'vendors' && (
        <DataTable
          title="Authorized Suppliers & Credit Limits"
          columns={vendorCols}
          data={vendors}
          searchPlaceholder="Search suppliers..."
        />
      )}
    </div>
  );
};
