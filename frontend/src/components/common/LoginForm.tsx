import React, { useState } from "react";
import { Box, Typography, TextField, Button } from "@mui/material";

export interface LoginFormField {
  key: string;
  label: string;
  type?: string;
}

interface LoginFormProps<T = Record<string, string>> {
  fields: LoginFormField[];
  buttonText: string;
  loadingText: string;
  onSubmit: (data: T) => Promise<void>;
}

export const LoginForm = <T extends Record<string, string>>({
  fields,
  buttonText,
  loadingText,
  onSubmit,
}: LoginFormProps<T>) => {
  const [formData, setFormData] = useState<T>(() => {
    const initial = {} as T;
    fields.forEach((field) => {
      initial[field.key as keyof T] = "" as T[keyof T];
    });
    return initial;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFieldChange = (key: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const isFormValid = () => {
    return fields.every((field) =>
      (formData[field.key as keyof T] as string).trim(),
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isFormValid()) {
      setError("Please fill in all fields");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onSubmit(formData);
    } catch (error) {
      setError("An error occurred during submission");
      console.error("Form submission error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
      {fields.map((field) => (
        <TextField
          key={field.key}
          fullWidth
          label={field.label}
          type={field.type || "text"}
          variant="outlined"
          value={formData[field.key as keyof T] as string}
          onChange={(e) => handleFieldChange(field.key, e.target.value)}
          sx={{ mb: 2 }}
        />
      ))}

      {error && (
        <Typography color="error" variant="body2" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Button
        fullWidth
        type="submit"
        variant="contained"
        disabled={loading || !isFormValid()}
        sx={{ mt: 2 }}
      >
        {loading ? loadingText : buttonText}
      </Button>
    </Box>
  );
};
