import React, { useState } from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface BankAccountItem {
  id: string;
  account_number: string;
  bank_name: string;
  currency: string;
  cleared_balance: number;
  ledger_balance: number;
  account_type: string;
}

export function TreasuryManagement() {
  const [activeTab, setActiveTab] = useState<'ACCOUNTS' | 'FORECAST' | 'FX_HEDGING'>('ACCOUNTS');

  const kpis: KPICardData[] = [
    { title: 'Total Liquid Treasury', value: '$12,450,800', change: '+8.4%', isPositive: true, icon: '🏦', subtitle: 'Across 6 corporate bank accounts' },
    { title: 'Projected 90D Cash Inflow', value: '$18,200,000', change: '+12.1%', isPositive: true, icon: '📈', subtitle: 'AR collections + contracts' },
    { title: 'Expected 90D Cash Outflow', value: '$14,150,000', change: '-3.2%', isPositive: false, icon: '📉', subtitle: 'AP + Payroll + CAPEX' },
    { title: 'Mark-to-Market FX Hedges', value: '+$142,500', change: '+5.5%', isPositive: true, icon: '💱', subtitle: 'EUR/USD & GBP/USD forward cover' },
  ];

  const accounts: BankAccountItem[] = [
    { id: '1', account_number: '•••• 4920', bank_name: 'JPMorgan Chase NY', currency: 'USD', cleared_balance: 6250000, ledger_balance: 6250000, account_type: 'OPERATING_CHECKING' },
    { id: '2', account_number: '•••• 8831', bank_name: 'Barclays London Corporate', currency: 'GBP', cleared_balance: 2150000, ledger_balance: 2150000, account_type: 'EURO_SWEEP' },
    { id: '3', account_number: '•••• 1044', bank_name: 'Deutsche Bank Frankfurt', currency: 'EUR', cleared_balance: 3400000, ledger_balance: 3400000, account_type: 'PRIMARY_CHECKING' },
    { id: '4', account_number: '•••• 7712', bank_name: 'BNP Paribas Paris', currency: 'EUR', cleared_balance: 650800, ledger_balance: 650800, account_type: 'TAX_ESCROW' },
  ];

  const columns: ColumnDef<BankAccountItem>[] = [
    { key: 'bank_name', header: 'Bank / Institution', width: '30%' },
    { key: 'account_number', header: 'Account Number', width: '20%' },
    { key: 'account_type', header: 'Type', width: '20%', render: a => <span className="px-2 py-0.5 text-xs rounded bg-slate-100 dark:bg-slate-800 font-mono">{a.account_type}</span> },
    { key: 'currency', header: 'Currency', width: '10%', align: 'center' },
    { key: 'cleared_balance', header: 'Cleared Balance', width: '20%', align: 'right', render: a => <span className="font-bold text-slate-900 dark:text-white">${a.cleared_balance.toLocaleString()} {a.currency}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Treasury & Cash Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Intraday liquidity positioning, automated multi-currency sweeps, and IFRS 9 hedge accounting</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
            ⚡ Execute Cash Sweep
          </button>
          <button className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-semibold transition-colors">
            📥 Import CAMT.053
          </button>
        </div>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <div className="flex border-b border-slate-200 dark:border-slate-800 gap-6 text-sm font-medium">
        <button
          onClick={() => setActiveTab('ACCOUNTS')}
          className={`pb-3 transition-colors ${activeTab === 'ACCOUNTS' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-slate-500 hover:text-slate-800'}`}
        >
          Bank Accounts & Cleared Balances
        </button>
        <button
          onClick={() => setActiveTab('FORECAST')}
          className={`pb-3 transition-colors ${activeTab === 'FORECAST' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-slate-500 hover:text-slate-800'}`}
        >
          90-Day Liquidity Forecast
        </button>
        <button
          onClick={() => setActiveTab('FX_HEDGING')}
          className={`pb-3 transition-colors ${activeTab === 'FX_HEDGING' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-slate-500 hover:text-slate-800'}`}
        >
          FX Derivatives & Hedging
        </button>
      </div>

      <AdvancedDataGrid
        title="Corporate Bank Accounts Register"
        subtitle="Real-time multi-tenant bank feeds synchronized via SWIFT MT940 / CAMT.053"
        columns={columns}
        data={accounts}
      />
    </div>
  );
}
