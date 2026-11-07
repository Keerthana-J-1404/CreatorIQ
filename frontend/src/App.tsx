import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ChannelProvider } from './context/ChannelContext';
import { Layout } from './components/Layout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ContentIntelligencePage } from './pages/ContentIntelligencePage';
import { AIStrategistPage } from './pages/AIStrategistPage';
import { MemoryCenterPage } from './pages/MemoryCenterPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  return (
    <ChannelProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/intelligence" element={<ContentIntelligencePage />} />
            <Route path="/strategist" element={<AIStrategistPage />} />
            <Route path="/memory" element={<MemoryCenterPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ChannelProvider>
  );
}

export default App;
