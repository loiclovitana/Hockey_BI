import React, { useMemo } from "react";
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import type { Team, LastPlayerStats, TeamModification } from "../../client";

interface AdaptationsListProps {
  modifications: TeamModification[];
  transfers: Team[];
  playerStats: LastPlayerStats[];
  onRemoveModification: (index: number) => void;
}

export const AdaptationsList: React.FC<AdaptationsListProps> = ({
  modifications,
  transfers,
  playerStats,
  onRemoveModification,
}) => {
  const adaptationsData = useMemo(() => {
    return modifications.map((mod) => {
      const transfer = transfers.find((t) => t.id === mod.team_id);
      const originalPlayer = playerStats.find(
        (p) => p.player_info.id === transfer?.player_id,
      );
      const replacedPlayer = playerStats.find(
        (p) => p.player_info.id === mod.replaced_player_id,
      );

      return {
        originalPlayerName: originalPlayer
          ? originalPlayer.player_info.name
          : "Unknown",
        replacedPlayerName: replacedPlayer
          ? replacedPlayer.player_info.name
          : "Unknown",
        fromDate: transfer?.from_datetime
          ? new Date(transfer.from_datetime).toLocaleDateString()
          : "-",
        toDate: transfer?.to_datetime
          ? new Date(transfer.to_datetime).toLocaleDateString()
          : "-",
      };
    });
  }, [modifications, transfers, playerStats]);

  if (modifications.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Adaptations
      </Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Original Player</TableCell>
              <TableCell>Replaced By</TableCell>
              <TableCell>From Date</TableCell>
              <TableCell>To Date</TableCell>
              <TableCell align="center">Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {adaptationsData.map((adaptation, index) => (
              <TableRow key={index}>
                <TableCell>{adaptation.originalPlayerName}</TableCell>
                <TableCell>{adaptation.replacedPlayerName}</TableCell>
                <TableCell>{adaptation.fromDate}</TableCell>
                <TableCell>{adaptation.toDate}</TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => onRemoveModification(index)}
                    aria-label="remove modification"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
