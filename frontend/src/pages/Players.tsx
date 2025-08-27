import React, { useEffect, useState } from "react";
import { Box } from "@mui/material";
import { type HockeyPlayer, getPlayersPlayersGet } from "../client"
import { HockeyPlayerList } from "../components/HockeyPlayerList";
import { PlayerDashboard } from "../components/PlayerDashboard";



export const Players: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<HockeyPlayer[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<HockeyPlayer|null>(null);
  
  useEffect(() => {
    const response = getPlayersPlayersGet().then(response => { 
    if (response.error) {
      console.error(response.error)
    }
    if (response.data) {
      setPlayers(response.data);
    }
  }).catch(

  ).finally(
    () => setLoading(false)
  )
}, [])

return (
  <Box sx={{ display: 'flex', height: 'calc(100vh - 64px)', gap: 2, p: 2 }}>
    <Box sx={{ 
      width: '300px', 
      minWidth: '300px',
      height: '100%',
    }}>
      <HockeyPlayerList players={players} setSelectedHockeyPlayer={setSelectedPlayer} selectedPlayer={selectedPlayer}/>
    </Box>
    
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
