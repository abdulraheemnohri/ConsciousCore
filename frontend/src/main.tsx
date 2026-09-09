import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import './app-v3.css';

import { AppState } from './types';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { CommandPalette } from './CommandPalette';

import { OnboardingPage } from './pages/OnboardingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ChatPage } from './pages/ChatPage';
import { GlobalWorkspacePage } from './pages/GlobalWorkspacePage';
import { AttentionCenterPage } from './pages/AttentionCenterPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { SkillsPage } from './pages/SkillsPage';
import { LearningPage } from './pages/LearningPage';
import { MemoryCenterPage } from './pages/MemoryCenterPage';
import { MemoryFederationPage } from './pages/MemoryFederationPage';
import { SelfModelPage } from './pages/SelfModelPage';
import { WorldModelPage } from './pages/WorldModelPage';
import { AINetworkPage } from './pages/AINetworkPage';
import { AIConversationsPage } from './pages/AIConversationsPage';
import { AgentsPage } from './pages/AgentsPage';
import { ExperimentsPage } from './pages/ExperimentsPage';
import { CodeLabPage } from './pages/CodeLabPage';
import { GoalsPage } from './pages/GoalsPage';
import { PlannerPage } from './pages/PlannerPage';
import { ReasoningPage } from './pages/ReasoningPage';
import { ReflectionPage } from './pages/ReflectionPage';
import { MetacognitionPage } from './pages/MetacognitionPage';
import { PredictionPage } from './pages/PredictionPage';
import { SimulationPage } from './pages/SimulationPage';
import { InternalStatePage } from './pages/InternalStatePage';
import { SleepPage } from './pages/SleepPage';
import { ToolCenterPage } from './pages/ToolCenterPage';
import { SafetyCenterPage } from './pages/SafetyCenterPage';
import { SecurityPage } from './pages/SecurityPage';
import { SystemPage } from './pages/SystemPage';
import { ActivityPage } from './pages/ActivityPage';
import { RuntimeCenterPage } from './pages/RuntimeCenterPage';
import { ModelsPage } from './pages/ModelsPage';
import { ParallelAIPage } from './pages/ParallelAIPage';
import { DistributedNodesPage } from './pages/DistributedNodesPage';
import { TelemetryPage } from './pages/TelemetryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { LogsPage } from './pages/LogsPage';
import { DeveloperConsolePage } from './pages/DeveloperConsolePage';
import { SettingsPage } from './pages/SettingsPage';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function App() {
  const [page, setPage] = useState('Dashboard');
  const [state, setState] = useState<AppState>({});
  const [cmdOpen, setCmdOpen] = useState(false);

  const loadState = async () => {
    try {
      const res = await fetch(`${API}/api/state`);
      if (res.ok) {
        const data = await res.json();
        setState(data);
      }
    } catch {}
  };

  useEffect(() => {
    loadState();
    const timer = setInterval(loadState, 5000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    (window as any).__cc_toggle_cmd = () => setCmdOpen(prev => !prev);
  }, []);

  const renderPage = () => {
    switch (page) {
      case 'Onboarding':
        return <OnboardingPage />;
      case 'Dashboard':
        return <DashboardPage state={state} onNavigate={setPage} />;
      case 'Chat Workspace':
        return <ChatPage state={state} onRefresh={loadState} />;
      case 'Global Workspace':
        return <GlobalWorkspacePage state={state} onRefresh={loadState} />;
      case 'Attention Center':
        return <AttentionCenterPage state={state} onRefresh={loadState} />;
      case 'Knowledge':
        return <KnowledgePage />;
      case 'Skills':
        return <SkillsPage />;
      case 'Learning':
        return <LearningPage />;
      case 'Memory':
        return <MemoryCenterPage state={state} onRefresh={loadState} />;
      case 'Memory Federation':
        return <MemoryFederationPage state={state} onRefresh={loadState} />;
      case 'Self Model':
        return <SelfModelPage state={state} onRefresh={loadState} />;
      case 'World Model':
        return <WorldModelPage state={state} onRefresh={loadState} />;
      case 'AI Network':
        return <AINetworkPage />;
      case 'AI Conversations':
        return <AIConversationsPage />;
      case 'Agents':
        return <AgentsPage />;
      case 'Experiments':
        return <ExperimentsPage />;
      case 'Code Lab':
        return <CodeLabPage />;
      case 'Goals':
        return <GoalsPage state={state} onRefresh={loadState} />;
      case 'Planner':
        return <PlannerPage state={state} onRefresh={loadState} />;
      case 'Reasoning':
        return <ReasoningPage state={state} />;
      case 'Reflection':
        return <ReflectionPage state={state} onRefresh={loadState} />;
      case 'Metacognition':
        return <MetacognitionPage state={state} />;
      case 'Prediction':
        return <PredictionPage state={state} />;
      case 'Simulation':
        return <SimulationPage state={state} />;
      case 'Internal State':
        return <InternalStatePage state={state} />;
      case 'Sleep':
        return <SleepPage state={state} onRefresh={loadState} />;
      case 'Tools':
        return <ToolCenterPage state={state} onRefresh={loadState} />;
      case 'Safety':
        return <SafetyCenterPage state={state} onRefresh={loadState} />;
      case 'Security':
        return <SecurityPage />;
      case 'System':
        return <SystemPage />;
      case 'Activity':
        return <ActivityPage />;
      case 'Runtime Center':
        return <RuntimeCenterPage state={state} onRefresh={loadState} />;
      case 'Models':
        return <ModelsPage state={state} onRefresh={loadState} />;
      case 'Parallel AI':
        return <ParallelAIPage state={state} />;
      case 'Distributed Nodes':
        return <DistributedNodesPage state={state} />;
      case 'Telemetry':
        return <TelemetryPage state={state} />;
      case 'Analytics':
        return <AnalyticsPage state={state} />;
      case 'Logs':
        return <LogsPage state={state} />;
      case 'Developer Console':
        return <DeveloperConsolePage state={state} onRefresh={loadState} />;
      case 'Settings':
        return <SettingsPage state={state} onRefresh={loadState} />;
      default:
        return <DashboardPage state={state} onNavigate={setPage} />;
    }
  };

  return (
    <div className="cc">
      <Sidebar
        currentPage={page}
        onNavigate={setPage}
        autonomyLevel={state.safety?.autonomy_level}
      />
      <main className="main">
        <Header
          currentPage={page}
          state={state}
          onOpenCommandPalette={() => setCmdOpen(true)}
          onRefresh={loadState}
        />
        {renderPage()}
      </main>

      <CommandPalette
        isOpen={cmdOpen}
        onClose={() => setCmdOpen(false)}
        onNavigate={setPage}
      />
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
