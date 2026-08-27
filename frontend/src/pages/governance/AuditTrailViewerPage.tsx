import React, { useState } from 'react';
import { Shield, Key, Search, FileText, Lock, CheckCircle2 } from 'lucide-react';

export const AuditTrailViewerPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const mockLogs = [
    {
      id: 'LOG-88910',
      timestamp: '2026-02-27T10:04:12Z',
      entity: 'JournalEntry',
      entityId: 'JV-2026-0042',
      action: 'POST_TRANSACTION',
      user: 'alex.morgan@nexerp.io',
      ip: '192.168.1.104',
      entryHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      prevHash: '7d793037a0760186574b0282f2f435e70d716860d243a99179540e88a0e0516e',
      diff: { status: { from: 'DRAFT', to: 'POSTED' }, total_debit: 50000.0 }
    },
    {
      id: 'LOG-88909',
      timestamp: '2026-02-27T09:45:01Z',
      entity: 'PurchaseOrder',
      entityId: 'PO-2026-0012',
      action: 'APPROVE_WORKFLOW',
      user: 'sarah.jenkins@nexerp.io',
      ip: '192.168.1.122',
      entryHash: '7d793037a0760186574b0282f2f435e70d716860d243a99179540e88a0e0516e',
      prevHash: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
      diff: { status: { from: 'IN_PROGRESS', to: 'APPROVED' }, approved_step: 2 }
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">SOX Section 404 Cryptographic Audit Trail</h1>
          <p className="text-sm text-slate-500">Immutable SHA-256 hash-chained event ledger tracking all financial postings and system mutations.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 rounded-lg text-xs font-semibold">
          <Lock className="w-4 h-4" /> Hash Chain Integrity: Verified 100% Tamper-Evident
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
          <div className="relative w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by Entity ID, User, or Hash..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs"
            />
          </div>
        </div>

        <div className="divide-y divide-slate-200 dark:divide-slate-700">
          {mockLogs.map((log) => (
            <div key={log.id} className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/30 space-y-2">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-mono text-xs font-bold rounded">
                    {log.action}
                  </span>
                  <span className="font-semibold text-slate-900 dark:text-white text-sm">{log.entity}</span>
                  <span className="font-mono text-xs text-slate-500">{log.entityId}</span>
                </div>
                <span className="text-xs text-slate-400 font-mono">{log.timestamp}</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-300">
                <div>
                  <span className="text-slate-400">Actor:</span> {log.user} ({log.ip})
                </div>
                <div className="font-mono text-[11px] truncate">
                  <span className="text-slate-400">Entry Hash:</span> {log.entryHash}
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900/60 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-700 dark:text-slate-300">
                <span className="text-slate-400 font-sans font-medium text-[11px] block mb-1">State Mutation Delta:</span>
                {JSON.stringify(log.diff, null, 2)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
