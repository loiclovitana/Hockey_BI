import React, { useState } from "react";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Box,
  TextField,
} from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import  SwissIcon   from "../assets/flag-switzerland.svg";
import { type HockeyPlayer } from "../client";

interface HockeyPlayerListProps {
  players: HockeyPlayer[];
  selectedPlayer?: HockeyPlayer|null;
  setSelectedHockeyPlayer: (player: HockeyPlayer) => void;
}

export const HockeyPlayerList: React.FC<HockeyPlayerListProps> = ({
  players,
  selectedPlayer,
  setSelectedHockeyPlayer,
}) => {
  const [searchQuery, setSearchQuery] = useState("");

  const handlePlayerSelect = (player: HockeyPlayer) => {
    setSelectedHockeyPlayer(player);
  };

  const normalizeString = (str: string) =>
    str
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const filteredPlayers = players.filter((player) =>
    normalizeString(player.name).includes(normalizeString(searchQuery))
  );

  return (
    <Box sx={{ flex: 1, height: "100%", display: "flex", flexDirection: "column" }}>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search players..."
        size="small"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ 
          backgroundColor: "background.paper",
          boxShadow: 1,
          mt:2
        }}
      />
      <List  sx={{ flex: 1, overflow: 'auto', pt:1 }}>
        {filteredPlayers.map((player) => (
          <ListItem key={player.id} disablePadding>
            <ListItemButton
              selected={selectedPlayer?.id === player.id}
              onClick={() => handlePlayerSelect(player)}
            >
              <ListItemText
                primary={player.name}
                secondary={
                    <span>{player.role}
                    {player.foreigner ? (
                      <PublicIcon sx={{ fontSize: 16,mx:1 }} />
                    ) : (
                      <img src={SwissIcon} style={{height:"16px",marginLeft:"5px"}}></img>
                    )}
                    </span>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};