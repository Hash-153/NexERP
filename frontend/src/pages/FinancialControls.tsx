import React, { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle2, ClipboardCheck, DollarSign, RefreshCw, ShieldCheck } from 'lucide-react';
import api from '../services/api';

type CashSummary = { weighted_inflow: string; weighted_outflow: string; weighted_net_cash: string };
type Readiness = { period_id: string; required_count: number; completed_count: number; open_required_count: number; ready_to_lock: boolean };

export const FinancialControls: React.FC = () => {
  const [cash, setCash] = useState<CashSummary | null>(null);
  const [periodId, setPeriodId] = useState('');
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true); setError('');
    try {
      const cashResponse = await api.get('/financial-controls/cash-forecast/summary');
      setCash(cashResponse.data);
    } catch { setError('Unable to load financial control data.'); } finally { setLoading(false); }
  };
  useEffect(() => { void load(); }, []);
  const checkPeriod = async (event: React.FormEvent) => { event.preventDefault(); if (!periodId.trim()) return; try { const response = await api.get(`/financial-controls/periods/${periodId}/readiness`); setReadiness(response.data); } catch { setError('The fiscal period could not be found.'); } };
  const format = (value?: string) => `$${Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

  return <main className="min-h-full bg-slate-950 px-5 py-6 text-slate-100 lg:px-8"><header className="mb-7 flex flex-wrap items-end justify-between gap-4"><div><div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-emerald-400"><ShieldCheck size={14} /> Controller workspace</div><h1 className="text-3xl font-semibold tracking-tight">Financial controls</h1><p className="mt-1 text-sm text-slate-400">Monitor close readiness, cash commitments, and approval discipline.</p></div><button onClick={() => void load()} title="Refresh control data" className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:border-emerald-500"><RefreshCw size={16} /> Refresh</button></header>
    {error && <div className="mb-5 flex items-center gap-2 border border-rose-900 bg-rose-950/40 px-4 py-3 text-sm text-rose-200"><AlertCircle size={16} /> {error}</div>}
    <section className="mb-7 grid grid-cols-1 gap-3 sm:grid-cols-3"><Metric icon={<DollarSign size={17} />} label="Weighted inflow" value={format(cash?.weighted_inflow)} color="text-emerald-300" /><Metric icon={<DollarSign size={17} />} label="Weighted outflow" value={format(cash?.weighted_outflow)} color="text-rose-300" /><Metric icon={<ClipboardCheck size={17} />} label="Net cash position" value={format(cash?.weighted_net_cash)} color="text-cyan-300" /></section>
    <section className="grid gap-5 lg:grid-cols-[1fr_1.4fr]"><form onSubmit={checkPeriod} className="border border-slate-800 bg-slate-900/70 p-5"><h2 className="mb-2 text-lg font-semibold">Close readiness</h2><p className="mb-5 text-sm text-slate-400">Enter a fiscal period ID to inspect its required control checklist.</p><label className="block text-sm text-slate-300">Fiscal period ID<input value={periodId} onChange={event => setPeriodId(event.target.value)} placeholder="Paste period ID" className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-emerald-400" required /></label><button type="submit" className="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950"><ClipboardCheck size={16} /> Check readiness</button></form><div className="border border-slate-800 bg-slate-900/70 p-5">{loading ? <div className="py-10 text-center text-sm text-slate-500">Loading controls...</div> : readiness ? <><div className="mb-5 flex items-center justify-between"><h2 className="text-lg font-semibold">Period status</h2>{readiness.ready_to_lock ? <span className="inline-flex items-center gap-1 text-sm text-emerald-300"><CheckCircle2 size={16} /> Ready to lock</span> : <span className="inline-flex items-center gap-1 text-sm text-amber-300"><AlertCircle size={16} /> Action required</span>}</div><div className="mb-4 h-3 overflow-hidden rounded-full bg-slate-800"><div className="h-full bg-emerald-400 transition-all" style={{ width: `${readiness.required_count ? readiness.completed_count / readiness.required_count * 100 : 0}%` }} /></div><div className="grid grid-cols-3 gap-3 text-center text-sm"><div><div className="text-xl font-semibold">{readiness.required_count}</div><div className="text-slate-500">Required</div></div><div><div className="text-xl font-semibold text-emerald-300">{readiness.completed_count}</div><div className="text-slate-500">Completed</div></div><div><div className="text-xl font-semibold text-amber-300">{readiness.open_required_count}</div><div className="text-slate-500">Open</div></div></div></> : <div className="py-10 text-center text-sm text-slate-500">Period readiness will appear here.</div>}</div></section>
  </main>;
};
const Metric: React.FC<{ icon: React.ReactNode; label: string; value: string; color: string }> = ({ icon, label, value, color }) => <div className="border border-slate-800 bg-slate-900/70 p-4"><div className={`mb-3 flex items-center gap-2 text-xs uppercase tracking-wider ${color}`}>{icon}{label}</div><div className="text-2xl font-semibold tabular-nums">{value}</div></div>;
