import React, { useState } from 'react';
import { Users, Star, TrendingUp, ChevronRight, Layers, Award } from 'lucide-react';

type PerformanceRating = 1 | 2 | 3 | 4 | 5;
type PotentialRating = 'Low' | 'Moderate' | 'High';

interface Employee {
  id: string;
  name: string;
  title: string;
  department: string;
  performance: PerformanceRating;
  potential: PotentialRating;
  tenure_years: number;
  salary_band: string;
  ready_in: 'Now' | '1-2 Years' | '3-5 Years';
  successor_to?: string;
}

const EMPLOYEES: Employee[] = [
  { id: 'E001', name: 'Sophia Harrington', title: 'VP Finance', department: 'Finance', performance: 5, potential: 'High', tenure_years: 8, salary_band: 'L7', ready_in: 'Now', successor_to: 'CFO' },
  { id: 'E002', name: 'Marcus Chen', title: 'Director Supply Chain', department: 'Operations', performance: 4, potential: 'High', tenure_years: 6, salary_band: 'L6', ready_in: '1-2 Years', successor_to: 'VP Operations' },
  { id: 'E003', name: 'Aisha Okafor', title: 'Senior HR Manager', department: 'HR', performance: 5, potential: 'High', tenure_years: 5, salary_band: 'L5', ready_in: '1-2 Years' },
  { id: 'E004', name: 'James Patterson', title: 'Lead Engineer', department: 'Engineering', performance: 4, potential: 'Moderate', tenure_years: 4, salary_band: 'L5', ready_in: '3-5 Years' },
  { id: 'E005', name: 'Nina Kowalski', title: 'Sales Manager', department: 'Sales', performance: 3, potential: 'High', tenure_years: 3, salary_band: 'L4', ready_in: '3-5 Years' },
  { id: 'E006', name: 'David Lawson', title: 'Controller', department: 'Finance', performance: 3, potential: 'Moderate', tenure_years: 7, salary_band: 'L5', ready_in: '3-5 Years' },
  { id: 'E007', name: 'Rachel Torres', title: 'QA Manager', department: 'Quality', performance: 2, potential: 'High', tenure_years: 2, salary_band: 'L4', ready_in: '3-5 Years' },
  { id: 'E008', name: 'Kevin Blake', title: 'Procurement Analyst', department: 'Procurement', performance: 3, potential: 'Low', tenure_years: 5, salary_band: 'L3', ready_in: '3-5 Years' },
  { id: 'E009', name: 'Linda Marsh', title: 'Accounts Payable Lead', department: 'Finance', performance: 2, potential: 'Moderate', tenure_years: 6, salary_band: 'L3', ready_in: '3-5 Years' },
];

const PERFORMANCE_LABELS: Record<PerformanceRating, string> = {
  5: 'Exceptional',
  4: 'Exceeds Expectations',
  3: 'Meets Expectations',
  2: 'Below Expectations',
  1: 'Critical',
};

function get9Box(perf: PerformanceRating, pot: PotentialRating): { label: string; color: string; description: string } {
  if (perf >= 4 && pot === 'High') return { label: 'Star / Future Leader', color: 'bg-purple-600', description: 'Top succession candidate — accelerated development track.' };
  if (perf >= 4 && pot === 'Moderate') return { label: 'Core Contributor', color: 'bg-blue-600', description: 'Solid performer — lateral or vertical development opportunity.' };
  if (perf >= 4 && pot === 'Low') return { label: 'Expert / Specialist', color: 'bg-teal-600', description: 'Deep domain expert — technical track retention focus.' };
  if (perf === 3 && pot === 'High') return { label: 'High Potential', color: 'bg-emerald-500', description: 'Growth trajectory — coaching needed to lift performance.' };
  if (perf === 3 && pot === 'Moderate') return { label: 'Effective', color: 'bg-yellow-500', description: 'Consistent contributor — steady performer.' };
  if (perf === 3 && pot === 'Low') return { label: 'Reliable', color: 'bg-orange-400', description: 'Dependable but limited growth potential.' };
  if (perf <= 2 && pot === 'High') return { label: 'Inconsistent Star', color: 'bg-pink-500', description: 'Potential star underperforming — may need new role/manager.' };
  if (perf <= 2 && pot === 'Moderate') return { label: 'Developing', color: 'bg-red-400', description: 'Below standard — PIP consideration or role reassignment.' };
  return { label: 'Risk / Underperformer', color: 'bg-red-700', description: 'Low performance and potential — exit or action plan required.' };
}

export default function SuccessionPlanningPage() {
  const [selected, setSelected] = useState<Employee | null>(null);
  const [filterDept, setFilterDept] = useState<string>('All');

  const departments = ['All', ...Array.from(new Set(EMPLOYEES.map(e => e.department)))];
  const filtered = filterDept === 'All' ? EMPLOYEES : EMPLOYEES.filter(e => e.department === filterDept);

  const stars = EMPLOYEES.filter(e => e.performance >= 4 && e.potential === 'High');
  const readyNow = EMPLOYEES.filter(e => e.ready_in === 'Now');

  // 9-Box grid positions: perf rows 5→1 (top→bottom), potential cols Low→Moderate→High (left→right)
  const perfLevels: PerformanceRating[] = [5, 4, 3, 2, 1];
  const potLevels: PotentialRating[] = ['Low', 'Moderate', 'High'];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Users className="text-purple-600" />
          Succession Planning & 9-Box Talent Grid
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Identify succession candidates and development priorities across the talent portfolio.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p className="text-xs text-gray-500">Total Assessed</p>
          <p className="text-2xl font-bold text-gray-900">{EMPLOYEES.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p className="text-xs text-gray-500">Stars / Future Leaders</p>
          <p className="text-2xl font-bold text-purple-700">{stars.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p className="text-xs text-gray-500">Ready Now</p>
          <p className="text-2xl font-bold text-emerald-600">{readyNow.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p className="text-xs text-gray-500">Succession Mapped</p>
          <p className="text-2xl font-bold text-indigo-600">{EMPLOYEES.filter(e => e.successor_to).length}</p>
        </div>
      </div>

      {/* 9-Box Grid */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Layers size={16} className="text-purple-500" />
          9-Box Talent Matrix
        </h2>

        <div className="flex">
          {/* Y-axis label */}
          <div className="flex flex-col justify-around items-end mr-2 text-xs text-gray-400 font-medium">
            {perfLevels.map(p => (
              <span key={p} className="transform -rotate-0 text-right w-28">
                {PERFORMANCE_LABELS[p]}
              </span>
            ))}
          </div>

          <div className="flex-1">
            {/* Column Headers */}
            <div className="grid grid-cols-3 gap-1 mb-1">
              {potLevels.map(p => (
                <div key={p} className="text-center text-xs font-semibold text-gray-500">{p} Potential</div>
              ))}
            </div>

            {/* Grid */}
            <div className="space-y-1">
              {perfLevels.map(perf => (
                <div key={perf} className="grid grid-cols-3 gap-1">
                  {potLevels.map(pot => {
                    const box = get9Box(perf, pot);
                    const inhabitants = filtered.filter(e => e.performance === perf && e.potential === pot);
                    return (
                      <div
                        key={pot}
                        className="min-h-[90px] rounded-lg border border-gray-100 bg-gray-50 p-2 hover:border-indigo-300 transition-colors"
                      >
                        <p className="text-xs font-semibold text-gray-600 mb-1 truncate">{box.label}</p>
                        <div className="space-y-1">
                          {inhabitants.map(e => (
                            <button
                              key={e.id}
                              onClick={() => setSelected(e)}
                              className={`w-full text-left px-2 py-1 rounded text-xs text-white font-medium ${box.color} hover:opacity-80 truncate`}
                            >
                              {e.name}
                            </button>
                          ))}
                          {inhabitants.length === 0 && (
                            <span className="text-xs text-gray-300">Empty</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>

            {/* X-axis label */}
            <div className="text-center mt-2 text-xs font-semibold text-gray-500">← Potential →</div>
          </div>
        </div>
      </div>

      {/* Department filter + Employee List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-semibold text-gray-800">Employee Talent Profiles</h2>
          <select
            value={filterDept}
            onChange={e => setFilterDept(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            {departments.map(d => <option key={d}>{d}</option>)}
          </select>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Name', 'Title', 'Department', 'Performance', 'Potential', 'Readiness', 'Successor To', 'Box'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {filtered.map(e => {
              const box = get9Box(e.performance, e.potential);
              return (
                <tr
                  key={e.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => setSelected(e)}
                >
                  <td className="px-4 py-3 font-semibold text-gray-900">{e.name}</td>
                  <td className="px-4 py-3 text-gray-600">{e.title}</td>
                  <td className="px-4 py-3 text-gray-500">{e.department}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          size={12}
                          className={i < e.performance ? 'text-yellow-400 fill-yellow-400' : 'text-gray-200 fill-gray-200'}
                        />
                      ))}
                      <span className="ml-1 text-xs text-gray-500">{PERFORMANCE_LABELS[e.performance]}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      e.potential === 'High' ? 'bg-purple-100 text-purple-700' :
                      e.potential === 'Moderate' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {e.potential}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      e.ready_in === 'Now' ? 'bg-emerald-100 text-emerald-700' :
                      e.ready_in === '1-2 Years' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {e.ready_in}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{e.successor_to || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold text-white ${box.color}`}>
                      {box.label}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Employee Detail Drawer */}
      {selected && (
        <div className="fixed inset-0 bg-black/40 flex items-end md:items-center justify-center z-50" onClick={() => setSelected(null)}>
          <div className="bg-white rounded-t-3xl md:rounded-2xl shadow-2xl w-full max-w-lg p-6" onClick={e => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{selected.name}</h3>
                <p className="text-sm text-gray-500">{selected.title} · {selected.department} · Band {selected.salary_band}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${get9Box(selected.performance, selected.potential).color}`}>
                {get9Box(selected.performance, selected.potential).label}
              </span>
            </div>

            <p className="text-sm text-gray-600 mb-4 bg-gray-50 rounded-lg p-3">
              {get9Box(selected.performance, selected.potential).description}
            </p>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-400 text-xs">Performance</p>
                <div className="flex items-center gap-1 mt-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} size={14} className={i < selected.performance ? 'text-yellow-400 fill-yellow-400' : 'text-gray-200 fill-gray-200'} />
                  ))}
                </div>
                <p className="text-xs text-gray-600 mt-1">{PERFORMANCE_LABELS[selected.performance]}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Potential</p>
                <p className="font-semibold text-gray-900 mt-1">{selected.potential}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Succession Readiness</p>
                <p className="font-semibold text-gray-900 mt-1">{selected.ready_in}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Tenure</p>
                <p className="font-semibold text-gray-900 mt-1">{selected.tenure_years} years</p>
              </div>
              {selected.successor_to && (
                <div className="col-span-2">
                  <p className="text-gray-400 text-xs">Successor Candidate For</p>
                  <p className="font-semibold text-indigo-600 mt-1 flex items-center gap-1">
                    <Award size={14} /> {selected.successor_to}
                  </p>
                </div>
              )}
            </div>

            <button
              onClick={() => setSelected(null)}
              className="mt-5 w-full py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
