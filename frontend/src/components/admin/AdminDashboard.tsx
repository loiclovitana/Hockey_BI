import React from "react";
import { Container, Typography, Grid, Paper, Box } from "@mui/material";
import { StartLoadingComponent } from "./StartLoadingComponent";
import { GetAdminUserComponent } from "./GetAdminUserComponent";
import { GetOperationComponent } from "./GetOperationComponent";
import { GetTasksComponent } from "./GetTasksComponent";

interface AdminDashboardProps {
  token: string;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ token }) => {
  return (
    <Container sx={{ pt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>

      <Grid container spacing={3} justifyContent="center" paddingTop={2}>
        <Grid size={10}>
          <Paper sx={{ p: 2 }}>
            <GetAdminUserComponent token={token} />
          </Paper>
        </Grid>

        <Grid size={10}>
          <Paper sx={{ p: 2 }}>
            <GetOperationComponent token={token} />
          </Paper>
        </Grid>

        <Grid size={10}>
          <Paper sx={{ p: 2 }}>
            <StartLoadingComponent token={token} />
          </Paper>
        </Grid>
      </Grid>
      <Box sx={{ pt: 2 }}>
        <Paper sx={{ p: 2 }}>
          <GetTasksComponent token={token} />
        </Paper>
      </Box>
    </Container>
  );
};
