"use client";

import React from "react";
import { TransactionRecord } from "@/types";
import { formatCurrency, getActionBadge, getRiskColor, formatTimeAgo } from "@/lib/utils";
import { Eye, ShieldAlert } from "lucide-react";

interface TransactionTableProps {
  transactions: TransactionRecord[];
  onSelectTransaction?: (tx: TransactionRecord) => void;
}

export const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  onSelectTransaction,
}) => {
  return (
    <div className="w-full overflow-x-auto rounded-xl border border-gray-800 bg-gray-900/60">
      <table className="w-full text-left text-xs text-gray-300">
        <thead className="bg-gray-950/80 text-[11px] text-gray-400 uppercase tracking-wider border-b border-gray-800">
          <tr>
            <th className="py-3.5 px-4 font-semibold">Transaction ID</th>
            <th className="py-3.5 px-4 font-semibold">Card / User</th>
            <th className="py-3.5 px-4 font-semibold">Amount</th>
            <th className="py-3.5 px-4 font-semibold">Merchant / Category</th>
            <th className="py-3.5 px-4 font-semibold">Risk Score</th>
            <th className="py-3.5 px-4 font-semibold">Decision</th>
            <th className="py-3.5 px-4 font-semibold">Time</th>
            <th className="py-3.5 px-4 font-semibold text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800/60">
          {transactions.length === 0 ? (
            <tr>
              <td colSpan={8} className="py-8 text-center text-gray-500">
                No transactions matching query criteria.
              </td>
            </tr>
          ) : (
            transactions.map((tx) => {
              const badge = getActionBadge(tx.decision_action);
              const riskColors = getRiskColor(tx.risk_tier);

              return (
                <tr key={tx.id || tx.transaction_id} className="hover:bg-gray-800/40 transition-colors group">
                  <td className="py-3 px-4 font-mono font-medium text-gray-200">
                    {tx.transaction_id}
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-mono text-gray-300">{tx.card_id}</div>
                    <div className="text-[10px] text-gray-500">{tx.cardholder_id}</div>
                  </td>
                  <td className="py-3 px-4 font-semibold text-gray-100">
                    {formatCurrency(tx.amount, tx.currency)}
                  </td>
                  <td className="py-3 px-4">
                    <div className="text-gray-200 truncate max-w-[140px]">{tx.merchant_name || tx.merchant_id}</div>
                    <div className="text-[10px] text-gray-400">{tx.merchant_category}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <span className={`inline-block w-2 h-2 rounded-full ${riskColors.badge}`}></span>
                      <span className="font-mono font-bold text-gray-200">{(tx.risk_score * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${badge.className}`}>
                      {badge.label}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-400 text-[11px]">
                    {formatTimeAgo(tx.created_at)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => onSelectTransaction?.(tx)}
                      className="p-1.5 rounded-lg bg-gray-800 text-gray-400 hover:text-blue-400 hover:bg-gray-700 transition-colors inline-flex items-center gap-1 text-[11px]"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
};
