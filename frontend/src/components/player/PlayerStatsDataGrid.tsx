import React from "react";
import { Box, Typography } from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { type HockeyPlayerStats } from "../../client";

interface PlayerStatsDataGridProps {
  playerStats: HockeyPlayerStats[] | null;
}

export const PlayerStatsDataGrid: React.FC<PlayerStatsDataGridProps> = ({ playerStats }) => {
  if (!playerStats || playerStats.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        No stats available
      </Typography>
    );
  }

  const columns: GridColDef[] = [
    { 
      field: 'validity_date', 
      headerName: 'Date', 
      width: 120,
      valueFormatter: (value) => {
        if (!value) return '-';
        return new Date(value).toISOString().split('T')[0];
      }
    },
    { field: 'club', headerName: 'Club', width: 80 },
    { field: 'price', headerName: 'Price', type: 'number', width: 100 },
    { field: 'appearances', headerName: 'Appearances', type: 'number', width: 120 },
    { field: 'goal', headerName: 'Goals', type: 'number', width: 80 },
    { field: 'assists', headerName: 'Assists', type: 'number', width: 80 },
    { field: 'penalties', headerName: 'Penalties', type: 'number', width: 100 },
    { field: 'plus_minus', headerName: '+/-', type: 'number', width: 80 },
    { field: 'hm_points', headerName: 'HM Points', type: 'number', width: 100 },
    { 
      field: 'ownership', 
      headerName: 'Ownership %', 
      type: 'number', 
      width: 120,
      valueFormatter: (value) => value ? `${value}%` : '-'
    },
  ];

  const rows = playerStats.map((stats, index) => ({
    id: `${stats.season_id}-${stats.player_id}-${index}`,
    validity_date: stats.validity_date,
    club: stats.club,
    price: stats.price,
    appearances: stats.appearances,
    goal: stats.goal,
    assists: stats.assists,
    penalties: stats.penalties,
    plus_minus: stats.plus_minus,
    hm_points: stats.hm_points,
    ownership: stats.ownership,
  }));

  return (
    <Box sx={{ height: 400, width: '100%', mt: 2 }}>
      <DataGrid
        rows={rows}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 10,
            },
          },
          sorting: {
            sortModel: [{ field: 'validity_date', sort: 'desc' }],
          },
        }}
        pageSizeOptions={[5, 10, 25]}
        disableRowSelectionOnClick
      />
    </Box>
  );
};