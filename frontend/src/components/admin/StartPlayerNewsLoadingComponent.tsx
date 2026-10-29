import React, { useState } from "react";
import { Button, Typography, Alert, CircularProgress } from "@mui/material";
import { startLoadingPlayernewsAdminPlayernewsStartPost } from "../../client/sdk.gen";

interface StartPlayerNewsLoadingComponentProps {
  token: string;
}

export const StartPlayerNewsLoadingComponent: React.FC<
  StartPlayerNewsLoadingComponentProps
> = ({ token }) => {
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartLoading = async () => {
    setLoading(true);
    setStarted(false);
    setError(null);

    try {
      const response = await startLoadingPlayernewsAdminPlayernewsStartPost({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.error) {
        setError(`Could not start SHN player news loading: ${response.error}`);
      } else {
        setStarted(true);
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
        Load SHN Player News
      </Typography>
      <Button
        variant="contained"
        onClick={handleStartLoading}
        disabled={loading}
        fullWidth
      >
        {loading ? <CircularProgress size={24} /> : "Load SHN Player News"}
      </Button>
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      {started && (
        <Alert severity="success" sx={{ mt: 2 }}>
          SHN player news loading started successfully. Check the operation
          status and task history for progress.
        </Alert>
      )}
    </>
  );
};
