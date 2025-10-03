import React, { useEffect, useState } from "react";
import { Box, Typography, useTheme, useMediaQuery } from "@mui/material";
import {
  type HockeyPlayerStats,
  getPlayerStatsPlayersStatsIdPlayerIdGet,
  type LastPlayerStats,
} from "../../client";
import { PlayerStatsDataGrid } from "./PlayerStatsDataGrid";
import { HockeyPlayerOwnershipChart } from "./HockeyPlayerOwnershipChart";

interface PlayerDashboardProps {
  selectedPlayer: LastPlayerStats | null;
}

export const PlayerDashboard: React.FC<PlayerDashboardProps> = ({
  selectedPlayer,
}) => {
  const [playerStats, setPlayerStats] = useState<HockeyPlayerStats[] | null>(
    null,
  );
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  useEffect(() => {
    if (!selectedPlayer) {
      setPlayerStats(null);
      return;
    }
    getPlayerStatsPlayersStatsIdPlayerIdGet({
      path: { player_id: selectedPlayer?.player_info.id },
    }).then((res) => {
      if (res.data) {
        setPlayerStats(res.data);
      }
    });
  }, [selectedPlayer]);

  return (
    <Box sx={{ p: isMobile ? 1 : 3, height: "100%", overflow: "auto" }}>
      {selectedPlayer ? (
        <>
          <Typography variant={isMobile ? "h5" : "h4"} gutterBottom>
            {selectedPlayer.player_info.name}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {selectedPlayer.player_info.role}
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {selectedPlayer.player_info.foreigner ? "Foreigner" : "Local"}
          </Typography>
          <PlayerStatsDataGrid playerStats={playerStats} />
          <HockeyPlayerOwnershipChart playerStats={playerStats} />
        </>
      ) : (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            textAlign: "center",
          }}
        >
          <Typography variant="h6" color="text.secondary">
            {isMobile
              ? "Tap menu to select a player"
              : "Select a player to view details"}
          </Typography>
        </Box>
      )}
    </Box>
  );
};
