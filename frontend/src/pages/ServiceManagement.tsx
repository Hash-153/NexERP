import React, { useEffect, useState } from 'react';
import { AlertTriangle, ClipboardList, Clock3, Filter, Gauge, Plus, RefreshCw, Search, Wrench } from 'lucide-react';
import api from '../services/api';

type Ticket = {
  id: string;
  ticket_number: string;
  subject: string;
  description: string;
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';
  status: 'OPEN' | 'IN_PROGRESS' | 'WAITING_CUSTOMER' | 'RESOLVED' | 'CLOSED' | 'CANCELLED';
  assigned_to_id?: string;
  actual_hours: string;
  due_at?: string;
  opened_at: string;
};

type Summary = { status: string; priority: string; ticket_count: number; total_hours: string; overdue_count: number };

const statusLabels: Record<Ticket['status'], string> = {
  OPEN: 'Open', IN_PROGRESS: 'In progress', WAITING_CUSTOMER: 'Waiting', RESOLVED: 'Resolved', CLOSED: 'Closed', CANCELLED: 'Cancelled'
};

const priorityStyles: Record<Ticket['priority'], string> = {
  LOW: 'text-slate-400 bg-slate-800', NORMAL: 'text-sky-300 bg-sky-950/50', HIGH: 'text-amber-300 bg-amber-950/50', URGENT: 'text-rose-300 bg-rose-950/50'
};

export const ServiceManagement: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [summary, setSummary] = useState<Summary[]>([]);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showNew, setShowNew] = useState(false);
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Ticket['priority']>('NORMAL');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [ticketResponse, summaryResponse] = await Promise.all([
        api.get('/service-management/tickets'),
        api.get('/service-management/summary')
      ]);
      setTickets(ticketResponse.data);
      setSummary(summaryResponse.data);
    } catch {
      setError('Service data could not be loaded. Check the API connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const createTicket = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!subject.trim() || !description.trim()) return;
    await api.post('/service-management/tickets', { subject, description, priority, channel: 'PORTAL' });
    setSubject('');
    setDescription('');
    setPriority('NORMAL');
    setShowNew(false);
    await load();
  };

  const filteredTickets = tickets.filter(ticket => {
    const matchesSearch = `${ticket.ticket_number} ${ticket.subject} ${ticket.description}`.toLowerCase().includes(search.toLowerCase());
    return matchesSearch && (!status || ticket.status === status);
  });
  const openCount = tickets.filter(ticket => ['OPEN', 'IN_PROGRESS', 'WAITING_CUSTOMER'].includes(ticket.status)).length;
  const overdueCount = summary.reduce((total, row) => total + row.overdue_count, 0);
  const workedHours = tickets.reduce((total, ticket) => total + Number(ticket.actual_hours || 0), 0);

  return (
    <main className="min-h-full bg-slate-950 px-5 py-6 text-slate-100 lg:px-8">
      <header className="mb-7 flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-cyan-400"><Wrench size={14} /> Customer operations</div>
          <h1 className="text-3xl font-semibold tracking-tight">Service desk</h1>
          <p className="mt-1 text-sm text-slate-400">Keep customer commitments visible from first response through resolution.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => void load()} title="Refresh service data" className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:border-cyan-500"><RefreshCw size={16} /> Refresh</button>
          <button onClick={() => setShowNew(true)} className="inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-400"><Plus size={16} /> New ticket</button>
        </div>
      </header>

      {error && <div className="mb-5 flex items-center gap-2 border border-rose-900 bg-rose-950/40 px-4 py-3 text-sm text-rose-200"><AlertTriangle size={16} /> {error}</div>}
      <section className="mb-7 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Metric icon={<ClipboardList size={18} />} label="Open workload" value={String(openCount)} detail="Active tickets" color="text-cyan-300" />
        <Metric icon={<Clock3 size={18} />} label="SLA at risk" value={String(overdueCount)} detail="Past response target" color="text-rose-300" />
        <Metric icon={<Gauge size={18} />} label="Logged hours" value={workedHours.toFixed(1)} detail="Across visible tickets" color="text-amber-300" />
        <Metric icon={<Filter size={18} />} label="Total tickets" value={String(tickets.length)} detail="Current queue" color="text-emerald-300" />
      </section>

      <section className="border border-slate-800 bg-slate-900/70">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 px-4 py-4">
          <div className="relative min-w-[240px] flex-1"><Search size={16} className="absolute left-3 top-2.5 text-slate-500" /><input value={search} onChange={event => setSearch(event.target.value)} placeholder="Search ticket number or subject" className="w-full rounded-lg border border-slate-700 bg-slate-950 py-2 pl-9 pr-3 text-sm text-slate-200 outline-none focus:border-cyan-500" /></div>
          <select value={status} onChange={event => setStatus(event.target.value)} className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-300 outline-none focus:border-cyan-500"><option value="">All statuses</option>{Object.entries(statusLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-slate-950/70 text-xs uppercase tracking-wider text-slate-500"><tr><th className="px-4 py-3">Ticket</th><th className="px-4 py-3">Priority</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">SLA due</th><th className="px-4 py-3 text-right">Hours</th></tr></thead><tbody className="divide-y divide-slate-800">{loading ? <tr><td colSpan={5} className="px-4 py-12 text-center text-slate-500">Loading service queue...</td></tr> : filteredTickets.length === 0 ? <tr><td colSpan={5} className="px-4 py-12 text-center text-slate-500">No tickets match this view.</td></tr> : filteredTickets.map(ticket => <tr key={ticket.id} className="hover:bg-slate-800/40"><td className="px-4 py-4"><div className="font-medium text-slate-200">{ticket.subject}</div><div className="mt-1 text-xs text-slate-500">{ticket.ticket_number}</div></td><td className="px-4 py-4"><span className={`rounded px-2 py-1 text-xs font-medium ${priorityStyles[ticket.priority]}`}>{ticket.priority}</span></td><td className="px-4 py-4 text-slate-300">{statusLabels[ticket.status]}</td><td className="px-4 py-4 text-slate-400">{ticket.due_at ? new Date(ticket.due_at).toLocaleString() : 'No contract SLA'}</td><td className="px-4 py-4 text-right tabular-nums text-slate-300">{Number(ticket.actual_hours || 0).toFixed(2)}</td></tr>)}</tbody></table>
        </div>
      </section>

      {showNew && <div className="fixed inset-0 z-20 flex items-center justify-center bg-slate-950/80 p-4"><form onSubmit={createTicket} className="w-full max-w-lg border border-slate-700 bg-slate-900 p-6 shadow-2xl"><div className="mb-5 flex items-center justify-between"><h2 className="text-lg font-semibold">Create service ticket</h2><button type="button" onClick={() => setShowNew(false)} className="text-slate-500 hover:text-slate-200" aria-label="Close">×</button></div><label className="mb-4 block text-sm text-slate-300">Subject<input value={subject} onChange={event => setSubject(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-cyan-500" required /></label><label className="mb-4 block text-sm text-slate-300">Description<textarea value={description} onChange={event => setDescription(event.target.value)} rows={4} className="mt-2 w-full resize-y rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-cyan-500" required /></label><label className="mb-6 block text-sm text-slate-300">Priority<select value={priority} onChange={event => setPriority(event.target.value as Ticket['priority'])} className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-cyan-500">{Object.keys(priorityStyles).map(key => <option key={key}>{key}</option>)}</select></label><div className="flex justify-end gap-2"><button type="button" onClick={() => setShowNew(false)} className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300">Cancel</button><button type="submit" className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950">Create ticket</button></div></form></div>}
    </main>
  );
};

const Metric: React.FC<{ icon: React.ReactNode; label: string; value: string; detail: string; color: string }> = ({ icon, label, value, detail, color }) => <div className="border border-slate-800 bg-slate-900/70 p-4"><div className={`mb-3 flex items-center gap-2 text-xs uppercase tracking-wider ${color}`}>{icon}{label}</div><div className="text-2xl font-semibold tabular-nums">{value}</div><div className="mt-1 text-xs text-slate-500">{detail}</div></div>;
