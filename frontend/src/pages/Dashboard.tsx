import React, { useState } from "react";
import { type DashBoardData, type Manager } from "../client";
import { TeamLoginForm } from "../components/myteam/TeamLoginForm";
import { MyTeamDashboard } from "../components/myteam/MyTeamDashboard";

export const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashBoardData | null>(
    null,
  );

  const updateManager = (manager: Manager) => {
    setDashboardData((prev) => (prev ? { ...prev, manager } : null));
  };

  if (dashboardData) {
    return (
      <MyTeamDashboard
        dashboardData={dashboardData}
        onManagerUpdate={updateManager}
      ></MyTeamDashboard>
    );
  }

  return <TeamLoginForm onSuccess={setDashboardData} />;
};
