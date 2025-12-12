import React, { useState } from "react";
import { Box, Typography, Button, ButtonGroup } from "@mui/material";
import { useDashboard } from "../hooks/useDashboard";
import { TeamLoginForm } from "../components/myteam/TeamLoginForm";
import { TeamAnalyticsView } from "../components/myteam/TeamAnalyticsView";

export const TransferAnalytics: React.FC = () => {
  const { dashboardData, setDashboardData, credentials } = useDashboard();
  const [team, setTeam] = useState(0);

  const numberOfTeam = dashboardData?.my_teams.length ?? 0;

  if (!dashboardData) {
    return <TeamLoginForm onSuccess={setDashboardData} />;
  }

  return (
    <Box sx={{ py: 3 }}>
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

          <Box sx={{ position: "relative", minHeight: "500px" }}>
            <Box
              sx={{
                position: team === 0 ? "relative" : "absolute",
                top: 0,
                left: 0,
                right: 0,
                //visibility: team === 0 ? "visible" : "hidden",
                opacity: team === 0 ? 1 : 0,
                transform: team === 0 ? "translateX(0)" : "translateX(-300px)",
                pointerEvents: team === 0 ? "auto" : "none",
                transition: "opacity 0.5s ease-in, transform 0.5s ease-in-out",
              }}
            >
              {credentials && (
                <TeamAnalyticsView
                  team={0}
                  dashboardData={dashboardData}
                  credentials={credentials}
                />
              )}
            </Box>

            {numberOfTeam >= 2 && (
              <Box
                sx={{
                  position: team === 1 ? "relative" : "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  //visibility: team === 1 ? "visible" : "hidden",
                  opacity: team === 1 ? 1 : 0,
                  transform: team === 1 ? "translateX(0)" : "translateX(300px)",
                  pointerEvents: team === 1 ? "auto" : "none",
                  transition: "opacity 0.5s ease-in, transform 0.5s ease-in-out",
                }}
              >
                {credentials && (
                  <TeamAnalyticsView
                    team={1}
                    dashboardData={dashboardData}
                    credentials={credentials}
                  />
                )}
              </Box>
            )}
          </Box>
        </>
      )}
    </Box>
  );
};
