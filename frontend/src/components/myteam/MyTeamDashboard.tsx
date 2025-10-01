import React, { useState } from "react";
import { Box, Typography, Button, ButtonGroup } from "@mui/material";
import { type DashBoardData } from "../../client";
import { TransferSuggestion } from "./TransferSuggestion";
import { AutolineupStatus } from "./AutolineupStatus";

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
        sx={{ wordBreak: "break-word", pb: 1 }}
      >
        Welcome {dashboardData.manager.email}
      </Typography>

      <Box sx={{ display: "flex", justifyContent: "center", pb: 3 }}>
        <AutolineupStatus manager={dashboardData.manager} />
      </Box>

      {numberOfTeam === 0 ? (
        <Typography variant="body2">
          You haven't created any team yet
        </Typography>
      ) : (
        <>
          <Box sx={{ display: "flex", justifyContent: "center", py: 1 }}>
            <ButtonGroup variant="contained" sx={{ minWidth: "300px" }}>
              <Button
                variant={team === 0 ? "contained" : "outlined"}
                onClick={() => setTeam(0)}
                sx={{ flex: 1 }}
              >
                Team 1
              </Button>
              <Button
                variant={team === 1 ? "contained" : "outlined"}
                onClick={() => setTeam(1)}
                disabled={numberOfTeam < 2}
                sx={{ flex: 1 }}
              >
                Team 2
              </Button>
            </ButtonGroup>
          </Box>
          <TransferSuggestion team={dashboardData.my_teams[team]} />
        </>
      )}
    </Box>
  );
};
