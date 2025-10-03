import React from "react";
import { Container, Typography, Paper, Box } from "@mui/material";
import { StartLoadingComponent } from "./StartLoadingComponent";
import { GetAdminUserComponent } from "./GetAdminUserComponent";
import { GetOperationComponent } from "./GetOperationComponent";
import { GetTasksComponent } from "./GetTasksComponent";

interface AdminDashboardProps {
  token: string;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ token }) => {
  return (
    <Container maxWidth="md" sx={{ pt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      <Box sx={{ pt: 2, display: "flex", flexDirection: "column", gap: 2 }}>
        <Paper sx={{ p: 2 }}>
          <GetAdminUserComponent token={token} />
        </Paper>
        <Paper sx={{ p: 2 }}>
          <GetOperationComponent token={token} />
        </Paper>
        <Paper sx={{ p: 2 }}>
          <StartLoadingComponent token={token} />
        </Paper>
        <Paper sx={{ p: 2 }}>
          <GetTasksComponent token={token} />
        </Paper>
      </Box>
    </Container>
  );
};
