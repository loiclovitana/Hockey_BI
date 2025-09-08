import React from "react";
import { Box, Alert, Typography } from "@mui/material";

interface EmptyStateProps {
  title?: string;
  message?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No Data Available",
  message = "No data is currently available. Please check back later or contact support if this issue persists.",
}) => {
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100%",
        p: 2,
      }}
    >
      <Alert severity="info" sx={{ maxWidth: 500 }}>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2">{message}</Typography>
      </Alert>
    </Box>
  );
};
