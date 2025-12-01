import React, { useState, useMemo, useContext } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  Paper,
  Typography,
  Box,
} from "@mui/material";
import { type Team } from "../../client/";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";

interface TransferListTableProps {
  transfers: Team[];
  selectedDate: string | null;
}

export const TransferListTable: React.FC<TransferListTableProps> = ({
  transfers,
  selectedDate
}) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { playerStats } = useContext(PlayerStatsContext);

  // Create a map of player_id to player info
  const playerMap = useMemo(() => {
    const map = new Map();
    playerStats?.forEach(stat => {
      map.set(stat.player_info.id, stat.player_info);
    });
    return map;
  }, [playerStats]);

  // Filter transfers by selected date
  const filteredTransfers = useMemo(() => {
    if (!selectedDate) return [];

    return transfers.filter(transfer => {
      const fromDate = transfer.from_datetime
        ? new Date(transfer.from_datetime).toISOString().split('T')[0]
        : null;
      const toDate = transfer.to_datetime
        ? new Date(transfer.to_datetime).toISOString().split('T')[0]
        : null;

      return fromDate === selectedDate || toDate === selectedDate;
    });
  }, [transfers, selectedDate]);

  const formatDateTime = (dateTime: string | null | undefined): string => {
    if (!dateTime) return "-";
    return new Date(dateTime).toLocaleDateString();
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const emptyRows =
    page > 0 ? Math.max(0, (1 + page) * rowsPerPage - filteredTransfers.length) : 0;

  const visibleRows = filteredTransfers.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage,
  );

  if (!selectedDate) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          Click on a transfer date in the timeline to view transfers
        </Typography>
      </Box>
    );
  }

  if (filteredTransfers.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          No transfers found for {new Date(selectedDate).toLocaleDateString()}
        </Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ width: "100%", py: 1, mt: 3 }}>
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="h6" gutterBottom>
          Transfers on {new Date(selectedDate).toLocaleDateString()}
        </Typography>
      </Box>

      <TableContainer>
        <Table aria-labelledby="transfersTable" size="small">
          <TableHead>
            <TableRow>
              <TableCell>Player Name</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>From Date</TableCell>
              <TableCell>To Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {visibleRows.map((transfer) => {
              const playerInfo = playerMap.get(transfer.player_id);
              return (
                <TableRow
                  key={transfer.id}
                  tabIndex={-1}
                >
                  <TableCell component="th" scope="row">
                    <Typography variant="body2" fontWeight="medium">
                      {playerInfo?.name || `Player ${transfer.player_id}`}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {playerInfo?.role || "-"}
                  </TableCell>
                  <TableCell>
                    {formatDateTime(transfer.from_datetime)}
                  </TableCell>
                  <TableCell>
                    {formatDateTime(transfer.to_datetime)}
                  </TableCell>
                </TableRow>
              );
            })}
            {emptyRows > 0 && (
              <TableRow
                style={{
                  height: 53 * emptyRows,
                }}
              >
                <TableCell colSpan={4} />
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={filteredTransfers.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
};
