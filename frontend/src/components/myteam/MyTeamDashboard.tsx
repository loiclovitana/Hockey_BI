import React, { useState } from "react";
import { Box, Typography, Select, MenuItem } from "@mui/material";
import { type DashBoardData } from "../../client";
import { TransferSuggestion } from "./TransferSuggestion";

interface MyTeamDashboardProps {
  dashboardData: DashBoardData;
}

export const MyTeamDashboard: React.FC<MyTeamDashboardProps> = ({
  dashboardData,
}) => {
  const [team, setTeam] = useState(0);

  const numberOfTeam = dashboardData.my_teams.length;
  if (numberOfTeam == 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Welcome {dashboardData.manager.email}
        </Typography>
        <Typography variant="body2">
          You haven't created any team yet
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Welcome {dashboardData.manager.email}
      </Typography>

      <Select
        value={team}
        size="medium"
        onChange={(e) => {
          setTeam(e.target.value);
        }}
        sx={{ mt: 2, ml: 2, p: 0.5 }}
      >
        {dashboardData.my_teams.map((_, index) => (
          <MenuItem key={index} value={index}>
            Team {index + 1}
          </MenuItem>
        ))}
      </Select>
      <TransferSuggestion team={dashboardData.my_teams[team]} />
    </Box>
  );
};
