import React, { useContext, useState } from "react";
import { Box, Paper, CircularProgress, Typography, Alert } from "@mui/material";
import {   type LastPlayerStats } from "../client"
import { HockeyPlayerList } from "../components/HockeyPlayerList";
import { PlayerDashboard } from "../components/PlayerDashboard";
import { PlayerStatsContext } from "../context/PlayerStatsContext";



export const Players: React.FC = () => {
  const {
    playerStats,
    loading,
    error } = useContext(PlayerStatsContext);
  const [selectedPlayer, setSelectedPlayer] = useState<LastPlayerStats | null>(null);
  
  if (loading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%', 
          flexDirection: 'column',
          gap: 2 
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          Loading player statistics...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%', 
          p: 2 
        }}
      >
        <Alert severity="error" sx={{ maxWidth: 500 }}>
          <Typography variant="h6" gutterBottom>
            Error Loading Player Data
          </Typography>
          <Typography variant="body2">
            {error instanceof Error ? error.message : 'An unexpected error occurred while loading player statistics.'}
          </Typography>
        </Alert>
      </Box>
    );
  }

  if (!playerStats || playerStats.length === 0) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%', 
          p: 2 
        }}
      >
        <Alert severity="info" sx={{ maxWidth: 500 }}>
          <Typography variant="h6" gutterBottom>
            No Player Data Available
          </Typography>
          <Typography variant="body2">
            No player statistics are currently available. Please check back later or contact support if this issue persists.
          </Typography>
        </Alert>
      </Box>
    );
  }


  return (
    <Box sx={{ display: 'flex', height: "100%", gap: 2, p: 2 }}>
      <Paper elevation={2}
        sx={{
          width: '300px',
          minWidth: '300px',
          height: '100%',
          px: 1
        }}>
        <HockeyPlayerList players={playerStats} setSelectedHockeyPlayer={setSelectedPlayer} selectedPlayer={selectedPlayer} />
      </Paper>

      <Box sx={{
        flex: 1,
        height: '100%',
        width: '100%'
      }}>
        <PlayerDashboard selectedPlayer={selectedPlayer} />
      </Box>
    </Box>
  );
};
