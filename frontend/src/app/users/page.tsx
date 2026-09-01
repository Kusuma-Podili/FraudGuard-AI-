"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { api } from "@/lib/api";
import { User } from "@/types";
import {
  Users,
  UserPlus,
  KeyRound,
  Edit2,
  CheckCircle2,
  RefreshCw,
} from "lucide-react";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Add User Modal
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newFullName, setNewFullName] = useState("");
  const [newPassword, setNewPassword] = useState("Analyst@2026");
  const [newRole, setNewRole] = useState("FRAUD_ANALYST");
  const [newDept, setNewDept] = useState("Risk Operations");

  // Edit User Modal
  const [editUser, setEditUser] = useState<User | null>(null);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editFullName, setEditFullName] = useState("");
  const [editRole, setEditRole] = useState("FRAUD_ANALYST");
  const [editDept, setEditDept] = useState("");

  // Reset Password Modal
  const [resetTargetUser, setResetTargetUser] = useState<User | null>(null);
  const [isResetOpen, setIsResetOpen] = useState(false);
  const [newResetPassword, setNewResetPassword] = useState("");

  const [notification, setNotification] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      const data = await api.listUsers();
      setUsers(data || []);
    } catch (e) {
      console.error("Failed to load users", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await api.createUser({
        email: newEmail,
        password: newPassword,
        full_name: newFullName,
        role: newRole,
        department: newDept,
      });
      setIsAddOpen(false);
      setNewEmail("");
      setNewFullName("");
      setNotification(`User account ${newEmail} created successfully.`);
      fetchUsers();
    } catch (e) {
      console.error("Failed to create user", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editUser) return;
    setIsSubmitting(true);
    try {
      await api.updateUser(editUser.id, {
        full_name: editFullName,
        role: editRole as any,
        department: editDept,
      });
      setIsEditOpen(false);
      setNotification(`User profile for ${editUser.email} updated.`);
      fetchUsers();
    } catch (e) {
      console.error("Failed to update user", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleActive = async (targetUser: User) => {
    try {
      await api.updateUser(targetUser.id, {
        is_active: !targetUser.is_active,
      });
      setNotification(`User ${targetUser.email} status changed to ${!targetUser.is_active ? "ACTIVE" : "INACTIVE"}.`);
      fetchUsers();
    } catch (e) {
      console.error("Failed to toggle status", e);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetTargetUser || !newResetPassword) return;
    setIsSubmitting(true);
    try {
      await api.resetUserPassword(resetTargetUser.id, newResetPassword);
      setIsResetOpen(false);
      setNewResetPassword("");
      setNotification(`Password securely updated for ${resetTargetUser.email}.`);
    } catch (e) {
      console.error("Password reset failed", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Users className="w-6 h-6 text-gray-800" />
            <h1 className="text-2xl font-bold text-[#111827] tracking-tight">Platform User Management</h1>
          </div>
          <p className="text-xs text-[#4B5563] mt-1">
            Provision, manage roles, configure permissions, and reset credentials for risk analysts and administrators.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchUsers} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setIsAddOpen(true)}>
            <UserPlus className="w-3.5 h-3.5 mr-1.5" />
            Add New User
          </Button>
        </div>
      </div>

      {notification && (
        <div className="p-3 bg-gray-100 border border-gray-300 rounded-xl text-xs text-gray-900 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-gray-900 shrink-0" />
            <span>{notification}</span>
          </div>
          <button onClick={() => setNotification(null)} className="text-[#4B5563] hover:text-[#111827]">✕</button>
        </div>
      )}

      {/* Users Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#111827]">
            <thead className="bg-[#F9FAFB] text-[11px] text-[#4B5563] uppercase tracking-wider border-b border-[#E5E7EB]">
              <tr>
                <th className="py-3.5 px-4 font-semibold">User</th>
                <th className="py-3.5 px-4 font-semibold">Email</th>
                <th className="py-3.5 px-4 font-semibold">Role</th>
                <th className="py-3.5 px-4 font-semibold">Department</th>
                <th className="py-3.5 px-4 font-semibold">Status</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E7EB]">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center text-gray-800 font-bold text-xs">
                        {u.full_name?.charAt(0) || "U"}
                      </div>
                      <span className="font-bold text-[#111827]">{u.full_name}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[#4B5563]">{u.email}</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 text-gray-800 border border-gray-300">
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-[#4B5563]">{u.department || "Operations"}</td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        u.is_active
                          ? "bg-gray-100 text-gray-900 border border-gray-300"
                          : "bg-[#FFEDD5] text-[#9A3412] border border-[#FDBA74]"
                      }`}
                    >
                      {u.is_active ? "ACTIVE" : "INACTIVE"}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right space-x-1.5">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditUser(u);
                        setEditFullName(u.full_name);
                        setEditRole(u.role);
                        setEditDept(u.department || "");
                        setIsEditOpen(true);
                      }}
                      className="text-[11px]"
                    >
                      <Edit2 className="w-3 h-3 mr-1" />
                      Edit
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setResetTargetUser(u);
                        setIsResetOpen(true);
                      }}
                      className="text-[11px]"
                    >
                      <KeyRound className="w-3 h-3 mr-1" />
                      Reset Pass
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleActive(u)}
                      className="text-[11px] text-gray-600 hover:text-gray-900"
                    >
                      {u.is_active ? "Deactivate" : "Activate"}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Add User Modal */}
      <Modal isOpen={isAddOpen} onClose={() => setIsAddOpen(false)} title="Add Platform User" size="md">
        <form onSubmit={handleCreateUser} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#111827]">Full Name</label>
            <input
              type="text"
              required
              value={newFullName}
              onChange={(e) => setNewFullName(e.target.value)}
              placeholder="Elena Rostova"
              className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#111827]">Work Email</label>
            <input
              type="email"
              required
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="elena@fraudguard.ai"
              className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#111827]">Role</label>
              <select
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
              >
                <option value="FRAUD_ANALYST">FRAUD_ANALYST</option>
                <option value="ADMIN">ADMIN</option>
                <option value="RISK_LEAD">RISK_LEAD</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#111827]">Department</label>
              <input
                type="text"
                value={newDept}
                onChange={(e) => setNewDept(e.target.value)}
                placeholder="Fraud Triage"
                className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#111827]">Initial Password</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E5E7EB]">
            <Button variant="secondary" size="sm" type="button" onClick={() => setIsAddOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Account"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit User Modal */}
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit User Profile" size="md">
        <form onSubmit={handleUpdateUser} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#111827]">Full Name</label>
            <input
              type="text"
              required
              value={editFullName}
              onChange={(e) => setEditFullName(e.target.value)}
              className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#111827]">Role</label>
              <select
                value={editRole}
                onChange={(e) => setEditRole(e.target.value)}
                className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
              >
                <option value="FRAUD_ANALYST">FRAUD_ANALYST</option>
                <option value="ADMIN">ADMIN</option>
                <option value="RISK_LEAD">RISK_LEAD</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#111827]">Department</label>
              <input
                type="text"
                value={editDept}
                onChange={(e) => setEditDept(e.target.value)}
                className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E5E7EB]">
            <Button variant="secondary" size="sm" type="button" onClick={() => setIsEditOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Reset Password Modal */}
      <Modal isOpen={isResetOpen} onClose={() => setIsResetOpen(false)} title="Reset User Password" size="sm">
        <form onSubmit={handleResetPassword} className="space-y-4">
          <p className="text-xs text-[#4B5563]">
            Set a new password for <strong className="text-[#111827]">{resetTargetUser?.email}</strong>.
          </p>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#111827]">New Password</label>
            <input
              type="password"
              required
              value={newResetPassword}
              onChange={(e) => setNewResetPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-2 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E5E7EB]">
            <Button variant="secondary" size="sm" type="button" onClick={() => setIsResetOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Updating..." : "Reset Password"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
