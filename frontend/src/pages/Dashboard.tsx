import React, { useState } from "react";
import { Box, Typography, Paper } from "@mui/material";
import { type DashBoardData } from "../client";
import { TeamLoginForm } from "../components/TeamLoginForm";

export const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashBoardData | null>(null);


  if (dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Paper sx={{ p: 2, mt: 2 }}>
          <Typography variant="body1">
            OK
          </Typography>
        </Paper>
      </Box>
    );
  }

  return <TeamLoginForm onSuccess={setDashboardData}/>;
};
