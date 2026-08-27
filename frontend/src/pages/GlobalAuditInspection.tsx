import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface AuditLogRecord {
  id: string;
  timestamp: string;
  actor_email: string;
  action: string;
  entity_type: string;
  entity_id: string;
  description: string;
}

export function GlobalAuditInspection() {
  const kpis: KPICardData[] = [
    { title: 'Total Immutable Audit Events', value: '84,290', change: '+1,420 Today', isPositive: true, icon: '🛡️', subtitle: 'SHA-256 state delta captured' },
    { title: 'SOX 404 Segregation of Duties', value: '100% Compliant', change: 'Zero Violations', isPositive: true, icon: '⚖️', subtitle: 'Dual authorization enforced' },
    { title: 'GDPR / CCPA Erasure Requests', value: '100% Fulfilled', change: 'Audit Logged', isPositive: true, icon: '🔒', subtitle: 'Cryptographic anonymization' },
    { title: 'Security Privilege Escalations', value: '0 Breaches', change: 'Secure', isPositive: true, icon: '🔑', subtitle: 'RBAC boundary enforced' },
  ];

  const logs: AuditLogRecord[] = [
    { id: '1', timestamp: '2026-03-01 13:45:12 UTC', actor_email: 'cfo@nexerp.local', action: 'POST_JOURNAL_VOUCHER', entity_type: 'JournalEntry', entity_id: 'JV-2026-00491', description: 'Posted $124,500 monthly asset depreciation journal' },
    { id: '2', timestamp: '2026-03-01 13:30:04 UTC', actor_email: 'treasury.ops@nexerp.local', action: 'EXECUTE_CASH_SWEEP', entity_type: 'TreasuryBankAccount', entity_id: 'ACC-JPM-001', description: 'Executed zero-balance sweep of $450,000 from Barclays UK' },
    { id: '3', timestamp: '2026-03-01 12:15:40 UTC', actor_email: 'warehouse.lead@nexerp.local', action: 'RELEASE_WAVE', entity_type: 'WaveBatchRun', entity_id: 'WAVE-20260301-A1', description: 'Released carrier cutoff wave for 120 pick lines' },
    { id: '4', timestamp: '2026-03-01 11:00:22 UTC', actor_email: 'legal.counsel@nexerp.local', action: 'CREATE_CONTRACT', entity_type: 'ContractDocument', entity_id: 'MSA-2026-081', description: 'Executed $3,600,000 Master Services Agreement' },
  ];

  const columns: ColumnDef<AuditLogRecord>[] = [
    { key: 'timestamp', header: 'Timestamp (UTC)', width: '20%', render: l => <span className="font-mono text-xs">{l.timestamp}</span> },
    { key: 'actor_email', header: 'Actor User', width: '22%', render: l => <span className="font-bold text-slate-800 dark:text-slate-200">{l.actor_email}</span> },
    { key: 'action', header: 'Action Verb', width: '18%', render: l => <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-800 font-mono font-bold">{l.action}</span> },
    { key: 'entity_type', header: 'Entity Domain', width: '15%' },
    { key: 'description', header: 'Audit Detail & Forensic Payload', width: '25%' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Global Forensic Audit Trail</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Immutable ledger state capture, field-level delta diffing, SOX 404 segregation of duties, and compliance inspection</p>
        </div>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Forensic State Modification Audit Trail"
        subtitle="Complete chronological record of all state transitions, financial postings, and authorization events"
        columns={columns}
        data={logs}
      />
    </div>
  );
}
