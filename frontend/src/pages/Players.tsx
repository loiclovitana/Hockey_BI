import React, { useContext, useState } from "react";
import { Box, Paper } from "@mui/material";
import { type LastPlayerStats } from "../client";
import { HockeyPlayerSearch } from "../components/player/HockeyPlayerSearch";
import { PlayerDashboard } from "../components/player/PlayerDashboard";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { EmptyState } from "../components/common/EmptyState";
import { PlayerStatsContext } from "../context/PlayerStatsContext";

export const Players: React.FC = () => {
  const { playerStats, loading, error } = useContext(PlayerStatsContext);
  const [selectedPlayer, setSelectedPlayer] = useState<LastPlayerStats | null>(
    null,
  );

  if (loading) {
    return <LoadingSpinner message="Loading player statistics..." />;
  }

  if (error) {
    return <ErrorMessage error={error} title="Error Loading Player Data" />;
  }

  if (!playerStats || playerStats.length === 0) {
    return (
      <EmptyState
        title="No Player Data Available"
        message="No player statistics are currently available. Please check back later or contact support if this issue persists."
      />
    );
  }

  return (
    <Box sx={{ display: "flex", height: "100%", gap: 2, p: 2 }}>
      <Paper
        elevation={2}
        sx={{
          width: "300px",
          minWidth: "300px",
          height: "100%",
          px: 1,
        }}
      >
        <HockeyPlayerSearch
          players={playerStats}
          setSelectedHockeyPlayer={setSelectedPlayer}
          selectedPlayer={selectedPlayer}
        />
      </Paper>

      <Box
        sx={{
          flex: 1,
          height: "100%",
          width: "100%",
        }}
      >
        <PlayerDashboard selectedPlayer={selectedPlayer} />
      </Box>
    </Box>
  );
};
