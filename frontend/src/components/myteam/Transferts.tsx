import React from "react";
import { Box, Typography, useTheme, useMediaQuery } from "@mui/material";
import { LineChart, lineElementClasses, markElementClasses } from "@mui/x-charts/LineChart";
import { ChartsReferenceLine } from '@mui/x-charts/ChartsReferenceLine';
import { type TeamValueEvolution } from "../../client/";

interface TransfertsProps {
  teamEvolution: TeamValueEvolution|null;
  adaptedTeamEvolution: TeamValueEvolution|null;
  transfertTimes?: Set<string>;
  onTransfertDayClick?: (day: string) => void;
  selectedTransfertDate?: string|null;
}

export const Transferts: React.FC<TransfertsProps> = ({ teamEvolution, adaptedTeamEvolution, transfertTimes, onTransfertDayClick, selectedTransfertDate }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  if (!teamEvolution && !adaptedTeamEvolution) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          No team value evolution data available
        </Typography>
      </Box>
    );
  }

  // Prepare data for chart
  const sortedTeamEvolution = teamEvolution?.evolution
    ? [...teamEvolution.evolution].sort(
        (a, b) => new Date(a.at).getTime() - new Date(b.at).getTime()
      )
    : [];

  const sortedAdaptedEvolution = adaptedTeamEvolution?.evolution
    ? [...adaptedTeamEvolution.evolution].sort(
        (a, b) => new Date(a.at).getTime() - new Date(b.at).getTime()
      )
    : [];

  // Use the longer dataset for x-axis
  const dates = sortedTeamEvolution.length >= sortedAdaptedEvolution.length
    ? sortedTeamEvolution.map((d) => new Date(d.at))
    : sortedAdaptedEvolution.map((d) => new Date(d.at));

  if (dates.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          No team value evolution data available
        </Typography>
      </Box>
    );
  }

  // Prepare series data
  const series = [];

  if (teamEvolution?.evolution && sortedTeamEvolution.length > 0) {
    series.push({
      data: sortedTeamEvolution.map((d) => d.value),
      label: "Team Value",
      showMark: false,
      color: theme.palette.primary.main,
      id:"v1"
    });
    series.push({
      data: sortedTeamEvolution.map((d) => d.theorical_value),
      label: "Team Theoretical Value",
      showMark: false,
      color: theme.palette.primary.main,
      id:"vt1"
    });
  }

  if (adaptedTeamEvolution?.evolution && sortedAdaptedEvolution.length > 0) {
    series.push({
      data: sortedAdaptedEvolution.map((d) => d.value),
      label: "Adapted Team Value",
      showMark: false,
      color: "#ff9800",
      id:"vt2"
    });
    series.push({
      data: sortedAdaptedEvolution.map((d) => d.theorical_value),
      label: "Adapted Team Theoretical Value",
      showMark: false,
      color: "#ff9800",
      strokeDasharray: "5 5",
      id:"vt2"
    });
  }

  // Convert transfer times to Date objects for reference lines
  const transferDates = transfertTimes
    ? Array.from(transfertTimes).map(dateStr => new Date(dateStr))
    : [];

  // Calculate position of each transfer date on the timeline
  const getTransferPosition = (transferDate: Date) => {
    if (dates.length === 0) return 0;
    const minTime = dates[0].getTime();
    const maxTime = dates[dates.length - 1].getTime();
    const transferTime = transferDate.getTime();
    return ((transferTime - minTime) / (maxTime - minTime)) * 100;
  };

  return (
    <Box sx={{ pt: 3, width: "100%", overflow: "hidden" }}>
      
      <Box
        sx={{
          width: "100%",
          height: "50vh",
          maxHeight: 500,
        }}
      >
        <LineChart
          series={series}
          xAxis={[
            {
              data: dates,
              scaleType: "time",
              min:dates[0],
              max:dates[dates.length-1],
              valueFormatter: (date) =>
                isMobile
                  ? date.toLocaleDateString("en", {
                      month: "short",
                      day: "numeric",
                    })
                  : date.toLocaleDateString(),
              ...(!isMobile && { label: "Date" }),
            },
          ]}
          yAxis={[
            {
              ...(!isMobile && { label: "Team Value" }),
            },
          ]}
          grid={{ vertical: true, horizontal: true }}
          sx={{
            [`.${lineElementClasses.root}[data-series="vt1"]`]: {
                strokeDasharray: '5 5',
              },
            [`.${lineElementClasses.root}[data-series="vt2"]`]: {
                strokeDasharray: '5 5',
              },
            "& .MuiChartsReferenceLine-root": {
              stroke: theme.palette.error.main,
              strokeWidth: 2,
              strokeDasharray: "3 3",
              cursor: "pointer",
              "&:hover": {
                strokeWidth: 3,
              }
            },
          }}
        >
          {transferDates.map((date) => (
            <ChartsReferenceLine
              key={`transfer-${date.toISOString()}`}
              x={date}
              label=""
              lineStyle={{ stroke: date.toISOString().split('T')[0]===selectedTransfertDate? theme.palette.success.main:theme.palette.secondary.main, strokeDasharray: "3 3" }}
            />
          ))}
        </LineChart>
      </Box>

      {/* Clickable Timeline for Transfer Days */}
      {transferDates.length > 0 && (
        <Box sx={{  px: 2,pl:8 }}>
          <Box
            sx={{
              position: "relative",
              width: "100%",
              height: 40,
              backgroundColor: theme.palette.background.paper,
              borderRadius: 1,
              border: `1px solid ${theme.palette.divider}`,
              mt: 1,
            }}
          >
            {transferDates.map((date) => {
              const position = getTransferPosition(date);
              const dateStr = date.toISOString().split('T')[0];
              const isSelected = selectedTransfertDate === dateStr;
              console.log(dateStr,selectedTransfertDate)
              return (
                <Box
                  key={`timeline-${date.toISOString()}`}
                  onClick={() => onTransfertDayClick?.(dateStr)}
                  sx={{
                    position: "absolute",
                    left: `${position}%`,
                    top: 0,
                    bottom: 0,
                    width: isSelected ? 6 : 3,
                    backgroundColor: isSelected ? theme.palette.success.main:theme.palette.secondary.main  ,
                    cursor: "pointer",
                    transform: "translateX(-50%)",
                    transition: "all 0.2s ease",
                    zIndex: isSelected ? 2 : 0,
                    "&:hover": {
                      width: 6,
                      backgroundColor: isSelected ? theme.palette.success.dark:theme.palette.primary.dark  ,
                      zIndex: 1,
                    },
                    "&::after": {
                      content: '""',
                      position: "absolute",
                      left: "50%",
                      top: "50%",
                      transform: "translate(-50%, -50%)",
                      width: isSelected ? 16 : 12,
                      height: isSelected ? 16 : 12,
                      borderRadius: "50%",
                      backgroundColor: isSelected ? theme.palette.success.main:theme.palette.primary.main ,
                      border: `2px solid ${theme.palette.background.paper}`,
                      transition: "all 0.2s ease",
                    },
                    "&:hover::after": {
                      width: 16,
                      height: 16,
                      backgroundColor: isSelected ? theme.palette.success.dark:theme.palette.primary.dark  ,
                    },
                  }}
                  title={date.toLocaleDateString()}
                />
              );
            })}
          </Box>
        </Box>
      )}
    </Box>
  );
};
