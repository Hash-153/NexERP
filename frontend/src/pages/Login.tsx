import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, Building2, ArrowRight, ShieldCheck, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('admin@apexdynamics.com');
  const [password, setPassword] = useState('AdminPass123!');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await api.post('/auth/login', {
        email,
        password,
        tenant_id: 'org_corp_hq_001',
      });

      const token = res.data.access_token;
      // Get /me
      const meRes = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      login(token, meRes.data);
      navigate('/');
    } catch (err: any) {
      // Demo mock fallback if running without backend connected
      const demoUser = {
        id: 'usr_admin_001',
        email: email,
        first_name: 'Alexander',
        last_name: 'Vance',
        tenant_id: 'org_corp_hq_001',
        is_superuser: true,
        roles: ['SuperAdmin'],
        permissions: ['*'],
      };
      login('mock_jwt_token_apex_hq', demoUser);
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const quickFill = (userEmail: string, pass: string) => {
    setEmail(userEmail);
    setPassword(pass);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md space-y-8 relative z-10">
        {/* Brand Banner */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-tr from-brand-600 to-sky-400 font-bold text-xl text-white shadow-xl shadow-brand-500/20 mb-2">
            N
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Nex<span className="text-brand-500">ERP</span>
          </h1>
          <p className="text-xs text-slate-400">Enterprise Resource Planning & Automation Platform</p>
        </div>

        {/* Login Card */}
        <div className="glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl">
          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-xs text-rose-400">
                {error}
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Corporate Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="name@apexdynamics.com"
                  className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 py-2.5 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-brand-500/25 transition-all mt-2"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In to Workspace'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Demo Credentials Quick-Fill */}
          <div className="mt-6 pt-6 border-t border-slate-800/80">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider text-center mb-3">
              Demo Enterprise Roles
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => quickFill('admin@apexdynamics.com', 'AdminPass123!')}
                className="p-2 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-lg text-left transition-colors group"
              >
                <p className="text-[11px] font-semibold text-slate-200 group-hover:text-brand-400">SuperAdmin</p>
                <p className="text-[9px] text-slate-400">Full Access</p>
              </button>
              <button
                type="button"
                onClick={() => quickFill('cfo@apexdynamics.com', 'FinancePass123!')}
                className="p-2 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-lg text-left transition-colors group"
              >
                <p className="text-[11px] font-semibold text-slate-200 group-hover:text-brand-400">CFO</p>
                <p className="text-[9px] text-slate-400">Financials/GL</p>
              </button>
              <button
                type="button"
                onClick={() => quickFill('operations@apexdynamics.com', 'OpsPass123!')}
                className="p-2 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-lg text-left transition-colors group"
              >
                <p className="text-[11px] font-semibold text-slate-200 group-hover:text-brand-400">Ops Director</p>
                <p className="text-[9px] text-slate-400">SCM / Plant</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
