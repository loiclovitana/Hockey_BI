import React, { useState } from "react";
import { Button, Typography, Alert, CircularProgress } from "@mui/material";
import { startLoadingPlayernewsAdminPlayernewsImportAndMatchStartPost as startImportAndMatchPlayerNews } from "../../client/sdk.gen";

interface StartPlayerNewsLoadingComponentProps {
  token: string;
}

export const StartPlayerNewsLoadingComponent: React.FC<
  StartPlayerNewsLoadingComponentProps
> = ({ token }) => {
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartImportAndMatch = async () => {
    setLoading(true);
    setStarted(false);
    setError(null);

    try {
      const response = await startImportAndMatchPlayerNews({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.error) {
        setError(
          `Could not start SHN player news import and matching: ${response.error}`,
        );
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
        Import and Match SHN Player News
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Import new Swiss Hockey News articles, then link recent news to players
        in the current season.
      </Typography>
      <Button
        variant="contained"
        onClick={handleStartImportAndMatch}
        disabled={loading}
        fullWidth
      >
        {loading ? (
          <CircularProgress size={24} />
        ) : (
          "Import and Match SHN Player News"
        )}
      </Button>
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      {started && (
        <Alert severity="success" sx={{ mt: 2 }}>
          SHN player news import and matching started. Check the operation
          status and task history for progress.
        </Alert>
      )}
    </>
  );
};
