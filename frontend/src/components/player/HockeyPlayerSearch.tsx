import React, { useState, useMemo } from "react";
import {
  Box,
  ButtonBase,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import SwissIcon from "../../assets/flag-switzerland.svg";
import { type LastPlayerStats } from "../../client";

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
    <TableRow
      hover
      selected={isSelected}
      onClick={() => onSelect(player)}
      sx={{ cursor: "pointer" }}
    >
      <TableCell>
        {player.player_stats?.club ? (
          <Box
            component="img"
            src={`/club/${player.player_stats.club}.webp`}
            alt={player.player_stats.club}
            sx={{ width: 32, objectFit: "contain" }}
          />
        ) : (
          "-"
        )}
      </TableCell>
      <TableCell component="th" scope="row">
        <ButtonBase
          aria-pressed={isSelected}
          sx={{
            justifyContent: "flex-start",
            textAlign: "left",
            borderRadius: 0.5,
            "&.Mui-focusVisible": {
              outline: "2px solid",
              outlineColor: "primary.main",
              outlineOffset: 2,
            },
          }}
        >
          <Typography component="span" variant="body2" fontWeight="medium">
            {player.player_info.name}
          </Typography>
        </ButtonBase>
      </TableCell>
      <TableCell>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {player.player_info.role}
          {player.player_info.foreigner ? (
            <PublicIcon titleAccess="Foreign player" sx={{ fontSize: 16 }} />
          ) : (
            <Box
              component="img"
              src={SwissIcon}
              alt="Swiss player"
              sx={{ height: 16 }}
            />
          )}
        </Box>
      </TableCell>
      <TableCell align="right">{player.player_stats?.price ?? "-"}</TableCell>
    </TableRow>
  );
};

interface HockeyPlayerSearchProps {
  players: LastPlayerStats[];
  selectedPlayer?: LastPlayerStats | null;
  setSelectedHockeyPlayer: (player: LastPlayerStats) => void;
}

export const HockeyPlayerSearch: React.FC<HockeyPlayerSearchProps> = ({
  players,
  selectedPlayer,
  setSelectedHockeyPlayer,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(30);

  const normalizeString = (str: string) =>
    str
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const filteredPlayers = useMemo(
    () =>
      players.filter((player) =>
        normalizeString(player.player_info.name).includes(
          normalizeString(searchQuery),
        ),
      ),
    [players, searchQuery],
  );

  const currentPage = Math.min(
    page,
    Math.max(0, Math.ceil(filteredPlayers.length / rowsPerPage) - 1),
  );

  const paginatedPlayers = useMemo(() => {
    const startIndex = currentPage * rowsPerPage;
    return filteredPlayers.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredPlayers, currentPage, rowsPerPage]);

  return (
    <Box
      sx={{
        height: "100%",
        minHeight: 0,
        boxSizing: "border-box",
        display: "flex",
        flexDirection: "column",
        p: 1,
      }}
    >
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search players..."
        size="small"
        value={searchQuery}
        onChange={(e) => {
          setSearchQuery(e.target.value);
          setPage(0);
        }}
        sx={{
          mb: 1,
        }}
      />
      <TableContainer sx={{ flex: 1, minHeight: 0 }}>
        <Table
          stickyHeader
          size="small"
          aria-label="Select a hockey player"
          sx={{
            "& .MuiTableCell-root:first-child:not([colspan])": {
              width: 52,
              minWidth: 52,
              maxWidth: 52,
              boxSizing: "border-box",
              pr: 0.5,
            },
            "& .MuiTableCell-root:nth-child(2)": {
              pl: 0.5,
            },
            "& .MuiTableCell-root:nth-child(n + 3):not([colspan])": {
              px: 1,
            },
          }}
        >
          <TableHead>
            <TableRow>
              <TableCell>Club</TableCell>
              <TableCell>Player Name</TableCell>
              <TableCell>Role</TableCell>
              <TableCell align="right">Price</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredPlayers.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} align="center" sx={{ py: 3 }}>
                  No players match the current search.
                </TableCell>
              </TableRow>
            )}
            {paginatedPlayers.map((player) => (
              <HockeyPlayerItem
                key={player.player_info.id}
                player={player}
                isSelected={
                  selectedPlayer?.player_info.id === player.player_info.id
                }
                onSelect={setSelectedHockeyPlayer}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 30, 50]}
        component="div"
        count={filteredPlayers.length}
        rowsPerPage={rowsPerPage}
        page={currentPage}
        onPageChange={(_, newPage) => setPage(newPage)}
        onRowsPerPageChange={(event) => {
          setRowsPerPage(parseInt(event.target.value, 10));
          setPage(0);
        }}
        labelRowsPerPage="Rows:"
        sx={{
          flexShrink: 0,
          "& .MuiTablePagination-toolbar": {
            px: 0,
            flexWrap: "wrap",
            justifyContent: "flex-end",
          },
          "& .MuiTablePagination-spacer": { display: "none" },
          "& .MuiTablePagination-selectRoot": { mx: 1 },
          "& .MuiTablePagination-actions": { ml: 1 },
        }}
      />
    </Box>
  );
};
