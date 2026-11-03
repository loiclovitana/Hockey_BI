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
import PublicIcon from "@mui/icons-material/Public";
import SwissIcon from "../assets/flag-switzerland.svg";
import { type LastPlayerStats } from "../client/";
import { ValueWithDifference } from "./common/ValueWithDifference";

interface PlayerStatsTableProps {
  data: LastPlayerStats[];
}

const CLUB_COLUMN_WIDTH = 52;

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
        <Table
          aria-labelledby="tableTitle"
          size="small"
          sx={{
            "& .MuiTableCell-root:nth-child(-n + 2):not([colspan])": {
              position: "sticky",
              zIndex: 1,
              bgcolor: "background.paper",
            },
            "& .MuiTableCell-root:first-child:not([colspan])": {
              left: 0,
              width: CLUB_COLUMN_WIDTH,
              minWidth: CLUB_COLUMN_WIDTH,
              maxWidth: CLUB_COLUMN_WIDTH,
              boxSizing: "border-box",
              pr: 0.5,
            },
            "& .MuiTableCell-root:nth-child(2)": {
              left: CLUB_COLUMN_WIDTH,
              pl: 0.5,
            },
          }}
        >
          <TableHead>
            <TableRow>
              <TableCell></TableCell>
              <TableCell>Player</TableCell>
              <TableCell>Role</TableCell>
              <TableCell align="right">HM Pts</TableCell>
              <TableCell
                align="right"
                sx={{ display: { xs: "none", md: "table-cell" } }}
              >
                Goals
              </TableCell>
              <TableCell
                align="right"
                sx={{ display: { xs: "none", md: "table-cell" } }}
              >
                Assists
              </TableCell>
              <TableCell
                align="right"
                sx={{ display: { xs: "none", md: "table-cell" } }}
              >
                Matchs
              </TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Est. Value</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.length === 0 && (
              <TableRow>
                <TableCell colSpan={9} align="center" sx={{ py: 3 }}>
                  No players match the current filters.
                </TableCell>
              </TableRow>
            )}
            {visibleRows.map((row) => {
              return (
                <TableRow
                  role="checkbox"
                  tabIndex={-1}
                  key={row.player_info.id}
                >
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
                  <TableCell component="th" scope="row">
                    <Typography variant="body2" fontWeight="medium">
                      {row.player_info.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      {row.player_info.role}
                      {row.player_info.foreigner ? (
                        <PublicIcon
                          titleAccess="Foreign player"
                          sx={{ fontSize: 16 }}
                        />
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

                  <TableCell align="right">
                    {formatValue(row.player_stats?.hm_points)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ display: { xs: "none", md: "table-cell" } }}
                  >
                    {formatValue(row.player_stats?.goal)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ display: { xs: "none", md: "table-cell" } }}
                  >
                    {formatValue(row.player_stats?.assists)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ display: { xs: "none", md: "table-cell" } }}
                  >
                    {formatValue(row.player_stats?.appearances)}
                  </TableCell>
                  <TableCell align="right">
                    {formatValue(row.player_stats?.price)}
                  </TableCell>
                  <TableCell align="right">
                    {!row.player_stats ? (
                      "-"
                    ) : (
                      <ValueWithDifference
                        value={
                          row.player_stats.estimated_value ??
                          row.player_stats.price
                        }
                        baseValue={row.player_stats.price}
                      />
                    )}
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
