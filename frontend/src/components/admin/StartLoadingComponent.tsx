import React, { useState } from "react";
import { Button, Typography, Alert, CircularProgress } from "@mui/material";
import { startLoadingAdminLoadStartPost } from "../../client/sdk.gen";

interface StartLoadingComponentProps {
  token: string;
}

export const StartLoadingComponent: React.FC<StartLoadingComponentProps> = ({
  token,
}) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleStartLoading = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await startLoadingAdminLoadStartPost({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.error) {
        setError(`An error occured: ${response.error}`);
      } else {
        setResult("Operation started sucessfully");
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
        Start Loading
      </Typography>

      <Button
        variant="contained"
        onClick={handleStartLoading}
        disabled={loading}
        fullWidth
      >
        {loading ? <CircularProgress size={24} /> : "Start Loading"}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Loading started successfully
        </Alert>
      )}
    </>
  );
};
