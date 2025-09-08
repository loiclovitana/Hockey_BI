import React from "react";
import { Box, Alert, Typography } from "@mui/material";

interface ErrorMessageProps {
  error: unknown;
  title?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  error,
  title = "Error Loading Data",
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
      <Alert severity="error" sx={{ maxWidth: 500 }}>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2">
          {error instanceof Error
            ? error.message
            : "An unexpected error occurred."}
        </Typography>
      </Alert>
    </Box>
  );
};
