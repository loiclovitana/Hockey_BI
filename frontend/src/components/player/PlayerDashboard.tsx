import React, { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";
import { type HockeyPlayerStats, getPlayerStatsPlayersStatsIdPlayerIdGet, type LastPlayerStats } from "../../client";
import { PlayerStatsDataGrid } from "./PlayerStatsDataGrid";
import { HockeyPlayerOwnershipChart } from "./HockeyPlayerOwnershipChart";

interface PlayerDashboardProps {
  selectedPlayer: LastPlayerStats | null;
}

export const PlayerDashboard: React.FC<PlayerDashboardProps> = ({ selectedPlayer }) => {

  const [playerStats,setPlayerStats] = useState<HockeyPlayerStats[]| null>(null);

  useEffect(()=>{
    if(!selectedPlayer){
      setPlayerStats(null);
      return
    }
    getPlayerStatsPlayersStatsIdPlayerIdGet({path:{player_id:selectedPlayer?.player_info.id}}).then(
      res => {
        if(res.data){
          setPlayerStats(res.data)
        }
      }
    )
  },[selectedPlayer])

  return (
    <Box sx={{ p: 3, height: '100%' }}>
      {selectedPlayer ? (
        <>
          <Typography variant="h4" gutterBottom>
            {selectedPlayer.player_info.name}
          </Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>
            {selectedPlayer.player_info.role}
          </Typography>
          <Typography variant="body1">
            {selectedPlayer.player_info.foreigner ? "Foreigner" : "Local"}
          </Typography>
          <PlayerStatsDataGrid playerStats={playerStats} />
          <HockeyPlayerOwnershipChart playerStats={playerStats} />

        </>
      ) : (
        <Typography variant="h6" color="text.secondary">
          Select a player to view details
        </Typography>
      )}
    </Box>
  );
};