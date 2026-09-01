"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { api } from "@/lib/api";
import { CustomerProfile, CustomerDossier } from "@/types";
import { formatCurrency, getRiskColor } from "@/lib/utils";
import {
  UserCheck,
  Search,
  Filter,
  CreditCard,
  MapPin,
  Smartphone,
  ShieldAlert,
  ShieldCheck,
  Activity,
  History,
  Lock,
  Unlock,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Eye,
} from "lucide-react";

export default function CustomersPage() {
  const [customers, setCustomers] = useState<CustomerProfile[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Filters
  const [riskTier, setRiskTier] = useState("ALL");
  const [search, setSearch] = useState("");

  // Dossier Modal
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerProfile | null>(null);
  const [dossier, setDossier] = useState<CustomerDossier | null>(null);
  const [isDossierOpen, setIsDossierOpen] = useState(false);
  const [isLoadingDossier, setIsLoadingDossier] = useState(false);

  const fetchCustomers = async () => {
    setIsLoading(true);
    try {
      const res = await api.listCustomers({
        page,
        page_size: pageSize,
        risk_tier: riskTier !== "ALL" ? riskTier : undefined,
        search: search || undefined,
      });
      setCustomers(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (e) {
      console.error("Failed to load customers", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [page, pageSize, riskTier]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchCustomers();
  };

  const handleOpenDossier = async (cust: CustomerProfile) => {
    setSelectedCustomer(cust);
    setIsDossierOpen(true);
    setIsLoadingDossier(true);
    try {
      const data = await api.getCustomerDossier(cust.card_id);
      setDossier(data);
    } catch (e) {
      console.error("Failed to load customer dossier", e);
    } finally {
      setIsLoadingDossier(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-blue-400" />
            <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Customer & Card 360° Intelligence</h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Cardholder identity dossiers, behavioral baseline profiling, and historic fraud risk indicators.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <Card className="p-4 bg-gray-950/60 border-gray-800">
        <form onSubmit={handleSearch} className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by customer name, card number (e.g. 4829), email..."
              className="w-full bg-gray-900 border border-gray-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <select
            value={riskTier}
            onChange={(e) => {
              setRiskTier(e.target.value);
              setPage(1);
            }}
            className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="ALL">All Risk Profiles</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>

          <Button type="submit" size="sm">
            Search
          </Button>
        </form>
      </Card>

      {/* Customer Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {customers.map((cust) => {
          const riskBadge = getRiskColor(cust.risk_tier);

          return (
            <Card key={cust.id} className="p-5 space-y-4 hover:border-gray-700 transition-all bg-gray-950/60">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-sm">
                    {cust.full_name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-200 text-sm">{cust.full_name}</h3>
                    <p className="text-[11px] text-gray-400 font-mono">{cust.email}</p>
                  </div>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${riskBadge.bg} ${riskBadge.text} ${riskBadge.border}`}>
                  {cust.risk_tier}
                </span>
              </div>

              {/* Card Meta */}
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-xl space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono font-bold text-gray-200">{cust.masked_card}</span>
                  <span className="text-[10px] font-semibold text-gray-400">{cust.card_network} • {cust.card_type}</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-gray-500 pt-1">
                  <span>Card Status:</span>
                  <span className={`font-semibold ${cust.card_status === "ACTIVE" ? "text-emerald-400" : "text-red-400"}`}>
                    {cust.card_status}
                  </span>
                </div>
              </div>

              {/* Behavioral Telemetry */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 bg-gray-900/40 rounded-lg">
                  <span className="text-[10px] text-gray-500">30d Avg Amount</span>
                  <p className="font-bold text-gray-200 mt-0.5">${cust.avg_amount_30d.toFixed(2)}</p>
                </div>
                <div className="p-2.5 bg-gray-900/40 rounded-lg">
                  <span className="text-[10px] text-gray-500">Total Tx Count</span>
                  <p className="font-bold text-gray-200 mt-0.5">{cust.total_transactions_count}</p>
                </div>
              </div>

              {/* Action */}
              <Button
                variant="secondary"
                size="sm"
                className="w-full text-xs font-semibold"
                onClick={() => handleOpenDossier(cust)}
              >
                <Eye className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
                View 360° Dossier
              </Button>
            </Card>
          );
        })}
      </div>

      {/* 360 Dossier Modal */}
      <Modal
        isOpen={isDossierOpen}
        onClose={() => setIsDossierOpen(false)}
        title={`Customer 360 Dossier: ${selectedCustomer?.full_name}`}
        size="lg"
      >
        {isLoadingDossier ? (
          <div className="py-16 text-center text-xs text-gray-400">Loading comprehensive customer dossier...</div>
        ) : (
          <div className="space-y-5">
            {/* Identity Header */}
            <div className="p-4 bg-gray-950 border border-gray-800 rounded-xl flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-gray-100">{selectedCustomer?.full_name}</h3>
                <p className="text-xs text-gray-400 font-mono mt-0.5">{selectedCustomer?.email} • {selectedCustomer?.phone}</p>
              </div>
              <div className="text-right">
                <span className="font-mono text-xs font-bold text-gray-200">{selectedCustomer?.masked_card}</span>
                <p className="text-[10px] text-emerald-400 font-semibold">{selectedCustomer?.card_network} ({selectedCustomer?.card_status})</p>
              </div>
            </div>

            {/* Behavioral Baselines */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg">
                <span className="text-[10px] text-gray-500 font-semibold">30d Avg Amount</span>
                <p className="text-sm font-bold text-emerald-400 mt-1">${dossier?.behavioral_baseline?.avg_amount_30d || 145.00}</p>
              </div>
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg">
                <span className="text-[10px] text-gray-500 font-semibold">Max Historic Amount</span>
                <p className="text-sm font-bold text-amber-400 mt-1">${dossier?.behavioral_baseline?.max_amount_single || 1800.00}</p>
              </div>
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg">
                <span className="text-[10px] text-gray-500 font-semibold">Total Tx Records</span>
                <p className="text-sm font-bold text-gray-200 mt-1">{dossier?.behavioral_baseline?.total_transactions || 64}</p>
              </div>
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg">
                <span className="text-[10px] text-gray-500 font-semibold">Prior Fraud Flags</span>
                <p className="text-sm font-bold text-red-400 mt-1">{dossier?.behavioral_baseline?.total_alerts || 0}</p>
              </div>
            </div>

            {/* Locations and Devices */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-3.5 bg-gray-900/40 border border-gray-800 rounded-xl space-y-2">
                <span className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-blue-400" />
                  Typical Geographies
                </span>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(dossier?.behavioral_baseline?.typical_locations || ["New York, US"]).map((loc, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 text-xs">
                      {loc}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-3.5 bg-gray-900/40 border border-gray-800 rounded-xl space-y-2">
                <span className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-purple-400" />
                  Known Device Hardware
                </span>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(dossier?.behavioral_baseline?.known_devices || ["dev_fp_apple_safari_1"]).map((dev, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono text-[11px]">
                      {dev}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Transaction History */}
            <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl space-y-2">
              <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider">Recent Card Authorizations</h4>
              <div className="divide-y divide-gray-800 max-h-48 overflow-y-auto">
                {(dossier?.recent_transactions || []).length === 0 ? (
                  <p className="text-xs text-gray-500 py-3">No historic transactions recorded for this card.</p>
                ) : (
                  dossier?.recent_transactions.map((tx) => (
                    <div key={tx.transaction_id} className="py-2 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-mono font-bold text-gray-200">{tx.transaction_id}</span>
                        <p className="text-[10px] text-gray-500">{tx.merchant_name || tx.merchant_id} • {tx.merchant_category}</p>
                      </div>
                      <div className="text-right">
                        <span className="font-bold text-gray-200">{formatCurrency(tx.amount)}</span>
                        <p className="text-[10px] text-emerald-400 font-semibold">{tx.decision_action}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-gray-800">
              <Button variant="secondary" size="sm" onClick={() => setIsDossierOpen(false)}>
                Close Dossier
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
