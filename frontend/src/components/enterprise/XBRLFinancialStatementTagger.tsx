import React from 'react';

export function XBRLFinancialStatementTagger() {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">XBRL / iXBRL SEC EDGAR Tax Tagging Studio</h3>
          <p className="text-xs text-slate-500">Automated mapping of Chart of Accounts to US-GAAP 2026 taxonomy tags</p>
        </div>
        <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full">
          100% XBRL Tagged
        </span>
      </div>

      <div className="space-y-2 text-xs font-mono">
        <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <div>
            <span className="font-bold text-slate-900 dark:text-white">10100 - Operating Cash &amp; Cash Equivalents</span>
            <div className="text-[11px] text-slate-400">US-GAAP: CashAndCashEquivalentsAtCarryingValue</div>
          </div>
          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">TAGGED</span>
        </div>
        <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <div>
            <span className="font-bold text-slate-900 dark:text-white">10300 - Accounts Receivable (Trade Billed)</span>
            <div className="text-[11px] text-slate-400">US-GAAP: AccountsReceivableNetCurrent</div>
          </div>
          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">TAGGED</span>
        </div>
        <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <div>
            <span className="font-bold text-slate-900 dark:text-white">40100 - SaaS Software Subscriptions</span>
            <div className="text-[11px] text-slate-400">US-GAAP: RevenueFromContractWithCustomerExcludingAssessedTax</div>
          </div>
          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">TAGGED</span>
        </div>
      </div>
    </div>
  );
}
