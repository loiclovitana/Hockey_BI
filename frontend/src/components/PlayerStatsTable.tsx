import React, { useState } from "react";
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
import { type LastPlayerStats } from "../client/";

interface PlayerStatsTableProps {
  data: LastPlayerStats[];
}

export const PlayerStatsTable: React.FC<PlayerStatsTableProps> = ({ data }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const formatValue = (value: number | null | undefined): string => {
    return value === null || value === undefined ? "-" : value.toString();
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
    page > 0 ? Math.max(0, (1 + page) * rowsPerPage - data.length) : 0;

  const visibleRows = data.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage,
  );

  return (
    <Paper sx={{ width: "100%", py: 1 }}>
      <TableContainer>
        <Table aria-labelledby="tableTitle" size="small">
          <TableHead>
            <TableRow>
              <TableCell>Player Name</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Club</TableCell>
              <TableCell align="right">HM Points</TableCell>
              <TableCell align="right" sx={{ display: { xs: 'none', md: 'table-cell' } }}>Goals</TableCell>
              <TableCell align="right" sx={{ display: { xs: 'none', md: 'table-cell' } }}>Assists</TableCell>
              <TableCell align="right" sx={{ display: { xs: 'none', md: 'table-cell' } }}>Matchs</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Estimated Value</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {visibleRows.map((row) => {
              return (
                <TableRow
                  role="checkbox"
                  tabIndex={-1}
                  key={row.player_info.id}
                >
                  <TableCell component="th" scope="row">
                    <Typography variant="body2" fontWeight="medium">
                      {row.player_info.name}
                    </Typography>
                  </TableCell>
                  <TableCell>{row.player_info.role}</TableCell>
                  <TableCell>
                    {row.player_stats?.club ? (
                      <Box
                        component="img"
                        src={`/club/${row.player_stats.club}.webp`}
                        alt={row.player_stats.club}
                        sx={{
                          width: 32,
                          objectFit: "contain",
                        }}
                      />
                    ) : (
                      "-"
                    )}
                  </TableCell>

                  <TableCell align="right">
                    {formatValue(row.player_stats?.hm_points)}
                  </TableCell>
                  <TableCell align="right" sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                    {formatValue(row.player_stats?.goal)}
                  </TableCell>
                  <TableCell align="right" sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                    {formatValue(row.player_stats?.assists)}
                  </TableCell>
                  <TableCell align="right" sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                    {formatValue(row.player_stats?.appearances)}
                  </TableCell>
                  <TableCell align="right">
                    {formatValue(row.player_stats?.price)}
                  </TableCell>
                  <TableCell align="right">
                    {(() => {
                      if (!row.player_stats) {
                        return "-";
                      }
                      const price = row.player_stats.price;
                      const estimatedValue =
                        row.player_stats.estimated_value ?? price;

                      const difference = estimatedValue - price;
                      const sign = difference > 0 ? "+" : "";
                      const color =
                        difference > 0
                          ? "success.main"
                          : difference < 0
                            ? "error.main"
                            : "primary.main";
                      return (
                        <Box component="span">
                          {estimatedValue.toFixed(1)}{" "}
                          <Box component="span" sx={{ color }}>
                            ({sign}
                            {difference.toFixed(1)})
                          </Box>
                        </Box>
                      );
                    })()}
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
                <TableCell colSpan={9} />
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={data.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
};
