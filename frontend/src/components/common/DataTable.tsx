import React, { useState } from 'react';
import { Search, Download, ChevronLeft, ChevronRight } from 'lucide-react';

export interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
  className?: string;
}

interface DataTableProps<T> {
  title?: string;
  columns: Column<T>[];
  data: T[];
  searchPlaceholder?: string;
  onExportCsv?: () => void;
  pageSize?: number;
}

export function DataTable<T extends Record<string, any>>({
  title,
  columns,
  data,
  searchPlaceholder = 'Search records...',
  onExportCsv,
  pageSize = 10,
}: DataTableProps<T>) {
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // Filter Data
  const filteredData = data.filter((row) => {
    if (!search) return true;
    return Object.values(row).some((val) =>
      String(val).toLowerCase().includes(search.toLowerCase())
    );
  });

  const totalPages = Math.ceil(filteredData.length / pageSize) || 1;
  const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
      {/* Header controls */}
      <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {title && <h3 className="text-base font-semibold text-white">{title}</h3>}
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              placeholder={searchPlaceholder}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-brand-500"
            />
          </div>
          {onExportCsv && (
            <button
              onClick={onExportCsv}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 rounded-lg transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export</span>
            </button>
          )}
        </div>
      </div>

      {/* Table view */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800 font-semibold uppercase tracking-wider text-[11px]">
            <tr>
              {columns.map((col, idx) => (
                <th key={idx} className={`py-3 px-4 ${col.className || ''}`}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="text-center py-8 text-slate-400">
                  No records found.
                </td>
              </tr>
            ) : (
              paginatedData.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-slate-800/30 transition-colors">
                  {columns.map((col, cIdx) => (
                    <td key={cIdx} className={`py-3 px-4 ${col.className || ''}`}>
                      {typeof col.accessor === 'function'
                        ? col.accessor(row)
                        : (row[col.accessor] as React.ReactNode)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/40 flex items-center justify-between text-xs text-slate-400">
        <span>
          Showing <span className="font-mono text-slate-200">{filteredData.length === 0 ? 0 : (currentPage - 1) * pageSize + 1}</span> to{' '}
          <span className="font-mono text-slate-200">{Math.min(currentPage * pageSize, filteredData.length)}</span> of{' '}
          <span className="font-mono text-slate-200">{filteredData.length}</span> results
        </span>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="px-2 font-mono">
            {currentPage} / {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
