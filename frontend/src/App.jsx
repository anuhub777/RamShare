import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { ProviderDashboard } from './pages/ProviderDashboard';
import { ConsumerDashboard } from './pages/ConsumerDashboard';
import { MarketplacePage } from './pages/MarketplacePage';
import { ProviderDetailPage } from './pages/ProviderDetailPage';
import { SubmitWorkloadPage } from './pages/SubmitWorkloadPage';
import { JobDetailPage } from './pages/JobDetailPage';
import { JobHistoryPage } from './pages/JobHistoryPage';
import { CreditWalletPage } from './pages/CreditWalletPage';
import { ProfilePage } from './pages/ProfilePage';
import { LoadingSpinner } from './components/common/LoadingSpinner';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <LoadingSpinner label="Authenticating session..." />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <DashboardLayout>{children}</DashboardLayout>;
};

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/provider" element={<ProtectedRoute><ProviderDashboard /></ProtectedRoute>} />
          <Route path="/consumer" element={<ProtectedRoute><ConsumerDashboard /></ProtectedRoute>} />
          <Route path="/marketplace" element={<ProtectedRoute><MarketplacePage /></ProtectedRoute>} />
          <Route path="/marketplace/:providerId" element={<ProtectedRoute><ProviderDetailPage /></ProtectedRoute>} />
          <Route path="/submit-job" element={<ProtectedRoute><SubmitWorkloadPage /></ProtectedRoute>} />
          <Route path="/jobs" element={<ProtectedRoute><JobHistoryPage /></ProtectedRoute>} />
          <Route path="/jobs/:jobId" element={<ProtectedRoute><JobDetailPage /></ProtectedRoute>} />
          <Route path="/credits" element={<ProtectedRoute><CreditWalletPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
