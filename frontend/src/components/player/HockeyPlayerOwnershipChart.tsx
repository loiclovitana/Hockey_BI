import React from "react";
import { LineChart } from "@mui/x-charts/LineChart";
import { Box, Typography, useTheme, useMediaQuery } from "@mui/material";
import { type HockeyPlayerStats } from "../../client";

interface HockeyPlayerOwnershipChartProps {
  playerStats: HockeyPlayerStats[] | null;
}

export const HockeyPlayerOwnershipChart: React.FC<
  HockeyPlayerOwnershipChartProps
> = ({ playerStats }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
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
    .filter((stat) => stat.ownership !== null && stat.ownership !== undefined)
    .sort(
      (a, b) =>
        new Date(a.validity_date).getTime() -
        new Date(b.validity_date).getTime(),
    )
    .map((stat) => ({
      date: new Date(stat.validity_date),
      ownership: stat.ownership as number,
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
    <Box sx={{ pt: 3, width: "100%", overflow: "hidden" }}>
      <Typography variant={isMobile ? "body1" : "h6"} gutterBottom>
        Ownership Over Time
      </Typography>
      <Box sx={{ width: "100%", overflowX: "auto", height:"50vh",maxHeight:500 }}>
        <LineChart
          series={[
            {
              data: ownershipData.map((d) => d.ownership),
              label: "Ownership %",
              showMark: false,
            },
          ]}
          xAxis={[
            {
              data: ownershipData.map((d) => d.date),
              scaleType: "time",
              valueFormatter: (date) =>
                isMobile
                  ? date.toLocaleDateString("de", {
                      month: "short",
                      day: "numeric",
                    })
                  : date.toLocaleDateString(),
              ...(!isMobile && { label: "Date" }),
            },
          ]}
          yAxis={[
            {
              ...(!isMobile && { label: "Ownership (%)" }),
            },
          ]}
          hideLegend
          sx={{ pl: 0 }}
          grid={{ vertical: true, horizontal: true }}
        />
      </Box>
    </Box>
  );
};
