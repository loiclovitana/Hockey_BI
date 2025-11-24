import React, { useState } from "react";
import { Box, Typography, Button, ButtonGroup } from "@mui/material";
import { useDashboard } from "../hooks/useDashboard";
import { TeamLoginForm } from "../components/myteam/TeamLoginForm";
import { Transferts } from "../components/myteam/Transferts";

export const TransferAnalytics: React.FC = () => {
  const { dashboardData, setDashboardData } = useDashboard();
  const [team, setTeam] = useState(0);

  if (!dashboardData) {
    return <TeamLoginForm onSuccess={setDashboardData} />;
  }

  const numberOfTeam = dashboardData.my_teams.length;

  return (
    <Box sx={{ py: 3 }}>
      <Typography variant="h5" textAlign="center" gutterBottom>
        Transfer Analytics
      </Typography>

      {numberOfTeam === 0 ? (
        <Typography variant="body2" textAlign="center">
          You haven't created any team yet
        </Typography>
      ) : (
        <>
          <Box sx={{ display: "flex", justifyContent: "center", pb: 2 }}>
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
          <Transferts team={dashboardData.my_teams[team]} />
        </>
      )}
    </Box>
  );
};
