import React, { useState, useMemo } from 'react';

export interface ColumnDef<T> {
  key: keyof T | string;
  header: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
}

interface AdvancedDataGridProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  searchPlaceholder?: string;
  onRowClick?: (item: T) => void;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  pageSize?: number;
}

export function AdvancedDataGrid<T extends { id?: string | number }>({
  columns,
  data,
  searchPlaceholder = 'Search records...',
  onRowClick,
  title,
  subtitle,
  actions,
  pageSize = 10,
}: AdvancedDataGridProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set());

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const filteredData = useMemo(() => {
    let result = [...data];
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      result = result.filter(item =>
        Object.values(item as any).some(
          val => val !== null && val !== undefined && String(val).toLowerCase().includes(term)
        )
      );
    }
    if (sortKey) {
      result.sort((a: any, b: any) => {
        const valA = a[sortKey];
        const valB = b[sortKey];
        if (valA === valB) return 0;
        if (valA === null || valA === undefined) return 1;
        if (valB === null || valB === undefined) return -1;
        if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
        return sortDirection === 'asc' ? 1 : -1;
      });
    }
    return result;
  }, [data, searchTerm, sortKey, sortDirection]);

  const totalPages = Math.ceil(filteredData.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, currentPage, pageSize]);

  const toggleSelectAll = () => {
    if (selectedIds.size === paginatedData.length) {
      setSelectedIds(new Set());
    } else {
      const newSelected = new Set(paginatedData.map(item => item.id || Math.random()));
      setSelectedIds(newSelected);
    }
  };

  const toggleSelectItem = (id: string | number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const exportCSV = () => {
    if (!data.length) return;
    const headers = columns.map(c => c.header).join(',');
    const rows = filteredData.map(item =>
      columns.map(c => {
        const val = (item as any)[c.key];
        return typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val;
      }).join(',')
    );
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers, ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${title || 'export'}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
      {/* Header Toolbar */}
      <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          {title && <h3 className="text-lg font-bold text-slate-900 dark:text-white">{title}</h3>}
          {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[240px]">
            <input
              type="text"
              value={searchTerm}
              onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1); }}
              placeholder={searchPlaceholder}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
            />
            <span className="absolute left-3 top-2.5 text-slate-400 text-sm">🔍</span>
          </div>
          <button
            onClick={exportCSV}
            className="px-3.5 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors flex items-center gap-1.5"
          >
            📥 Export CSV
          </button>
          {actions}
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 font-semibold">
              <th className="py-3 px-4 w-10">
                <input
                  type="checkbox"
                  checked={paginatedData.length > 0 && selectedIds.size === paginatedData.length}
                  onChange={toggleSelectAll}
                  className="rounded border-slate-300 dark:border-slate-700 text-blue-600 focus:ring-blue-500"
                />
              </th>
              {columns.map(col => (
                <th
                  key={String(col.key)}
                  onClick={() => col.sortable !== false && handleSort(String(col.key))}
                  className={`py-3 px-4 select-none ${col.sortable !== false ? 'cursor-pointer hover:text-blue-600 dark:hover:text-blue-400' : ''} ${
                    col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
                  }`}
                  style={{ width: col.width }}
                >
                  <div className={`flex items-center gap-1.5 ${col.align === 'right' ? 'justify-end' : col.align === 'center' ? 'justify-center' : 'justify-start'}`}>
                    <span>{col.header}</span>
                    {sortKey === col.key && (
                      <span className="text-blue-600 dark:text-blue-400 text-xs">
                        {sortDirection === 'asc' ? '▲' : '▼'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1} className="py-12 text-center text-slate-400 dark:text-slate-500">
                  No matching records found
                </td>
              </tr>
            ) : (
              paginatedData.map((item, idx) => {
                const isSelected = selectedIds.has((item as any).id || idx);
                return (
                  <tr
                    key={(item as any).id || idx}
                    onClick={() => onRowClick && onRowClick(item)}
                    className={`hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-colors ${
                      isSelected ? 'bg-blue-50/70 dark:bg-blue-900/20' : ''
                    } ${onRowClick ? 'cursor-pointer' : ''}`}
                  >
                    <td className="py-3 px-4" onClick={e => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleSelectItem((item as any).id || idx)}
                        className="rounded border-slate-300 dark:border-slate-700 text-blue-600 focus:ring-blue-500"
                      />
                    </td>
                    {columns.map(col => (
                      <td
                        key={String(col.key)}
                        className={`py-3 px-4 text-slate-700 dark:text-slate-300 ${
                          col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
                        }`}
                      >
                        {col.render ? col.render(item) : String((item as any)[col.key] ?? '')}
                      </td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 bg-slate-50/50 dark:bg-slate-900/50">
        <div>
          Showing {filteredData.length > 0 ? (currentPage - 1) * pageSize + 1 : 0} to{' '}
          {Math.min(currentPage * pageSize, filteredData.length)} of {filteredData.length} entries
          {selectedIds.size > 0 && ` (${selectedIds.size} selected)`}
        </div>
        <div className="flex items-center gap-1.5">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            className="px-2.5 py-1.5 rounded border border-slate-200 dark:border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Previous
          </button>
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
            const page = i + 1;
            return (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`px-3 py-1.5 rounded font-medium transition-colors ${
                  currentPage === page
                    ? 'bg-blue-600 text-white'
                    : 'border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                {page}
              </button>
            );
          })}
          <button
            disabled={currentPage === totalPages || totalPages === 0}
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            className="px-2.5 py-1.5 rounded border border-slate-200 dark:border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
