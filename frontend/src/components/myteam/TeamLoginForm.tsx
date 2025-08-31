import React, { useState } from "react";
import { Box, Typography,  TextField, Button, Container } from "@mui/material";
import { loadMyteamLoadPost, type DashBoardData } from "../../client";

interface TeamLoginFormProps {
  onSuccess: (data: DashBoardData) => void;
}

export const TeamLoginForm: React.FC<TeamLoginFormProps> = ({ onSuccess }) => {
  const [hmUser, setHmUser] = useState("");
  const [hmPassword, setHmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!hmUser.trim() || !hmPassword.trim()) {
      setError("Please enter both username and password");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await loadMyteamLoadPost({
        query: {
          hm_user: hmUser,
          hm_password: hmPassword
        }
      });
      
      if (response.data) {
        onSuccess(response.data);
      }
      
      if (response.error) {
        setError("Failed to load team data");
        console.error(response.error);
      }
    } catch (error) {
      setError("An error occurred while loading team data");
      console.error("Failed to load team:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container  
      sx={{ 
        mt: 8,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
        <Typography variant="h2" gutterBottom align="center">
          Start now
        </Typography>
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <TextField
            fullWidth
            label="HM Username"
            variant="outlined"
            value={hmUser}
            onChange={(e) => setHmUser(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          <TextField
            fullWidth
            label="HM Password"
            type="password"
            variant="outlined"
            value={hmPassword}
            onChange={(e) => setHmPassword(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          {error && (
            <Typography color="error" variant="body2" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}
          
          <Button
            fullWidth
            type="submit"
            variant="contained"
            disabled={loading || !hmUser.trim() || !hmPassword.trim()}
            sx={{ mt: 2 }}
          >
            {loading ? "Loading..." : "Load my HM data"}
          </Button>
        </Box>
    </Container>
  );
};