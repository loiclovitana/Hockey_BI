import React from "react";
import { LineChart } from "@mui/x-charts/LineChart";
import { Box, Typography } from "@mui/material";
import { type HockeyPlayerStats } from "../client";

interface HockeyPlayerOwnershipChartProps {
  playerStats: HockeyPlayerStats[] | null;
}

export const HockeyPlayerOwnershipChart: React.FC<HockeyPlayerOwnershipChartProps> = ({ playerStats }) => {
  if (!playerStats || playerStats.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          No ownership data available
        </Typography>
      </Box>
    );
  }

  const ownershipData = playerStats
    .filter(stat => stat.ownership !== null && stat.ownership !== undefined)
    .sort((a, b) => new Date(a.validity_date).getTime() - new Date(b.validity_date).getTime())
    .map(stat => ({
      date: new Date(stat.validity_date),
      ownership: stat.ownership as number
    }));

  if (ownershipData.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          No ownership data available for this player
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Ownership Over Time
      </Typography>
      <LineChart
        width={800}
        height={400}
        series={[
          {
            data: ownershipData.map(d => d.ownership),
            label: "Ownership %",
            color: "#1976d2"
          }
        ]}
        xAxis={[{
          data: ownershipData.map(d => d.date),
          label: "Date",
          scaleType: "time",
          valueFormatter: (date) => date.toLocaleDateString()
        }]}
        yAxis={[{
          label: "Ownership (%)",
          min: 0,
          max: 100
        }]}
        margin={{ left: 60, right: 30, top: 30, bottom: 60 }}
        grid={{ vertical: true, horizontal: true }}
      />
    </Box>
  );
};