import { createContext } from "react";
import { type DashBoardData, type Manager } from "../client";

export interface DashboardContextType {
  dashboardData: DashBoardData | null;
  setDashboardData: (data: DashBoardData | null) => void;
  updateManager: (manager: Manager) => void;
}

export const DashboardContext = createContext<DashboardContextType | undefined>(
  undefined,
);
