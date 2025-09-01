import React, { useContext } from "react";
import { type LastPlayerStats, type Team } from "../../client";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";
import { ErrorMessage } from "../common/ErrorMessage";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { EmptyState } from "../common/EmptyState";
import { Box, Typography } from "@mui/material";
import { PlayerStatsTable } from "../PlayerStatsTable";

interface TransferSuggestionProps {
  team: Team[];
}

export const TransferSuggestion: React.FC<TransferSuggestionProps> = ({ team }) => {
  const { playerStats, loading, error } = useContext(PlayerStatsContext)
  if (loading) {
    return <LoadingSpinner message="Loading player statistics..." />;
  }

  if (error) {
    return <ErrorMessage error={error} title="Error Loading Player Data" />;
  }
  if (!playerStats || playerStats.length === 0) {
    return <EmptyState title="No Player Data Available" message="No player statistics are currently available. Please check back later or contact support if this issue persists." />;
  }

  const myTeamId = team.map(t => t.player_id)

  const get_value_difference = (a: LastPlayerStats) => {
    if (!a.player_stats) {
      return 0;
    }
    return a.player_stats.estimated_value - a.player_stats.price
  }

  const myTeamStats = playerStats.filter(
    (player) => {
      return player.player_info.role != "GK" && myTeamId.includes(player.player_info.id)
    }

  ).sort((a, b) => get_value_difference(a) - get_value_difference(b))

  const otherPlayersStats = playerStats.filter(
    (player) => {
      return player.player_info.role != "GK" && !myTeamId.includes(player.player_info.id)
    }

  ).sort((a, b) => get_value_difference(b) - get_value_difference(a))

  return (
    <Box flex={1} sx={{ m: 2 }}>
      <Typography variant="h5">You should sell</Typography>
      <PlayerStatsTable data={myTeamStats} />
      <Typography variant="h5">You should buy</Typography>
      <PlayerStatsTable data={otherPlayersStats} />
    </Box>
  );
};