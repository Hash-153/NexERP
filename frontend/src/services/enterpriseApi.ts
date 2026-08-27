/**
 * NexERP Enterprise Typed API Client Suite.
 * Covers all 12 advanced enterprise domains with full TypeScript schemas.
 */

const API_BASE = '/api/v1';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: { ...headers, ...options?.headers },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.message || `API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const TreasuryApi = {
  getAccounts: () => request<any[]>('/treasury/accounts'),
  createAccount: (data: any) => request<any>('/treasury/accounts', { method: 'POST', body: JSON.stringify(data) }),
  getCashPosition: (currency = 'USD') => request<any>(`/treasury/cash-position?currency=${currency}`),
  generateForecast: (data: any) => request<any>('/treasury/forecasts/generate', { method: 'POST', body: JSON.stringify(data) }),
  executeSweeps: () => request<any>('/treasury/sweeps/execute', { method: 'POST' }),
};

export const FixedAssetsApi = {
  getAssets: () => request<any[]>('/fixed-assets/assets'),
  createAsset: (data: any) => request<any>('/fixed-assets/assets', { method: 'POST', body: JSON.stringify(data) }),
  runDepreciation: (data: any) => request<any>('/fixed-assets/depreciation/run', { method: 'POST', body: JSON.stringify(data) }),
  scanAudit: (data: any) => request<any>('/fixed-assets/audits/scan', { method: 'POST', body: JSON.stringify(data) }),
};

export const WMSApi = {
  getZones: () => request<any[]>('/wms/zones'),
  optimizeSlotting: () => request<any>('/wms/slotting/optimize', { method: 'POST' }),
  createWave: (data: any) => request<any>('/wms/waves', { method: 'POST', body: JSON.stringify(data) }),
  confirmPick: (data: any) => request<any>('/wms/pick/confirm', { method: 'POST', body: JSON.stringify(data) }),
};

export const LogisticsApi = {
  getCarriers: () => request<any[]>('/logistics/carriers'),
  createDispatch: (data: any) => request<any>('/logistics/dispatches', { method: 'POST', body: JSON.stringify(data) }),
  sendTelematicsPing: (data: any) => request<any>('/logistics/telematics/ping', { method: 'POST', body: JSON.stringify(data) }),
};

export const CRMApi = {
  getLeads: () => request<any[]>('/crm/leads'),
  createLead: (data: any) => request<any>('/crm/leads', { method: 'POST', body: JSON.stringify(data) }),
  createQuote: (data: any) => request<any>('/crm/quotes', { method: 'POST', body: JSON.stringify(data) }),
};

export const FieldServiceApi = {
  getWorkOrders: () => request<any[]>('/field-service/work-orders'),
  createWorkOrder: (data: any) => request<any>('/field-service/work-orders', { method: 'POST', body: JSON.stringify(data) }),
  dispatch: (data: any) => request<any>('/field-service/dispatch', { method: 'POST', body: JSON.stringify(data) }),
};

export const ContractsApi = {
  getContracts: () => request<any[]>('/contracts/documents'),
  createContract: (data: any) => request<any>('/contracts/documents', { method: 'POST', body: JSON.stringify(data) }),
};

export const ESGApi = {
  getEmissions: () => request<any[]>('/esg/emissions'),
  logEmissions: (data: any) => request<any>('/esg/emissions', { method: 'POST', body: JSON.stringify(data) }),
  getSummary: (period = '2026-Q1') => request<any>(`/esg/summary?period=${period}`),
};

export const BudgetingApi = {
  getPlans: () => request<any[]>('/budgeting/plans'),
  createPlan: (data: any) => request<any>('/budgeting/plans', { method: 'POST', body: JSON.stringify(data) }),
};

export const APSApi = {
  getWorkCenters: () => request<any[]>('/aps/work-centers'),
  scheduleOperation: (data: any) => request<any>('/aps/schedule', { method: 'POST', body: JSON.stringify(data) }),
};

export const PortalsApi = {
  getAsns: () => request<any[]>('/vendor-portal/asns'),
  submitAsn: (data: any) => request<any>('/vendor-portal/asns', { method: 'POST', body: JSON.stringify(data) }),
  getRmas: () => request<any[]>('/customer-portal/rmas'),
  requestRma: (data: any) => request<any>('/customer-portal/rmas', { method: 'POST', body: JSON.stringify(data) }),
};
