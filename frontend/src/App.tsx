import React, { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Sidebar, PageId } from './components/layout/Sidebar';
import { DemoModal } from './components/layout/DemoModal';
import { Overview } from './pages/Overview';
import { Infrastructure } from './pages/Infrastructure';
import { FailureSimulator } from './pages/FailureSimulator';
import { AIRecovery } from './pages/AIRecovery';
import { AlgorithmLab } from './pages/AlgorithmLab';
import { Experiments } from './pages/Experiments';
import { Reports } from './pages/Reports';
import { api } from './services/api';
import { SimulationState, EventLogEntry } from './types';

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('overview');
  const [simulationState, setSimulationState] = useState<SimulationState | null>(null);
  const [events, setEvents] = useState<EventLogEntry[]>([]);
  const [highlightedRouteEdges, setHighlightedRouteEdges] = useState<string[]>([]);
  const [isDemoOpen, setIsDemoOpen] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);

  const fetchSimulationState = async () => {
    try {
      const state = await api.getSimulationState();
      setSimulationState(state);
      const evs = await api.getFailureHistory();
      setEvents(evs);
    } catch (err) {
      console.error('Error fetching simulation state:', err);
    }
  };

  useEffect(() => {
    fetchSimulationState();
  }, []);

  const handleReset = async () => {
    setIsResetting(true);
    try {
      await api.resetSimulation();
      setHighlightedRouteEdges([]);
      await fetchSimulationState();
    } catch (err) {
      console.error('Error resetting simulation:', err);
    } finally {
      setIsResetting(false);
    }
  };

  const handleSelectScenario = async (scenarioId: string) => {
    try {
      await api.loadPreset(scenarioId);
      await fetchSimulationState();
    } catch (err) {
      console.error('Error loading preset scenario:', err);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background text-zinc-100 font-sans">
      {/* Top Navigation */}
      <Navbar
        activeScenario={simulationState?.active_scenario || 'Equilibrium'}
        metrics={simulationState?.metrics || null}
        onReset={handleReset}
        onOpenDemo={() => setIsDemoOpen(true)}
        isResetting={isResetting}
      />

      {/* Main Workspace Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Navigation Sidebar */}
        <Sidebar
          currentPage={currentPage}
          onSelectPage={setCurrentPage}
          unservedDemand={simulationState?.metrics?.unserved_demand || 0}
        />

        {/* Content Viewport */}
        <main className="flex-1 overflow-hidden bg-[#090a0f] relative">
          {currentPage === 'overview' && (
            <Overview
              metrics={simulationState?.metrics || null}
              network={simulationState?.network || null}
              events={events}
              onNavigate={setCurrentPage}
            />
          )}

          {currentPage === 'map' && (
            <Infrastructure
              network={simulationState?.network || null}
              metrics={simulationState?.metrics || null}
              highlightedRouteEdges={highlightedRouteEdges}
            />
          )}

          {currentPage === 'simulator' && (
            <FailureSimulator
              network={simulationState?.network || null}
              metrics={simulationState?.metrics || null}
              events={events}
              onRefreshState={fetchSimulationState}
            />
          )}

          {currentPage === 'recovery' && (
            <AIRecovery
              network={simulationState?.network || null}
              metrics={simulationState?.metrics || null}
              onRefreshState={fetchSimulationState}
              onHighlightRoute={(edges) => {
                setHighlightedRouteEdges(edges);
                setCurrentPage('map');
              }}
            />
          )}

          {currentPage === 'lab' && (
            <AlgorithmLab network={simulationState?.network || null} />
          )}

          {currentPage === 'experiments' && <Experiments />}

          {currentPage === 'reports' && <Reports />}
        </main>
      </div>

      {/* Presentation / Demo Walkthrough Modal */}
      <DemoModal
        isOpen={isDemoOpen}
        onClose={() => setIsDemoOpen(false)}
        onSelectScenario={handleSelectScenario}
        onNavigate={setCurrentPage}
      />
    </div>
  );
}
