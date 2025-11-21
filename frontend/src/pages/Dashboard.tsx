import React from "react";
import { TeamLoginForm } from "../components/myteam/TeamLoginForm";
import { MyTeamDashboard } from "../components/myteam/MyTeamDashboard";
import { useDashboard } from "../hooks/useDashboard";

export const Dashboard: React.FC = () => {
  const { dashboardData, setDashboardData, updateManager } = useDashboard();

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
