import React, { useState } from "react";
import { AdminLoginForm } from "../components/admin/AdminLoginForm";
import { AdminDashboard } from "../components/admin/AdminDashboard";

export const Admin: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);

  const handleLoginSuccess = (accessToken: string) => {
    setToken(accessToken);
  };

  if (!token) {
    return <AdminLoginForm onSuccess={handleLoginSuccess} />;
  }

  return <AdminDashboard token={token} />;
};
