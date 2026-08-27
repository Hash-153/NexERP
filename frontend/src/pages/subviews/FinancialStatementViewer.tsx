import React, { useState } from 'react';

export function FinancialStatementViewer() {
  const [statementType, setStatementType] = useState<'PL' | 'BS'>('PL');

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">GAAP / IFRS Multi-Period Financial Statements</h2>
          <p className="text-sm text-slate-500">Audited multi-currency general ledger statement rollups with drill-down line items</p>
        </div>
        <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
          <button
            onClick={() => setStatementType('PL')}
            className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-colors ${statementType === 'PL' ? 'bg-white dark:bg-slate-900 shadow-sm text-blue-600' : 'text-slate-600'}`}
          >
            Income Statement (P&amp;L)
          </button>
          <button
            onClick={() => setStatementType('BS')}
            className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-colors ${statementType === 'BS' ? 'bg-white dark:bg-slate-900 shadow-sm text-blue-600' : 'text-slate-600'}`}
          >
            Classified Balance Sheet
          </button>
        </div>
      </div>

      {statementType === 'PL' ? (
        <div className="space-y-4 text-sm font-sans">
          <div className="border-b border-slate-200 dark:border-slate-800 pb-2">
            <h4 className="font-bold text-slate-900 dark:text-white text-base mb-2">Revenues</h4>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">40100 - Enterprise Software Subscriptions</span>
              <span className="font-mono font-semibold">$4,850,000.00</span>
            </div>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">40200 - Professional Implementation Services</span>
              <span className="font-mono font-semibold">$1,250,000.00</span>
            </div>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">40300 - Managed Maintenance &amp; Support</span>
              <span className="font-mono font-semibold">$620,000.00</span>
            </div>
            <div className="flex justify-between py-2 border-t border-slate-200 dark:border-slate-800 font-bold text-slate-900 dark:text-white">
              <span>Total Gross Revenue</span>
              <span className="font-mono">$6,720,000.00</span>
            </div>
          </div>

          <div className="border-b border-slate-200 dark:border-slate-800 pb-2">
            <h4 className="font-bold text-slate-900 dark:text-white text-base mb-2">Cost of Goods Sold (COGS)</h4>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">50100 - Cloud Datacenter &amp; Hosting</span>
              <span className="font-mono font-semibold">$680,000.00</span>
            </div>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">50200 - Customer Success Direct Delivery</span>
              <span className="font-mono font-semibold">$450,000.00</span>
            </div>
            <div className="flex justify-between py-2 border-t border-slate-200 dark:border-slate-800 font-bold text-slate-900 dark:text-white">
              <span>Total Cost of Goods Sold</span>
              <span className="font-mono">$1,130,000.00</span>
            </div>
            <div className="flex justify-between py-2 bg-slate-50 dark:bg-slate-800/60 px-3 rounded font-bold text-emerald-600 dark:text-emerald-400">
              <span>Gross Profit (Margin: 83.18%)</span>
              <span className="font-mono">$5,590,000.00</span>
            </div>
          </div>

          <div className="border-b border-slate-200 dark:border-slate-800 pb-2">
            <h4 className="font-bold text-slate-900 dark:text-white text-base mb-2">Operating Expenses (OPEX)</h4>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">60100 - Research &amp; Development Engineering</span>
              <span className="font-mono font-semibold">$1,850,000.00</span>
            </div>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">60200 - Sales &amp; Marketing Execution</span>
              <span className="font-mono font-semibold">$950,000.00</span>
            </div>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">60300 - General &amp; Administrative</span>
              <span className="font-mono font-semibold">$420,000.00</span>
            </div>
            <div className="flex justify-between py-2 border-t border-slate-200 dark:border-slate-800 font-bold text-slate-900 dark:text-white">
              <span>Total Operating Expenses</span>
              <span className="font-mono">$3,220,000.00</span>
            </div>
          </div>

          <div className="flex justify-between p-4 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 rounded-lg font-black text-blue-900 dark:text-blue-100 text-lg">
            <span>Net Operating Income (EBIT)</span>
            <span className="font-mono">$2,370,000.00</span>
          </div>
        </div>
      ) : (
        <div className="space-y-4 text-sm font-sans">
          <div className="border-b border-slate-200 dark:border-slate-800 pb-2">
            <h4 className="font-bold text-slate-900 dark:text-white text-base mb-2">Total Assets</h4>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">Current Assets (Cash, AR, Inventory)</span>
              <span className="font-mono font-semibold">$7,555,000.00</span>
            </div>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">Property, Plant &amp; Equipment (Net)</span>
              <span className="font-mono font-semibold">$6,300,000.00</span>
            </div>
            <div className="flex justify-between py-2 border-t border-slate-200 dark:border-slate-800 font-bold text-slate-900 dark:text-white">
              <span>Total Consolidated Assets</span>
              <span className="font-mono text-emerald-600 dark:text-emerald-400">$13,855,000.00</span>
            </div>
          </div>

          <div className="border-b border-slate-200 dark:border-slate-800 pb-2">
            <h4 className="font-bold text-slate-900 dark:text-white text-base mb-2">Total Liabilities &amp; Stockholders' Equity</h4>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">Current Liabilities (AP, Accruals, Deferred Rev)</span>
              <span className="font-mono font-semibold">$5,480,000.00</span>
            </div>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">Long-Term Senior Debt &amp; Lease Liabilities</span>
              <span className="font-mono font-semibold">$5,750,000.00</span>
            </div>
            <div className="flex justify-between py-1.5 text-slate-700 dark:text-slate-300">
              <span className="pl-4">Total Stockholders' Equity</span>
              <span className="font-mono font-semibold">$2,625,000.00</span>
            </div>
            <div className="flex justify-between py-2 border-t border-slate-200 dark:border-slate-800 font-bold text-slate-900 dark:text-white">
              <span>Total Liabilities &amp; Equity</span>
              <span className="font-mono text-emerald-600 dark:text-emerald-400">$13,855,000.00</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
