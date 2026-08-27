import React, { useState } from 'react';
import { Award, CheckCircle, Clock, DollarSign, ShieldAlert, Star, TrendingUp } from 'lucide-react';

export const RFQAuctionPage: React.FC = () => {
  const mockBids = [
    { rank: 1, vendor: 'Apex Precision Metals', price: 42.50, leadTime: 7, qualityRating: 98.5, score: 94.2, isWinner: true },
    { rank: 2, vendor: 'Global Component Supply', price: 39.00, leadTime: 21, qualityRating: 91.0, score: 86.8, isWinner: false },
    { rank: 3, vendor: 'Vanguard Industrial Corp', price: 48.00, leadTime: 5, qualityRating: 99.0, score: 82.1, isWinner: false },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">RFQ Sealed Bidding & Multi-Attribute Supplier Award</h1>
          <p className="text-sm text-slate-500">Multi-Attribute Decision Matrix (MADM) ranking vendor bids across weighted Price (50%), Lead Time (30%), and Quality (20%).</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium transition shadow-sm">
          <Award className="w-4 h-4" /> Convert Winner to PO
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">RFQ Reference</span>
          <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">RFQ-2026-0081</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Target Item</span>
          <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">Titanium Shaft 25mm</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Requested Quantity</span>
          <p className="text-xl font-bold text-indigo-600 mt-1">5,000 Units</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Bids Evaluated</span>
          <p className="text-xl font-bold text-emerald-600 mt-1">3 Sealed Proposals</p>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-indigo-600" /> Multi-Attribute Bid Evaluation Matrix
          </h3>
          <span className="text-xs font-mono text-slate-500">Weighting: Price 50% | Delivery 30% | Quality 20%</span>
        </div>

        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700 text-slate-500 text-xs uppercase tracking-wider">
              <th className="p-4">Rank</th>
              <th className="p-4">Vendor Partner</th>
              <th className="p-4 text-right">Bid Unit Price</th>
              <th className="p-4 text-right">Lead Time (Days)</th>
              <th className="p-4 text-right">Historical Quality</th>
              <th className="p-4 text-right">Composite Score</th>
              <th className="p-4 text-center">Award Decision</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {mockBids.map((b) => (
              <tr key={b.rank} className={`hover:bg-slate-50 dark:hover:bg-slate-700/30 ${b.isWinner ? 'bg-emerald-50/40 dark:bg-emerald-950/20' : ''}`}>
                <td className="p-4 font-bold text-slate-900 dark:text-white">#{b.rank}</td>
                <td className="p-4 font-medium text-slate-900 dark:text-white">{b.vendor}</td>
                <td className="p-4 text-right font-mono font-semibold text-slate-900 dark:text-white">${b.price.toFixed(2)}</td>
                <td className="p-4 text-right font-mono text-slate-600 dark:text-slate-400">{b.leadTime} Days</td>
                <td className="p-4 text-right font-mono text-slate-600 dark:text-slate-400">{b.qualityRating}%</td>
                <td className="p-4 text-right font-mono font-bold text-indigo-600">{b.score.toFixed(1)} / 100</td>
                <td className="p-4 text-center">
                  {b.isWinner ? (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 rounded-full text-xs font-bold">
                      <CheckCircle className="w-3.5 h-3.5" /> Awarded Winner
                    </span>
                  ) : (
                    <span className="text-xs text-slate-400">Not Awarded</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
