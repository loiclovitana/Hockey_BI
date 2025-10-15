import React, { useContext } from "react";
import { Box, Typography, Paper } from "@mui/material";
import { type Team } from "../../client";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";
import { ValueWithDifference } from "../common/ValueWithDifference";

interface TeamValueProps {
  team: Team[];
}

const INITIAL_VALUE = 150.0;

export const TeamValue: React.FC<TeamValueProps> = ({ team }) => {
  // For now, set both values to 0
  const { playerStats } = useContext(PlayerStatsContext);
  const myTeamId = team.filter((t) => !t.to_datetime).map((t) => t.player_id);

  if (!playerStats) {
    return <></>;
  }

  const myTeamStats = playerStats.filter((player) => {
    return myTeamId.includes(player.player_info.id);
  });

  const totalValue = myTeamStats
    .map((p) => p.player_stats?.price)
    .reduce((acc: number, price) => acc + (price ?? 0), 0);
  const estimatedValue = myTeamStats
    .map((p) => {
      if (p.player_info.role == "GK") {
        return p.player_stats?.price;
      }
      return p.player_stats?.estimated_value ?? p.player_stats?.price;
    })
    .reduce((acc: number, value) => acc + (value ?? 0), 0);
  return (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        display: "flex",
        justifyContent: "space-around",
        alignItems: "center",
      }}
    >
      <Box sx={{ textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Value
        </Typography>
        <Typography variant="h6" fontWeight="bold">
          <ValueWithDifference value={totalValue} baseValue={INITIAL_VALUE} />
        </Typography>
      </Box>
      <Box sx={{ textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Estimated Value
        </Typography>
        <Typography variant="h6" fontWeight="bold">
          <ValueWithDifference value={estimatedValue} baseValue={totalValue} />
        </Typography>
      </Box>
    </Paper>
  );
};
