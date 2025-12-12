import React from "react";
import { Box, Typography, useTheme, useMediaQuery, Chip } from "@mui/material";
import { LineChart, lineElementClasses } from "@mui/x-charts/LineChart";
import { ChartsReferenceLine } from "@mui/x-charts/ChartsReferenceLine";
import { type TeamValueEvolution } from "../../client";

interface CustomLegendProps {
  series: Array<{
    label: string;
    color: string;
    isDashed?: boolean;
  }>;
}

const CustomLegend: React.FC<CustomLegendProps> = ({ series }) => {
  return (
    <Box
      sx={{
        display: "flex",
        flexWrap: "wrap",
        gap: 2,
        justifyContent: "center",
        px: 2,
        pb: 2,
      }}
    >
      {series.map((item, index) => (
        <Box
          key={index}
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          <svg width="32" height="3" style={{ overflow: "visible" }}>
            <line
              x1="0"
              y1="1.5"
              x2="32"
              y2="1.5"
              stroke={item.color}
              strokeWidth="2"
              strokeDasharray={item.isDashed ? "5 3" : "none"}
            />
          </svg>
          <Typography variant="body2" sx={{ fontSize: "0.875rem" }}>
            {item.label}
          </Typography>
        </Box>
      ))}
    </Box>
  );
};

interface TeamValueChartProps {
  teamEvolution: TeamValueEvolution | null;
  adaptedTeamEvolution: TeamValueEvolution | null;
  transfertTimes?: Set<string>;
  onTransfertDayClick?: (day: string) => void;
  selectedTransfertDate?: string | null;
}

interface TransferTimelineProps {
  transferDates: Date[];
  dates: Date[];
  selectedTransfertDate?: string | null;
  onTransfertDayClick?: (day: string) => void;
}

const TransferTimeline: React.FC<TransferTimelineProps> = ({
  transferDates,
  dates,
  selectedTransfertDate,
  onTransfertDayClick,
}) => {
  const theme = useTheme();

  // Calculate position of each transfer date on the timeline
  const getTransferPosition = (transferDate: Date) => {
    if (dates.length === 0) return 0;
    const minTime = dates[0].getTime();
    const maxTime = dates[dates.length - 1].getTime();
    const transferTime = transferDate.getTime();
    return ((transferTime - minTime) / (maxTime - minTime)) * 100;
  };

  return (
    <Box sx={{ px: 2, pl: 8 }}>
      {transferDates.length > 0 && (
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
            const dateStr = date.toISOString().split("T")[0];
            const isSelected = selectedTransfertDate === dateStr;
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
                  backgroundColor: isSelected
                    ? theme.palette.success.main
                    : theme.palette.secondary.main,
                  cursor: "pointer",
                  transform: "translateX(-50%)",
                  transition: "all 0.2s ease",
                  zIndex: isSelected ? 2 : 0,
                  "&:hover": {
                    width: 6,
                    backgroundColor: isSelected
                      ? theme.palette.success.dark
                      : theme.palette.secondary.dark,
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
                    backgroundColor: isSelected
                      ? theme.palette.success.main
                      : theme.palette.secondary.main,
                    border: `2px solid ${theme.palette.background.paper}`,
                    transition: "all 0.2s ease",
                  },
                  "&:hover::after": {
                    width: 16,
                    height: 16,
                    backgroundColor: isSelected
                      ? theme.palette.success.dark
                      : theme.palette.secondary.dark,
                  },
                }}
                title={date.toLocaleDateString()}
              />
            );
          })}
        </Box>
      )}
      {/* Special filter chips */}
      <Box sx={{ display: "flex", gap: 1, pt: 1 }}>
        <Chip
          label="Start"
          onClick={() => onTransfertDayClick?.("start")}
          color={selectedTransfertDate === "start" ? "success" : "default"}
          variant={selectedTransfertDate === "start" ? "filled" : "outlined"}
          sx={{ cursor: "pointer" }}
        />
        <Chip
          label="Current"
          onClick={() => onTransfertDayClick?.("current")}
          color={selectedTransfertDate === "current" ? "success" : "default"}
          variant={selectedTransfertDate === "current" ? "filled" : "outlined"}
          sx={{ cursor: "pointer", marginLeft: "auto" }}
        />
      </Box>
    </Box>
  );
};

export const TeamValueChart: React.FC<TeamValueChartProps> = ({
  teamEvolution,
  adaptedTeamEvolution,
  transfertTimes,
  onTransfertDayClick,
  selectedTransfertDate,
}) => {
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
        (a, b) => new Date(a.at).getTime() - new Date(b.at).getTime(),
      )
    : [];

  const sortedAdaptedEvolution = adaptedTeamEvolution?.evolution
    ? [...adaptedTeamEvolution.evolution].sort(
        (a, b) => new Date(a.at).getTime() - new Date(b.at).getTime(),
      )
    : [];

  // Use the longer dataset for x-axis
  const dates =
    sortedTeamEvolution.length >= sortedAdaptedEvolution.length
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
  const legendData: Array<{
    label: string;
    color: string;
    isDashed?: boolean;
  }> = [];

  if (teamEvolution?.evolution && sortedTeamEvolution.length > 0) {
    series.push({
      data: sortedTeamEvolution.map((d) => d.value),
      label: "Actual",
      showMark: false,
      color: theme.palette.primary.main,
      id: "v1",
    });
    legendData.push({
      label: "Actual",
      color: theme.palette.primary.main,
      isDashed: false,
    });

    series.push({
      data: sortedTeamEvolution.map((d) => d.theorical_value),
      label: "Actual (Target)",
      showMark: false,
      color: theme.palette.primary.main,
      id: "vt1",
    });
    legendData.push({
      label: "Actual (Target)",
      color: theme.palette.primary.main,
      isDashed: true,
    });
  }

  if (adaptedTeamEvolution?.evolution && sortedAdaptedEvolution.length > 0) {
    series.push({
      data: sortedAdaptedEvolution.map((d) => d.value),
      label: "Alternative",
      showMark: false,
      color: "#ff9800",
      id: "v2",
    });
    legendData.push({
      label: "Alternative",
      color: "#ff9800",
      isDashed: false,
    });

    series.push({
      data: sortedAdaptedEvolution.map((d) => d.theorical_value),
      label: "Alternative (Target)",
      showMark: false,
      color: "#ff9800",
      strokeDasharray: "5 5",
      id: "vt2",
    });
    legendData.push({
      label: "Alternative (Target)",
      color: "#ff9800",
      isDashed: true,
    });
  }

  // Convert transfer times to Date objects for reference lines
  const transferDates = transfertTimes
    ? Array.from(transfertTimes).map((dateStr) => new Date(dateStr))
    : [];

  return (
    <Box sx={{ pt: 3, width: "100%", overflow: "hidden" }}>
      {/* Custom Legend */}
      <CustomLegend series={legendData} />
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
              min: dates[0],
              max: dates[dates.length - 1],
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
          hideLegend={true}
          sx={{
            [`.${lineElementClasses.root}[data-series="vt1"]`]: {
              strokeDasharray: "5 5",
            },
            [`.${lineElementClasses.root}[data-series="vt2"]`]: {
              strokeDasharray: "5 5",
            },
            "& .MuiChartsReferenceLine-root": {
              stroke: theme.palette.error.main,
              strokeWidth: 2,
              strokeDasharray: "3 3",
              cursor: "pointer",
              "&:hover": {
                strokeWidth: 3,
              },
            },
          }}
        >
          {transferDates.map((date) => (
            <ChartsReferenceLine
              key={`transfer-${date.toISOString()}`}
              x={date}
              label=""
              lineStyle={{
                stroke:
                  date.toISOString().split("T")[0] === selectedTransfertDate
                    ? theme.palette.success.main
                    : theme.palette.secondary.main,
                strokeDasharray: "3 3",
              }}
            />
          ))}
        </LineChart>
      </Box>

      {/* Clickable Timeline for Transfer Days */}
      <TransferTimeline
        transferDates={transferDates}
        dates={dates}
        selectedTransfertDate={selectedTransfertDate}
        onTransfertDayClick={onTransfertDayClick}
      />
    </Box>
  );
};
