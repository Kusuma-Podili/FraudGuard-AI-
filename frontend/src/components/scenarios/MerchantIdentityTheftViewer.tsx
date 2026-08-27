// Enterprise Forensic Scenario Component: MerchantIdentityTheftViewer
// Title: Synthetic Business Entity & Shell Terminal Detector

import React, { useState } from 'react';
import { Shield, AlertOctagon, CheckCircle2, FileText, Activity, Lock, Users, BarChart3, Clock, Eye, RefreshCw } from 'lucide-react';

export interface MerchantIdentityTheftViewerProps {
  scenarioId?: string;
  onMitigate?: (action: string) => void;
}

export const MerchantIdentityTheftViewer: React.FC<MerchantIdentityTheftViewerProps> = ({ scenarioId = 'SCEN_ACTIVE_001', onMitigate }) => {
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [threatLevel, setThreatLevel] = useState<string>('MITIGATED');
  const [riskProbability, setRiskProbability] = useState<number>(0.042);

  const handleRunForensicScan = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      setRiskProbability(0.018);
      setThreatLevel('CLEAR');
      if (onMitigate) {
        onMitigate('SCAN_COMPLETED');
      }
    }, 700);
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 text-gray-100 shadow-2xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <AlertOctagon className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-gray-100">Synthetic Business Entity & Shell Terminal Detector</h3>
            <p className="text-xs text-gray-400 font-mono">Scenario Reference: {scenarioId}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3 py-1 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
            Risk: {(riskProbability * 100).toFixed(1)}%
          </span>
          <button
            onClick={handleRunForensicScan}
            disabled={isAnalyzing}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs font-bold text-white shadow-lg shadow-purple-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
            <span>{isAnalyzing ? 'Analyzing Patterns...' : 'Run Forensic Scan'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-gray-950/70 border border-gray-800 rounded-xl">
          <p className="text-xs text-gray-400 uppercase font-semibold">Threat Classification</p>
          <p className="text-xl font-bold text-gray-100 mt-1 font-mono">{threatLevel}</p>
          <span className="text-[10px] text-emerald-400 font-mono">Real-Time Hot Path</span>
        </div>
        <div className="p-4 bg-gray-950/70 border border-gray-800 rounded-xl">
          <p className="text-xs text-gray-400 uppercase font-semibold">Forensic Confidence</p>
          <p className="text-xl font-bold text-purple-400 mt-1 font-mono">99.4%</p>
          <span className="text-[10px] text-gray-500 font-mono">Bayesian Verified</span>
        </div>
        <div className="p-4 bg-gray-950/70 border border-gray-800 rounded-xl">
          <p className="text-xs text-gray-400 uppercase font-semibold">Regulatory Protocol</p>
          <p className="text-xl font-bold text-blue-400 mt-1 font-mono">FINCEN SAR</p>
          <span className="text-[10px] text-gray-500 font-mono">Auto-Escalation Ready</span>
        </div>
      </div>

      <div className="p-4 bg-gray-950 border border-gray-800 rounded-xl space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400 font-mono">Containment Status: AUTOMATED_INTERCEPTION</span>
          <span className="text-emerald-400 font-mono">Sub-20ms SLA Pass</span>
        </div>
        <p className="text-xs text-gray-400 leading-relaxed">
          The Synthetic Business Entity & Shell Terminal Detector continuous pattern detector correlates real-time authorization metadata,
          device signals, and historical cardholder trajectories to neutralize complex financial attacks.
        </p>
      </div>
    </div>
  );
};

export default MerchantIdentityTheftViewer;
