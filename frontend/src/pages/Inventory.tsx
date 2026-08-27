import React, { useEffect, useState } from 'react';
import { Boxes, Plus, Warehouse, Layers, ArrowUpDown } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const Inventory: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadInventory = async () => {
      try {
        const res = await api.get('/inventory/items');
        setItems(res.data);
      } catch (err) {
        setItems([
          { sku: 'HYD-PUMP-500', name: '5000 PSI Hydraulic Triplex Pump', item_type: 'FINISHED_GOOD', standard_cost: 1450.0, list_price: 3200.0, lead_time_days: 14, safety_stock: 10.0 },
          { sku: 'SUB-VALVE-BLOCK', name: 'High-Pressure Hydraulic Manifold Block', item_type: 'WORK_IN_PROGRESS', standard_cost: 420.0, list_price: 850.0, lead_time_days: 7, safety_stock: 20.0 },
          { sku: 'RM-STEEL-BILLET', name: 'Forged Alloy Steel Round Billet 100mm', item_type: 'RAW_MATERIAL', standard_cost: 110.0, list_price: 0.0, lead_time_days: 10, safety_stock: 50.0 },
          { sku: 'RM-MOTOR-15HP', name: '15 HP Three-Phase Induction Motor 460V', item_type: 'RAW_MATERIAL', standard_cost: 650.0, list_price: 0.0, lead_time_days: 14, safety_stock: 15.0 },
          { sku: 'RM-SEAL-KIT', name: 'Viton High-Temperature O-Ring Seal Kit', item_type: 'RAW_MATERIAL', standard_cost: 35.0, list_price: 0.0, lead_time_days: 5, safety_stock: 100.0 },
          { sku: 'RM-CERAMIC-PLUNGER', name: 'Solid Ceramic Plunger 28mm', item_type: 'RAW_MATERIAL', standard_cost: 45.0, list_price: 0.0, lead_time_days: 12, safety_stock: 60.0 },
          { sku: 'RM-FASTENER-M12', name: 'Grade 12.9 High-Tensile Socket Screws M12', item_type: 'RAW_MATERIAL', standard_cost: 2.5, list_price: 0.0, lead_time_days: 3, safety_stock: 500.0 },
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadInventory();
  }, []);

  const itemCols: Column<any>[] = [
    { header: 'SKU Code', accessor: 'sku', className: 'font-mono font-bold text-brand-400' },
    { header: 'Item Name', accessor: 'name', className: 'font-medium text-white' },
    {
      header: 'Category Type',
      accessor: (row) => (
        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
          row.item_type === 'FINISHED_GOOD' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
          row.item_type === 'WORK_IN_PROGRESS' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
          'bg-sky-500/10 text-sky-400 border border-sky-500/20'
        }`}>
          {row.item_type}
        </span>
      )
    },
    {
      header: 'Unit Cost (FIFO)',
      accessor: (row) => `$${row.standard_cost.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono text-slate-300 text-right',
    },
    {
      header: 'List Price',
      accessor: (row) => `$${row.list_price.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
    {
      header: 'Lead Time',
      accessor: (row) => `${row.lead_time_days} days`,
      className: 'font-mono text-slate-400 text-center',
    },
    {
      header: 'Safety Stock',
      accessor: (row) => `${row.safety_stock} units`,
      className: 'font-mono font-semibold text-brand-400 text-center',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Boxes className="w-6 h-6 text-brand-500" />
            Inventory & Warehouse WMS
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Item Master Catalog, Multi-Location Bin Tracking, FIFO Valuation Layers, and Physical Audits.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Create Item</span>
          </button>
        </div>
      </div>

      <DataTable
        title="Enterprise Item Master & Costing Catalog"
        columns={itemCols}
        data={items}
        searchPlaceholder="Search catalog by SKU or item name..."
      />
    </div>
  );
};
