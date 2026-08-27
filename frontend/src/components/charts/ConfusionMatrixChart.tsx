"use client";

import React from "react";

interface ConfusionMatrixProps {
  matrix: {
    true_negative: number;
    false_positive: number;
    false_negative: number;
    true_positive: number;
  };
}

export const ConfusionMatrixChart: React.FC<ConfusionMatrixProps> = ({ matrix }) => {
  return (
    <div className="w-full">
      <div className="grid grid-cols-2 gap-3 text-center">
        {/* True Negative */}
        <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-xl p-4">
          <p className="text-[11px] text-emerald-400 font-semibold uppercase">True Negative (TN)</p>
          <p className="text-xl font-bold text-gray-100 mt-1">{matrix.true_negative.toLocaleString()}</p>
          <p className="text-[10px] text-gray-500 mt-0.5">Legitimate Allowed</p>
        </div>

        {/* False Positive */}
        <div className="bg-amber-950/30 border border-amber-500/30 rounded-xl p-4">
          <p className="text-[11px] text-amber-400 font-semibold uppercase">False Positive (FP)</p>
          <p className="text-xl font-bold text-gray-100 mt-1">{matrix.false_positive.toLocaleString()}</p>
          <p className="text-[10px] text-gray-500 mt-0.5">Customer Friction</p>
        </div>

        {/* False Negative */}
        <div className="bg-red-950/30 border border-red-500/30 rounded-xl p-4">
          <p className="text-[11px] text-red-400 font-semibold uppercase">False Negative (FN)</p>
          <p className="text-xl font-bold text-gray-100 mt-1">{matrix.false_negative.toLocaleString()}</p>
          <p className="text-[10px] text-gray-500 mt-0.5">Missed Fraud Leakage</p>
        </div>

        {/* True Positive */}
        <div className="bg-blue-950/30 border border-blue-500/30 rounded-xl p-4">
          <p className="text-[11px] text-blue-400 font-semibold uppercase">True Positive (TP)</p>
          <p className="text-xl font-bold text-gray-100 mt-1">{matrix.true_positive.toLocaleString()}</p>
          <p className="text-[10px] text-gray-500 mt-0.5">Fraud Blocked</p>
        </div>
      </div>
    </div>
  );
};
