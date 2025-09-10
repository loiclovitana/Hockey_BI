import React from "react";
import { LoginForm, type LoginFormField } from "../common/LoginForm";
import { loginAdminLoginPost } from "../../client";
import { Container, Typography } from "@mui/material";

interface AdminLoginFormProps {
  onSuccess: (token: string) => void;
}

interface AdminLoginData extends Record<string, string> {
  username: string;
  password: string;
}

const adminLoginFields: LoginFormField[] = [
  { key: "username", label: "Username" },
  { key: "password", label: "Password", type: "password" },
];

export const AdminLoginForm: React.FC<AdminLoginFormProps> = ({
  onSuccess,
}) => {
  const handleSubmit = async (formData: AdminLoginData) => {
    const response = await loginAdminLoginPost({
      body: {
        username: formData.username,
        password: formData.password,
      },
    });

    if (response.data) {
      onSuccess(response.data.access_token);
    }

    if (response.error) {
      console.error(response.error);
      throw new Error("Failed to login");
    }
  };

  return (
    <Container
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        pt: 4,
      }}
    >
      <Typography variant="h4" gutterBottom>
        Admin Login
      </Typography>
      <LoginForm<AdminLoginData>
        fields={adminLoginFields}
        buttonText="Login"
        loadingText="Logging in..."
        onSubmit={handleSubmit}
      />
    </Container>
  );
};
