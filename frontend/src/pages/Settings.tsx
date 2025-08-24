import React from "react";
import { Box, Typography, Paper } from "@mui/material";

export const Settings: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography variant="body1">
          Application settings and configuration options will be available here.
        </Typography>
      </Paper>
    </Box>
  );
};
