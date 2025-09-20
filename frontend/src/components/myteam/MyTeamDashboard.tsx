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

  return (
    <Box sx={{ py: 3 }}>
      <Typography
        variant="h6"
        textAlign={"center"}
        gutterBottom
        sx={{ wordBreak: "break-word", pb: 2 }}
      >
        Welcome {dashboardData.manager.email}
      </Typography>

      {numberOfTeam === 0 ? (
        <Typography variant="body2">
          You haven't created any team yet
        </Typography>
      ) : (
        <>
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
        </>
      )}
    </Box>
  );
};
