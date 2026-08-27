import React, { useState } from 'react';
import { Tag, DollarSign, Users, TrendingUp, Check, Percent } from 'lucide-react';

export const PricingCalculatorPage: React.FC = () => {
  const [quantity, setQuantity] = useState<number>(25);
  const [customerTier, setCustomerTier] = useState<'STANDARD' | 'SILVER' | 'GOLD' | 'PLATINUM'>('GOLD');
  const baseListPrice = 120.0;

  const volumeBreaks = [
    { minQty: 1, discount: 0, label: '1 - 9 Units (Base)' },
    { minQty: 10, discount: 10, label: '10 - 49 Units (10% Off)' },
    { minQty: 50, discount: 20, label: '50 - 99 Units (20% Off)' },
    { minQty: 100, discount: 30, label: '100+ Units (30% Off)' },
  ];

  const tierDiscounts = {
    STANDARD: 0,
    SILVER: 5,
    GOLD: 10,
    PLATINUM: 15,
  };

  // Determine volume discount
  let volumeDiscountPct = 0;
  for (let i = volumeBreaks.length - 1; i >= 0; i--) {
    if (quantity >= volumeBreaks[i].minQty) {
      volumeDiscountPct = volumeBreaks[i].discount;
      break;
    }
  }

  const tierDiscountPct = tierDiscounts[customerTier];
  const combinedDiscountPct = Math.min(45, volumeDiscountPct + tierDiscountPct);
  const effectiveUnitPrice = baseListPrice * (1 - combinedDiscountPct / 100);
  const totalOrderAmount = effectiveUnitPrice * quantity;
  const totalSavings = (baseListPrice * quantity) - totalOrderAmount;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Commercial Pricing & Tier Discount Engine</h1>
          <p className="text-sm text-slate-500">Simulate customer volume pricing matrices, loyalty tier discounts, and gross margin contribution.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: Input Parameters */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-4">
          <h3 className="font-semibold text-slate-900 dark:text-white text-sm flex items-center gap-2">
            <Tag className="w-4 h-4 text-indigo-600" /> Order Parameters
          </h3>

          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Base List Price (USD)</label>
            <div className="p-2.5 bg-slate-50 dark:bg-slate-900 rounded-lg font-mono font-bold text-slate-900 dark:text-white">
              ${baseListPrice.toFixed(2)}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Order Quantity</label>
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-full p-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-semibold"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Customer Partner Tier</label>
            <div className="grid grid-cols-2 gap-2">
              {(['STANDARD', 'SILVER', 'GOLD', 'PLATINUM'] as const).map((tier) => (
                <button
                  key={tier}
                  onClick={() => setCustomerTier(tier)}
                  className={`p-2 rounded-lg text-xs font-bold border transition ${customerTier === tier ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400' : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'}`}
                >
                  {tier} (+{tierDiscounts[tier]}%)
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Calculated Price Summary */}
        <div className="md:col-span-2 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-xs text-slate-500 font-medium">Effective Unit Price</span>
              <p className="text-2xl font-black text-slate-900 dark:text-white mt-1">${effectiveUnitPrice.toFixed(2)}</p>
              <span className="text-xs text-emerald-600 font-semibold">{combinedDiscountPct}% Total Discount</span>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-xs text-slate-500 font-medium">Total Order Value</span>
              <p className="text-2xl font-black text-indigo-600 mt-1">${totalOrderAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
              <span className="text-xs text-slate-500 font-mono">{quantity} Units</span>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-xs text-slate-500 font-medium">Customer Savings</span>
              <p className="text-2xl font-black text-emerald-600 mt-1">${totalSavings.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
              <span className="text-xs text-slate-500 font-medium">vs List Price</span>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Volume Discount Tier Matrix</h4>
            <div className="divide-y divide-slate-100 dark:divide-slate-700 text-xs">
              {volumeBreaks.map((vb, idx) => (
                <div key={idx} className="py-2.5 flex justify-between items-center">
                  <span className="text-slate-700 dark:text-slate-300 font-medium">{vb.label}</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-white">
                    ${(baseListPrice * (1 - (vb.discount + tierDiscountPct) / 100)).toFixed(2)} / unit
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
