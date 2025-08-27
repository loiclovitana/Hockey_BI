import React from "react";
import { Paper, Typography } from "@mui/material";
import { type HockeyPlayer } from "../client";

interface PlayerDashboardProps {
  selectedPlayer: HockeyPlayer | null;
}

export const PlayerDashboard: React.FC<PlayerDashboardProps> = ({ selectedPlayer }) => {
  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      {selectedPlayer ? (
        <>
          <Typography variant="h4" gutterBottom>
            {selectedPlayer.name}
          </Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>
            {selectedPlayer.role}
          </Typography>
          <Typography variant="body1">
            {selectedPlayer.foreigner ? "Foreigner" : "Local"}
          </Typography>
        </>
      ) : (
        <Typography variant="h6" color="text.secondary">
          Select a player to view details
        </Typography>
      )}
    </Paper>
  );
};