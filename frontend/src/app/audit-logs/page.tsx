"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { api } from "@/lib/api";
import {
  History,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Eye,
} from "lucide-react";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [totalPages, setTotalPages] = useState(1);
  const [actionType, setActionType] = useState("ALL");
  const [isLoading, setIsLoading] = useState(false);

  const [selectedLog, setSelectedLog] = useState<any | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const res = await api.listAuditLogs({
        page,
        page_size: pageSize,
        action_type: actionType !== "ALL" ? actionType : undefined,
      });
      setLogs(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (e) {
      console.error("Failed to load audit logs", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, pageSize, actionType]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <History className="w-6 h-6 text-gray-800" />
            <h1 className="text-2xl font-bold text-[#111827] tracking-tight">Compliance Audit Trail</h1>
          </div>
          <p className="text-xs text-[#4B5563] mt-1">
            Cryptographically sealed, immutable ledger of all administrative and analyst security operations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchLogs} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filter Control */}
      <Card className="p-4 bg-white border-[#E5E7EB]">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs font-semibold text-[#4B5563]">Action Type:</span>
          <select
            value={actionType}
            onChange={(e) => {
              setActionType(e.target.value);
              setPage(1);
            }}
            className="bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg px-3 py-1.5 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
          >
            <option value="ALL">All Recorded Actions</option>
            <option value="USER_LOGIN">USER_LOGIN</option>
            <option value="CASE_STATUS_UPDATE">CASE_STATUS_UPDATE</option>
            <option value="USER_CREATED">USER_CREATED</option>
            <option value="USER_UPDATED">USER_UPDATED</option>
            <option value="USER_PASSWORD_RESET">USER_PASSWORD_RESET</option>
            <option value="SETTINGS_RISK_THRESHOLDS_UPDATE">SETTINGS_RISK_THRESHOLDS_UPDATE</option>
            <option value="SETTINGS_NOTIFICATIONS_UPDATE">SETTINGS_NOTIFICATIONS_UPDATE</option>
            <option value="ALERT_ASSIGNMENT">ALERT_ASSIGNMENT</option>
            <option value="ALERT_STATUS_UPDATE">ALERT_STATUS_UPDATE</option>
            <option value="ALERT_CONVERTED_TO_CASE">ALERT_CONVERTED_TO_CASE</option>
          </select>
        </div>
      </Card>

      {/* Logs Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#111827]">
            <thead className="bg-[#F9FAFB] text-[11px] text-[#4B5563] uppercase tracking-wider border-b border-[#E5E7EB]">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Timestamp</th>
                <th className="py-3.5 px-4 font-semibold">Actor Email</th>
                <th className="py-3.5 px-4 font-semibold">Action</th>
                <th className="py-3.5 px-4 font-semibold">Resource</th>
                <th className="py-3.5 px-4 font-semibold">Summary</th>
                <th className="py-3.5 px-4 font-semibold text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E7EB]">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-[#9CA3AF]">
                    No compliance audit logs match the query.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4 font-mono text-[11px] text-[#4B5563]">
                      {log.created_at ? new Date(log.created_at).toLocaleString() : "N/A"}
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-[#111827]">{log.user_email}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-800 border border-gray-300 font-mono text-[10px] font-bold">
                        {log.action_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-[#4B5563]">
                      {log.resource_type}: {log.resource_id}
                    </td>
                    <td className="py-3 px-4 text-[#111827] max-w-sm truncate">{log.change_summary}</td>
                    <td className="py-3 px-4 text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedLog(log);
                          setIsDetailOpen(true);
                        }}
                        className="text-[11px]"
                      >
                        <Eye className="w-3 h-3 mr-1 text-gray-700" />
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-[#E5E7EB] flex items-center justify-between text-xs text-[#4B5563]">
          <div>
            Showing <strong className="text-[#111827]">{(page - 1) * pageSize + 1}</strong> to{" "}
            <strong className="text-[#111827]">{Math.min(page * pageSize, total)}</strong> of{" "}
            <strong className="text-[#111827]">{total}</strong> audit entries
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page <= 1}
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Button>
            <span className="text-xs text-[#111827] font-medium px-2">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              disabled={page >= totalPages}
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>

      {/* Log Detail Modal */}
      <Modal isOpen={isDetailOpen} onClose={() => setIsDetailOpen(false)} title="Audit Record Inspector" size="md">
        {selectedLog && (
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-[#F9FAFB] rounded-lg border border-[#E5E7EB] space-y-1">
              <div className="flex justify-between">
                <span className="text-[#4B5563]">Action:</span>
                <span className="font-bold text-gray-900">{selectedLog.action_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#4B5563]">Actor:</span>
                <span className="font-mono text-[#111827]">{selectedLog.user_email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#4B5563]">Resource:</span>
                <span className="font-mono text-[#111827]">{selectedLog.resource_type}: {selectedLog.resource_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#4B5563]">IP Address:</span>
                <span className="font-mono text-[#111827]">{selectedLog.ip_address || "127.0.0.1"}</span>
              </div>
            </div>

            <div className="space-y-2">
              <span className="font-bold text-[#111827] uppercase tracking-wider">Payload Changes</span>
              <pre className="p-3 bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg text-[#111827] font-mono text-[11px] overflow-x-auto">
                {JSON.stringify(
                  {
                    before_state: selectedLog.before_state,
                    after_state: selectedLog.after_state,
                  },
                  null,
                  2
                )}
              </pre>
            </div>

            <div className="flex justify-end pt-2 border-t border-[#E5E7EB]">
              <Button variant="secondary" size="sm" onClick={() => setIsDetailOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
