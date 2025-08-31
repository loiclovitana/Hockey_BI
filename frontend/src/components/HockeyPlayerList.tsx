import React, { useState, useMemo } from "react";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Box,
  TextField,
  Pagination,
} from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import  SwissIcon   from "../assets/flag-switzerland.svg";
import { type LastPlayerStats } from "../client";

interface HockeyPlayerItemProps {
  player: LastPlayerStats;
  isSelected: boolean;
  onSelect: (player: LastPlayerStats) => void;
}

const HockeyPlayerItem: React.FC<HockeyPlayerItemProps> = ({
  player,
  isSelected,
  onSelect,
}) => {
  return (
    <ListItem disablePadding>
      <ListItemButton
        selected={isSelected}
        onClick={() => onSelect(player)}
      >
        <ListItemText
          primary={player.player_info.name}
          secondary={
            <span>{player.player_info.role}
            {player.player_info.foreigner ? (
              <PublicIcon sx={{ fontSize: 16,mx:1 }} />
            ) : (
              <img src={SwissIcon} style={{height:"16px",marginLeft:"5px"}}></img>
            )}
            </span>
          }
        />
      </ListItemButton>
    </ListItem>
  );
};

interface HockeyPlayerListProps {
  players: LastPlayerStats[];
  selectedPlayer?: LastPlayerStats|null;
  setSelectedHockeyPlayer: (player: LastPlayerStats) => void;
}

export const HockeyPlayerList: React.FC<HockeyPlayerListProps> = ({
  players,
  selectedPlayer,
  setSelectedHockeyPlayer,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);
  const PLAYER_PER_PAGE = 30;

  const normalizeString = (str: string) =>
    str
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const filteredPlayers = useMemo(() => 
    players.filter((player) =>
      normalizeString(player.player_info.name).includes(normalizeString(searchQuery))
    ), [players, searchQuery]);

  const totalPages = Math.ceil(filteredPlayers.length / PLAYER_PER_PAGE);
  
  const paginatedPlayers = useMemo(() => {
    const startIndex = (page - 1) * PLAYER_PER_PAGE;
    return filteredPlayers.slice(startIndex, startIndex + PLAYER_PER_PAGE);
  }, [filteredPlayers, page]);
  
  
  return (
    <Box sx={{ flex: 1, height: "100%", display: "flex", flexDirection: "column" }}>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search players..."
        size="small"
        value={searchQuery}
        onChange={(e) => {
          setSearchQuery(e.target.value);
          setPage(1);
        }}
        sx={{ 
          backgroundColor: "background.paper",
          boxShadow: 1,
          mt:2
        }}
      />
      <List sx={{ flex: 1, overflow: 'auto', pt:1 }}>
        {paginatedPlayers.map((player) => (
          <HockeyPlayerItem
            key={player.player_info.id}
            player={player}
            isSelected={selectedPlayer?.player_info.id === player.player_info.id}
            onSelect={setSelectedHockeyPlayer}
          />
        ))}
      </List>
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
          <Pagination 
            count={totalPages} 
            page={page} 
            onChange={(_, newPage) => setPage(newPage)}
            color="primary"
            size="small"
          />
        </Box>
      )}
    </Box>
  );
};