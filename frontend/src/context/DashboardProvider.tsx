import React, { useState } from "react";
import { DashboardContext, type Credentials } from "./DashboardContext";
import { type DashBoardData, type Manager } from "../client";

interface DashboardProviderProps {
  children: React.ReactNode;
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({
  children,
}) => {
  const [dashboardData, setDashboardData] = useState<DashBoardData | null>(
    null,
  );
  const [credentials, setCredentials] = useState<Credentials | null>(null);

  const updateManager = (manager: Manager) => {
    setDashboardData((prev) => (prev ? { ...prev, manager } : null));
  };

  return (
    <DashboardContext.Provider
      value={{ dashboardData, setDashboardData, updateManager, credentials, setCredentials }}
    >
      {children}
    </DashboardContext.Provider>
  );
};
