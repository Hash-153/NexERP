import React, { useState } from 'react';

interface BinSlot {
  aisle: string;
  bay: string;
  shelf: string;
  bin: string;
  sku: string;
  velocity: 'A' | 'B' | 'C';
  picksPerDay: number;
  capacityPct: number;
}

export function SlottingHeatmapVisualizer() {
  const [selectedAisle, setSelectedAisle] = useState('Aisle-01');

  const slots: BinSlot[] = [
    { aisle: 'Aisle-01', bay: '01', shelf: '1', bin: 'A', sku: 'SKU-TITANIUM-ROTOR', velocity: 'A', picksPerDay: 142, capacityPct: 92 },
    { aisle: 'Aisle-01', bay: '01', shelf: '2', bin: 'B', sku: 'SKU-FASTENER-HEX-M8', velocity: 'A', picksPerDay: 185, capacityPct: 84 },
    { aisle: 'Aisle-01', bay: '01', shelf: '3', bin: 'C', sku: 'SKU-GASKET-SEAL-EPDM', velocity: 'B', picksPerDay: 48, capacityPct: 65 },
    { aisle: 'Aisle-01', bay: '01', shelf: '4', bin: 'D', sku: 'SKU-HYDRAULIC-VALVE-50', velocity: 'C', picksPerDay: 12, capacityPct: 40 },
    { aisle: 'Aisle-01', bay: '02', shelf: '1', bin: 'A', sku: 'SKU-CONTROL-PCB-ARM', velocity: 'A', picksPerDay: 210, capacityPct: 95 },
    { aisle: 'Aisle-01', bay: '02', shelf: '2', bin: 'B', sku: 'SKU-STEPPER-MOTOR-24V', velocity: 'A', picksPerDay: 160, capacityPct: 88 },
    { aisle: 'Aisle-01', bay: '02', shelf: '3', bin: 'C', sku: 'SKU-POWER-SUPPLY-500W', velocity: 'B', picksPerDay: 54, capacityPct: 70 },
    { aisle: 'Aisle-01', bay: '02', shelf: '4', bin: 'D', sku: 'SKU-HEAVY-CAST-HOUSING', velocity: 'C', picksPerDay: 8, capacityPct: 35 },
  ];

  const getColorByVelocity = (v: string) => {
    switch (v) {
      case 'A': return 'bg-rose-500 text-white border-rose-600 hover:bg-rose-600';
      case 'B': return 'bg-amber-500 text-white border-amber-600 hover:bg-amber-600';
      default: return 'bg-blue-500 text-white border-blue-600 hover:bg-blue-600';
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">Warehouse 3D Slotting Velocity Heatmap</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">Ergonomic ground reach slotting: Red (High Fast Pick), Amber (Medium), Blue (Slow Bulk)</p>
        </div>
        <select
          value={selectedAisle}
          onChange={e => setSelectedAisle(e.target.value)}
          className="px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-semibold"
        >
          <option value="Aisle-01">Aisle 01 (Fast Pick Face)</option>
          <option value="Aisle-02">Aisle 02 (Sub-Assembly)</option>
          <option value="Aisle-03">Aisle 03 (Heavy Raw Materials)</option>
        </select>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
        {slots.map((slot, idx) => (
          <div
            key={idx}
            className={`border rounded-xl p-4 transition-all cursor-pointer shadow-sm ${getColorByVelocity(slot.velocity)}`}
          >
            <div className="flex justify-between items-center text-xs font-mono font-bold opacity-90 mb-1">
              <span>{slot.aisle}-{slot.bay}-{slot.shelf}{slot.bin}</span>
              <span className="px-1.5 py-0.5 rounded bg-black/20 text-[10px]">Class {slot.velocity}</span>
            </div>
            <div className="font-bold text-sm truncate my-1">{slot.sku}</div>
            <div className="flex justify-between text-xs mt-3 pt-2 border-t border-white/20">
              <span>{slot.picksPerDay} picks/day</span>
              <span>{slot.capacityPct}% full</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
