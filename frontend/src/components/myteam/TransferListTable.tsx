import React, { useMemo, useContext, useState, useId } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Button,
  Menu,
  MenuItem,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { type Team } from "../../client/";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";

interface TransferListTableProps {
  transfers: Team[];
  selectedDate: string | null;
  availableDates: Set<string>;
  onDateSelect: (date: string) => void;
  selectedPlayerId: number | null;
  onPlayerSelect: (playerId: number) => void;
}

export const TransferListTable: React.FC<TransferListTableProps> = ({
  transfers,
  selectedDate,
  availableDates,
  onDateSelect,
  selectedPlayerId: selectedRowId,
  onPlayerSelect: onRowSelect,
}) => {
  const { playerStats } = useContext(PlayerStatsContext);
  const [dateMenuAnchor, setDateMenuAnchor] = useState<HTMLElement | null>(
    null,
  );
  const dateMenuId = useId();
  const dateButtonId = `${dateMenuId}-button`;
  const dateOptions = [
    { value: "start", label: "Starting Team" },
    ...Array.from(availableDates)
      .sort()
      .map((date) => ({
        value: date,
        label: `Transfers on ${new Date(date).toLocaleDateString()}`,
      })),
    { value: "current", label: "Current Team" },
  ];

  // Create a map of player_id to player info
  const playerMap = useMemo(() => {
    const map = new Map();
    playerStats?.forEach((stat) => {
      map.set(stat.player_info.id, stat.player_info);
    });
    return map;
  }, [playerStats]);

  // Filter transfers by selected date
  const filteredTransfers = useMemo(() => {
    if (!selectedDate) return [];

    // Handle special cases
    if (selectedDate === "start") {
      return transfers.filter((transfer) => !transfer.from_datetime);
    }

    if (selectedDate === "current") {
      return transfers.filter((transfer) => !transfer.to_datetime);
    }

    // Handle regular date filtering
    return transfers.filter((transfer) => {
      const fromDate = transfer.from_datetime
        ? new Date(transfer.from_datetime).toISOString().split("T")[0]
        : null;
      const toDate = transfer.to_datetime
        ? new Date(transfer.to_datetime).toISOString().split("T")[0]
        : null;

      return fromDate === selectedDate || toDate === selectedDate;
    });
  }, [transfers, selectedDate]);

  const formatDateTime = (dateTime: string | null | undefined): string => {
    if (!dateTime) return "-";
    return new Date(dateTime).toLocaleDateString();
  };

  if (!selectedDate) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          Click on a transfer date in the timeline to view transfers
        </Typography>
      </Box>
    );
  }

  const getDisplayTitle = () => {
    if (selectedDate === "start") return "Starting Team";
    if (selectedDate === "current") return "Current Team";
    return `Transfers on ${new Date(selectedDate).toLocaleDateString()}`;
  };

  const getNoDataMessage = () => {
    if (selectedDate === "start") return "No starting team players found";
    if (selectedDate === "current") return "No current team players found";
    return `No transfers found for ${new Date(selectedDate).toLocaleDateString()}`;
  };

  if (filteredTransfers.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          {getNoDataMessage()}
        </Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ width: "100%", py: 1, mt: 3 }}>
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          <Button
            id={dateButtonId}
            aria-controls={dateMenuAnchor ? dateMenuId : undefined}
            aria-haspopup="menu"
            aria-expanded={dateMenuAnchor ? "true" : undefined}
            onClick={(event) => setDateMenuAnchor(event.currentTarget)}
            endIcon={<ExpandMoreIcon />}
            sx={{
              typography: "h6",
              textTransform: "none",
              color: "text.primary",
              textAlign: "left",
            }}
          >
            {getDisplayTitle()}
          </Button>
        </Typography>
        <Menu
          id={dateMenuId}
          anchorEl={dateMenuAnchor}
          open={Boolean(dateMenuAnchor)}
          onClose={() => setDateMenuAnchor(null)}
          slotProps={{ list: { "aria-labelledby": dateButtonId } }}
        >
          {dateOptions.map(({ value, label }) => (
            <MenuItem
              key={value}
              selected={selectedDate === value}
              onClick={() => {
                onDateSelect(value);
                setDateMenuAnchor(null);
              }}
            >
              {label}
            </MenuItem>
          ))}
        </Menu>
      </Box>

      <TableContainer>
        <Table aria-labelledby={dateButtonId} size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>From</TableCell>
              <TableCell>To</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredTransfers.map((transfer) => {
              const playerInfo = playerMap.get(transfer.player_id);
              const isSelected = selectedRowId === transfer.id;
              return (
                <TableRow
                  key={transfer.id}
                  tabIndex={-1}
                  hover
                  selected={isSelected}
                  onClick={() => onRowSelect(transfer.id)}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell component="th" scope="row">
                    <Typography variant="body2" fontWeight="medium">
                      {playerInfo?.name || `Player ${transfer.player_id}`}
                    </Typography>
                  </TableCell>
                  <TableCell>{playerInfo?.role || "-"}</TableCell>
                  <TableCell>
                    {formatDateTime(transfer.from_datetime)}
                  </TableCell>
                  <TableCell>{formatDateTime(transfer.to_datetime)}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};
