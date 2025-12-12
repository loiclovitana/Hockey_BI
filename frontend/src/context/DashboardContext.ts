import { createContext } from "react";
import { type DashBoardData, type Manager } from "../client";

export interface Credentials {
  hm_user: string;
  hm_password: string;
}

export interface DashboardContextType {
  dashboardData: DashBoardData | null;
  setDashboardData: (data: DashBoardData | null) => void;
  updateManager: (manager: Manager) => void;
  credentials: Credentials | null;
  setCredentials: (credentials: Credentials | null) => void;
}

export const DashboardContext = createContext<DashboardContextType | undefined>(
  undefined,
);
