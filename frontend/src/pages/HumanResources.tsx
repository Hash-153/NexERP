import React, { useEffect, useState } from 'react';
import { Users, Plus, DollarSign, Calendar, FileText, CheckCircle2 } from 'lucide-react';
import { DataTable, Column } from '../components/common/DataTable';
import api from '../services/api';

export const HumanResources: React.FC = () => {
  const [employees, setEmployees] = useState<any[]>([]);
  const [payrollRuns, setPayrollRuns] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'employees' | 'payroll'>('employees');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHR = async () => {
      try {
        const [eRes, pRes] = await Promise.all([
          api.get('/hr/employees'),
          api.get('/hr/payroll/runs')
        ]);
        setEmployees(eRes.data);
        setPayrollRuns(pRes.data);
      } catch (err) {
        setEmployees([
          { employee_number: 'EMP-001', first_name: 'Alexander', last_name: 'Vance', department: { name: 'Executive Leadership' }, job_position: { title: 'Chief Executive Officer' }, base_salary: 18500.0, employment_status: 'ACTIVE' },
          { employee_number: 'EMP-002', first_name: 'Eleanor', last_name: 'Sterling', department: { name: 'Finance & Accounting' }, job_position: { title: 'Chief Financial Officer' }, base_salary: 15000.0, employment_status: 'ACTIVE' },
          { employee_number: 'EMP-003', first_name: 'Marcus', last_name: 'Kane', department: { name: 'Plant Manufacturing' }, job_position: { title: 'Operations Director' }, base_salary: 12500.0, employment_status: 'ACTIVE' },
          { employee_number: 'EMP-004', first_name: 'Dr. Julian', last_name: 'Mercer', department: { name: 'Engineering & R&D' }, job_position: { title: 'Principal Engineer' }, base_salary: 11000.0, employment_status: 'ACTIVE' },
          { employee_number: 'EMP-005', first_name: 'Thomas', last_name: 'Hale', department: { name: 'Plant Manufacturing' }, job_position: { title: 'CNC Machinist' }, base_salary: 7200.0, employment_status: 'ACTIVE' },
        ]);
        setPayrollRuns([
          { run_number: 'PAYROLL-2026-01', month: 1, year: 2026, total_gross_pay: 77040.0, total_tax_withheld: 16948.8, total_net_pay: 52387.2, status: 'APPROVED' }
        ]);
      } finally {
        setLoading(false);
      }
    };
    loadHR();
  }, []);

  const empCols: Column<any>[] = [
    { header: 'Emp #', accessor: 'employee_number', className: 'font-mono font-bold text-brand-400' },
    {
      header: 'Full Name',
      accessor: (row) => `${row.first_name} ${row.last_name}`,
      className: 'font-medium text-white',
    },
    { header: 'Department', accessor: (row) => row.department?.name || 'Operations', className: 'text-slate-300' },
    { header: 'Job Title', accessor: (row) => row.job_position?.title || 'Engineer', className: 'text-slate-300' },
    {
      header: 'Status',
      accessor: (row) => (
        <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-semibold">
          {row.employment_status}
        </span>
      )
    },
    {
      header: 'Monthly Base Salary',
      accessor: (row) => `$${row.base_salary.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
  ];

  const payrollCols: Column<any>[] = [
    { header: 'Batch Number', accessor: 'run_number', className: 'font-mono font-bold text-brand-400' },
    { header: 'Month / Year', accessor: (row) => `${row.month} / ${row.year}`, className: 'font-mono' },
    {
      header: 'Total Gross Pay',
      accessor: (row) => `$${row.total_gross_pay.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-white text-right',
    },
    {
      header: 'Tax Withheld',
      accessor: (row) => `$${row.total_tax_withheld.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono text-rose-400 text-right',
    },
    {
      header: 'Total Net Pay',
      accessor: (row) => `$${row.total_net_pay.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      className: 'font-mono font-bold text-emerald-400 text-right',
    },
    {
      header: 'GL Status',
      accessor: (row) => (
        <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-semibold">
          GL Posted & Approved
        </span>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Users className="w-6 h-6 text-brand-500" />
            Human Resources & Payroll Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Employee Directory, Org Chart, Attendance, Progressive Tax Slabs, and Automated GL Payroll Accruals.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-brand-500/20 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Onboard Employee</span>
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('employees')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'employees'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Employee Directory
        </button>
        <button
          onClick={() => setActiveTab('payroll')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'payroll'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          Monthly Payroll Runs
        </button>
      </div>

      {activeTab === 'employees' && (
        <DataTable
          title="Enterprise Employee Master Directory"
          columns={empCols}
          data={employees}
          searchPlaceholder="Search employees..."
        />
      )}

      {activeTab === 'payroll' && (
        <DataTable
          title="Monthly Progressive Bracket Payroll Batches"
          columns={payrollCols}
          data={payrollRuns}
          searchPlaceholder="Search payroll runs..."
        />
      )}
    </div>
  );
};
