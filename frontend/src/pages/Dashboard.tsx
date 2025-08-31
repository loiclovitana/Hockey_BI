import React, { useState } from "react";
import { type DashBoardData } from "../client";
import { TeamLoginForm } from "../components/myteam/TeamLoginForm";
import { MyTeamDashboard } from "../components/myteam/MyTeamDashboard";

export const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashBoardData | null>(null);


  if (dashboardData) {
    return (
      <MyTeamDashboard dashboardData={dashboardData}></MyTeamDashboard>
    );
  }

  return <TeamLoginForm onSuccess={setDashboardData}/>;
};
