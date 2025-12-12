import React, { useState, useMemo, useCallback } from "react";
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

  const updateManager = useCallback((manager: Manager) => {
    setDashboardData((prev) => (prev ? { ...prev, manager } : null));
  }, []);

  const value = useMemo(
    () => ({
      dashboardData,
      setDashboardData,
      updateManager,
      credentials,
      setCredentials,
    }),
    [dashboardData, credentials, updateManager],
  );

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
};
