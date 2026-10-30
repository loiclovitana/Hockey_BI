import React, { useState } from "react";
import { Button, Typography, Alert, CircularProgress } from "@mui/material";
import { startMatchingPlayernewsAdminPlayernewsMatchStartPost as startMatchingPlayerNews } from "../../client/sdk.gen";

interface StartPlayerNewsMatchingComponentProps {
  token: string;
}

export const StartPlayerNewsMatchingComponent: React.FC<
  StartPlayerNewsMatchingComponentProps
> = ({ token }) => {
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartMatching = async () => {
    setLoading(true);
    setStarted(false);
    setError(null);

    try {
      const response = await startMatchingPlayerNews({
        headers: {
          Authorization: `Bearer ${token}`,
        },
        query: {
          since_d: 30,
          replace: true,
        },
      });
      if (response.error) {
        setError(`Could not start player news matching: ${response.error}`);
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
        Re-match Player News
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Re-evaluate player matches for news from the last 30 days, including
        news already linked to a player.
      </Typography>
      <Button
        variant="outlined"
        onClick={handleStartMatching}
        disabled={loading}
        fullWidth
      >
        {loading ? <CircularProgress size={24} /> : "Re-match Player News"}
      </Button>
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      {started && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Player news matching started with replacement enabled. Check the
          operation status and task history for progress.
        </Alert>
      )}
    </>
  );
};
