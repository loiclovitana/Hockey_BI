import React from "react";
import { Box, Typography, Paper } from "@mui/material";

export const Players: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Players
      </Typography>
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography variant="body1">
          Player statistics and information will be displayed here.
        </Typography>
      </Paper>
    </Box>
  );
};
