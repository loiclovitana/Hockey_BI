import React, { useState } from "react";
import {
  Button,
  Typography,
  Alert,
  CircularProgress,
  Box,
} from "@mui/material";
import { getAdminUserAdminUserGet } from "../../client/sdk.gen";
import type { AdminUser } from "../../client";

interface GetAdminUserComponentProps {
  token: string;
}

export const GetAdminUserComponent: React.FC<GetAdminUserComponentProps> = ({
  token,
}) => {
  const [loading, setLoading] = useState(false);
  const [userData, setUserData] = useState<AdminUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGetUser = async () => {
    setLoading(true);
    setError(null);
    setUserData(null);

    try {
      const { data, error } = await getAdminUserAdminUserGet({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (data) {
        setUserData(data);
      }
      if (error) {
        setError(`Couldn't get user: ${error}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Typography variant="h6" gutterBottom>
        Get Admin User
      </Typography>

      <Button
        variant="contained"
        onClick={handleGetUser}
        disabled={loading}
        fullWidth
      >
        {loading ? <CircularProgress size={24} /> : "Get User Info"}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {userData && (
        <Box sx={{ mt: 2 }}>
          <Alert severity="success">User data retrieved successfully</Alert>
          <Typography variant="body2" sx={{ mt: 1, fontFamily: "monospace" }}>
            {JSON.stringify(userData, null, 2)}
          </Typography>
        </Box>
      )}
    </>
  );
};
