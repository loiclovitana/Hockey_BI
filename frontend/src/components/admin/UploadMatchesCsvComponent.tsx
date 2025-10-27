import React, { useState } from "react";
import {
  Button,
  Typography,
  Alert,
  CircularProgress,
  Box,
} from "@mui/material";
import { uploadMatchesCsvAdminMatchesUploadPost } from "../../client/sdk.gen";
import type { MatchImportResponse } from "../../client/types.gen";

interface UploadMatchesCsvComponentProps {
  token: string;
}

export const UploadMatchesCsvComponent: React.FC<
  UploadMatchesCsvComponentProps
> = ({ token }) => {
  const [loading, setLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState<MatchImportResponse | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a CSV file first");
      return;
    }

    setLoading(true);
    setError(null);
    setUploadResult(null);

    try {
      const response = await uploadMatchesCsvAdminMatchesUploadPost({
        body: {
          file: selectedFile,
        },
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.data) {
        setUploadResult(response.data);
      }
      if (response.error) {
        setError(`Couldn't upload matches: ${JSON.stringify(response.error)}`);
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
        Upload Matches CSV
      </Typography>

      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Button variant="outlined" component="label" fullWidth>
          {selectedFile ? selectedFile.name : "Select CSV File"}
          <input type="file" accept=".csv" hidden onChange={handleFileChange} />
        </Button>

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={loading || !selectedFile}
          fullWidth
        >
          {loading ? <CircularProgress size={24} /> : "Upload Matches"}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {uploadResult && (
        <Box sx={{ mt: 2 }}>
          <Alert severity="success">{uploadResult.message}</Alert>
        </Box>
      )}
    </>
  );
};
