import React, { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";
import { type HockeyPlayerStats, type HockeyPlayer, getPlayerStatsPlayersStatsIdPlayerIdGet } from "../client";
import { PlayerStatsDataGrid } from "./PlayerStatsDataGrid";
import { HockeyPlayerOwnershipChart } from "./HockeyPlayerOwnershipChart";

interface PlayerDashboardProps {
  selectedPlayer: HockeyPlayer | null;
}

export const PlayerDashboard: React.FC<PlayerDashboardProps> = ({ selectedPlayer }) => {

  const [playerStats,setPlayerStats] = useState<HockeyPlayerStats[]| null>(null);

  useEffect(()=>{
    if(!selectedPlayer){
      setPlayerStats(null);
      return
    }
    getPlayerStatsPlayersStatsIdPlayerIdGet({path:{player_id:selectedPlayer?.id}}).then(
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
            {selectedPlayer.name}
          </Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>
            {selectedPlayer.role}
          </Typography>
          <Typography variant="body1">
            {selectedPlayer.foreigner ? "Foreigner" : "Local"}
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