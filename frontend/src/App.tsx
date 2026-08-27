import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Financials } from './pages/Financials';
import { AccountsPayable } from './pages/AccountsPayable';
import { AccountsReceivable } from './pages/AccountsReceivable';
import { Inventory } from './pages/Inventory';
import { Procurement } from './pages/Procurement';
import { Sales } from './pages/Sales';
import { Manufacturing } from './pages/Manufacturing';
import { QualityControl } from './pages/QualityControl';
import { HumanResources } from './pages/HumanResources';
import { Projects } from './pages/Projects';
import { Analytics } from './pages/Analytics';
import { CurrencyRevaluationPage } from './pages/financials/CurrencyRevaluationPage';
import { BankReconciliationPage } from './pages/financials/BankReconciliationPage';
import { FixedAssetRegisterPage } from './pages/financials/FixedAssetRegisterPage';
import { RFQAuctionPage } from './pages/procurement/RFQAuctionPage';
import { FiniteCapacityGanttPage } from './pages/manufacturing/FiniteCapacityGanttPage';
import { SPCControlChartsPage } from './pages/quality/SPCControlChartsPage';
import { AltmanDuPontPage } from './pages/analytics/AltmanDuPontPage';
import { PricingCalculatorPage } from './pages/sales/PricingCalculatorPage';
import { CompensationEquityPage } from './pages/hr/CompensationEquityPage';
import { WavePickingGenealogyPage } from './pages/inventory/WavePickingGenealogyPage';
import { AuditTrailViewerPage } from './pages/governance/AuditTrailViewerPage';
import { ServiceManagement } from './pages/ServiceManagement';
import { CRM } from './pages/CRM';
import { FinancialControls } from './pages/FinancialControls';
import { Notifications } from './pages/Notifications';
import { TreasuryManagement } from './pages/TreasuryManagement';
import { FixedAssetsManagement } from './pages/FixedAssetsManagement';
import { AdvancedWMS } from './pages/AdvancedWMS';
import { LogisticsFleet } from './pages/LogisticsFleet';
import { CRMLeadsPipeline } from './pages/CRMLeadsPipeline';
import { FieldServiceOperations } from './pages/FieldServiceOperations';
import { ContractLifecycle } from './pages/ContractLifecycle';
import { ESGComplianceReporting } from './pages/ESGComplianceReporting';
import { StrategicBudgeting } from './pages/StrategicBudgeting';
import { ProductionSchedulingAPS } from './pages/ProductionSchedulingAPS';
import { VendorCollaborationPortal } from './pages/VendorCollaborationPortal';
import { CustomerSelfServicePortal } from './pages/CustomerSelfServicePortal';
import { ExecutiveIntelligence } from './pages/ExecutiveIntelligence';
import { GlobalAuditInspection } from './pages/GlobalAuditInspection';
import { TaxCompliancePortal } from './pages/TaxCompliancePortal';
import { SubscriptionBillingPortal } from './pages/SubscriptionBillingPortal';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="h-screen bg-slate-950 flex items-center justify-center text-slate-400">Loading NexERP...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="financials" element={<Financials />} />
            <Route path="financials/controls" element={<FinancialControls />} />
            <Route path="financials/treasury" element={<TreasuryManagement />} />
            <Route path="financials/fixed-assets-management" element={<FixedAssetsManagement />} />
            <Route path="financials/budgeting" element={<StrategicBudgeting />} />
            <Route path="financials/tax-compliance" element={<TaxCompliancePortal />} />
            <Route path="financials/subscription-billing" element={<SubscriptionBillingPortal />} />
            <Route path="notifications" element={<Notifications />} />
            <Route path="financials/revaluation" element={<CurrencyRevaluationPage />} />
            <Route path="financials/reconciliation" element={<BankReconciliationPage />} />
            <Route path="financials/fixed-assets" element={<FixedAssetRegisterPage />} />
            <Route path="accounts-payable" element={<AccountsPayable />} />
            <Route path="accounts-receivable" element={<AccountsReceivable />} />
            <Route path="inventory" element={<Inventory />} />
            <Route path="inventory/genealogy" element={<WavePickingGenealogyPage />} />
            <Route path="inventory/advanced-wms" element={<AdvancedWMS />} />
            <Route path="logistics/fleet" element={<LogisticsFleet />} />
            <Route path="procurement" element={<Procurement />} />
            <Route path="procurement/rfq" element={<RFQAuctionPage />} />
            <Route path="procurement/vendor-portal" element={<VendorCollaborationPortal />} />
            <Route path="sales" element={<Sales />} />
            <Route path="sales/crm" element={<CRM />} />
            <Route path="sales/crm-pipeline" element={<CRMLeadsPipeline />} />
            <Route path="sales/contracts" element={<ContractLifecycle />} />
            <Route path="sales/pricing" element={<PricingCalculatorPage />} />
            <Route path="customer-portal" element={<CustomerSelfServicePortal />} />
            <Route path="manufacturing" element={<Manufacturing />} />
            <Route path="manufacturing/gantt" element={<FiniteCapacityGanttPage />} />
            <Route path="manufacturing/aps" element={<ProductionSchedulingAPS />} />
            <Route path="quality" element={<QualityControl />} />
            <Route path="quality/spc" element={<SPCControlChartsPage />} />
            <Route path="hr" element={<HumanResources />} />
            <Route path="hr/compensation" element={<CompensationEquityPage />} />
            <Route path="projects" element={<Projects />} />
            <Route path="field-service" element={<FieldServiceOperations />} />
            <Route path="compliance/esg" element={<ESGComplianceReporting />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="analytics/solvency" element={<AltmanDuPontPage />} />
            <Route path="analytics/executive" element={<ExecutiveIntelligence />} />
            <Route path="governance/audit" element={<AuditTrailViewerPage />} />
            <Route path="governance/audit-inspection" element={<GlobalAuditInspection />} />
            <Route path="service-management" element={<ServiceManagement />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};
