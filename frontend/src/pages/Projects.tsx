import React, { useEffect, useState } from 'react';
import { Briefcase, Plus, Clock, Target, CheckCircle2 } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const Projects: React.FC = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const res = await api.get('/projects');
        setProjects(res.data);
      } catch (err) {
        setProjects([
          { project_number: 'PRJ-2026-00001', name: 'Next-Gen Subsea High-Pressure Pumping System R&D', start_date: '2026-01-10', budget_amount: 450000.0, total_logged_hours: 180.0, total_cost_incurred: 22500.0, status: 'ACTIVE' },
          { project_number: 'PRJ-2026-00002', name: 'Refinery Hydrocracking Manifold Overhaul', start_date: '2026-02-01', budget_amount: 180000.0, total_logged_hours: 45.0, total_cost_incurred: 5625.0, status: 'ACTIVE' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadProjects();
  }, []);

  const prjCols: Column<any>[] = [
    { header: 'Project Code', accessor: 'project_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Project Scope & Name', accessor: 'name', className: 'font-medium text-white' },
    { header: 'Start Date', accessor: 'start_date', className: 'font-mono text-slate-400' },
    {
      header: 'Budget',
      accessor: (row) => `$${row.budget_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
    {
      header: 'Logged Hours',
      accessor: (row) => `${row.total_logged_hours} hrs`,
      className: 'font-mono text-brand-400 text-center',
    },
    {
      header: 'Cost Incurred',
      accessor: (row) => `$${row.total_cost_incurred.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-semibold text-rose-400 text-right',
    },
    {
      header: 'Status',
      accessor: (row) => (
        <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-semibold">
          {row.status}
        </span>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Briefcase className="w-6 h-6 text-brand-500" />
            Projects & Professional Services (PSA)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Work Breakdown Structure (WBS), Gantt Tasks, Milestones, and Weekly Timesheets.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Create Project</span>
          </button>
        </div>
      </div>

      <DataTable
        title="Active Engineering & Professional Services Projects"
        columns={prjCols}
        data={projects}
        searchPlaceholder="Search projects..."
      />
    </div>
  );
};
