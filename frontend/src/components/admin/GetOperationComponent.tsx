import React, { useState } from "react";
import {
  Button,
  Typography,
  Alert,
  CircularProgress,
  Box,
} from "@mui/material";
import { getOperationAdminOperationGet } from "../../client/sdk.gen";

interface GetOperationComponentProps {
  token: string;
}

export const GetOperationComponent: React.FC<GetOperationComponentProps> = ({
  token,
}) => {
  const [loading, setLoading] = useState(false);
  const [operationData, setOperationData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGetOperation = async () => {
    setLoading(true);
    setError(null);
    setOperationData(null);

    try {
      const response = await getOperationAdminOperationGet({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.data) {
        setOperationData(response.data);
      }
      if (response.error) {
        setError(`Couldn't get operation ${response.error}`);
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
        Get Operation
      </Typography>

      <Button
        variant="contained"
        onClick={handleGetOperation}
        disabled={loading}
        fullWidth
      >
        {loading ? <CircularProgress size={24} /> : "Get Operation"}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {operationData && (
        <Box sx={{ mt: 2 }}>
          <Alert severity="success">
            Operation data retrieved successfully
          </Alert>
          <Typography variant="body2" sx={{ mt: 1, fontFamily: "monospace" }}>
            {JSON.stringify(operationData, null, 2)}
          </Typography>
        </Box>
      )}
    </>
  );
};
