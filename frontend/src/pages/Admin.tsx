import React, { useState } from "react";
import { Container, Typography } from "@mui/material";
import { AdminLoginForm } from "../components/admin/AdminLoginForm";

export const Admin: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);

  const handleLoginSuccess = (accessToken: string) => {
    setToken(accessToken);
  };

  if (!token) {
    return <AdminLoginForm onSuccess={handleLoginSuccess} />;
  }

  return (
    <Container sx={{ pt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      <Typography variant="body1">
        Welcome to the admin panel. Functionality will be added here.
      </Typography>
    </Container>
  );
};
