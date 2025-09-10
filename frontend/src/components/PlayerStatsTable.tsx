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
  Checkbox,
  Typography,
  Box,
} from "@mui/material";
import { type LastPlayerStats } from "../client/";

interface PlayerStatsTableProps {
  data: LastPlayerStats[];
  onSelectionChange?: (selectedIds: number[]) => void;
}

export const PlayerStatsTable: React.FC<PlayerStatsTableProps> = ({
  data,
  onSelectionChange,
}) => {
  const [selected, setSelected] = useState<number[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const newSelected = data.map((item) => item.player_info.id);
      setSelected(newSelected);
      onSelectionChange?.(newSelected);
      return;
    }
    setSelected([]);
    onSelectionChange?.([]);
  };

  const handleClick = (id: number) => {
    const selectedIndex = selected.indexOf(id);
    let newSelected: number[] = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, id);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }

    setSelected(newSelected);
    onSelectionChange?.(newSelected);
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

  const isSelected = (id: number) => selected.indexOf(id) !== -1;

  const emptyRows =
    page > 0 ? Math.max(0, (1 + page) * rowsPerPage - data.length) : 0;

  const visibleRows = data.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage,
  );

  return (
    <Paper sx={{ width: "100%", pb: 2 }}>
      <TableContainer>
        <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle">
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  color="primary"
                  indeterminate={
                    selected.length > 0 && selected.length < data.length
                  }
                  checked={data.length > 0 && selected.length === data.length}
                  onChange={handleSelectAllClick}
                  inputProps={{
                    "aria-label": "select all players",
                  }}
                />
              </TableCell>
              <TableCell>Player Name</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Club</TableCell>
              <TableCell align="right">HM Points</TableCell>
              <TableCell align="right">Goals</TableCell>
              <TableCell align="right">Assists</TableCell>
              <TableCell align="right">Appearances</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Estimated Value</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {visibleRows.map((row) => {
              const isItemSelected = isSelected(row.player_info.id);
              const labelId = `enhanced-table-checkbox-${row.player_info.id}`;

              return (
                <TableRow
                  hover
                  onClick={() => handleClick(row.player_info.id)}
                  role="checkbox"
                  aria-checked={isItemSelected}
                  tabIndex={-1}
                  key={row.player_info.id}
                  selected={isItemSelected}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      color="primary"
                      checked={isItemSelected}
                      inputProps={{
                        "aria-labelledby": labelId,
                      }}
                    />
                  </TableCell>
                  <TableCell
                    component="th"
                    id={labelId}
                    scope="row"
                    padding="none"
                  >
                    <Typography variant="body2" fontWeight="medium">
                      {row.player_info.name}
                    </Typography>
                  </TableCell>
                  <TableCell>{row.player_info.role}</TableCell>
                  <TableCell>{row.player_stats?.club || "-"}</TableCell>

                  <TableCell align="right">
                    {row.player_stats?.hm_points || "-"}
                  </TableCell>
                  <TableCell align="right">
                    {row.player_stats?.goal || "-"}
                  </TableCell>
                  <TableCell align="right">
                    {row.player_stats?.assists || "-"}
                  </TableCell>
                  <TableCell align="right">
                    {row.player_stats?.appearances || "-"}
                  </TableCell>
                  <TableCell align="right">
                    {row.player_stats?.price || "-"}
                  </TableCell>
                  <TableCell align="right">
                    {(() => {
                      if (!row.player_stats) {
                        return "-";
                      }
                      const price = row.player_stats.price;
                      const estimatedValue =
                        row.player_stats.estimated_value || price;

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
                <TableCell colSpan={10} />
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
