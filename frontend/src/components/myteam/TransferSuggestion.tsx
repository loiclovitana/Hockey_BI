import React, { useContext, useState } from "react";
import { type LastPlayerStats, type Team } from "../../client";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";
import { ErrorMessage } from "../common/ErrorMessage";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { EmptyState } from "../common/EmptyState";
import { SectionHeader } from "../common/SectionHeader";
import { Box } from "@mui/material";
import { PlayerStatsTable } from "../PlayerStatsTable";
import { DashboardPlayerFilters } from "./DashboardPlayerFilters";
import { DEFAULT_PLAYER_FILTERS, matchesPlayerFilters } from "./playerFilters";

interface TransferSuggestionProps {
  team: Team[];
}

export const TransferSuggestion: React.FC<TransferSuggestionProps> = ({
  team,
}) => {
  const { playerStats, loading, error } = useContext(PlayerStatsContext);
  const [filters, setFilters] = useState(DEFAULT_PLAYER_FILTERS);
  if (loading) {
    return <LoadingSpinner message="Loading player statistics..." />;
  }

  if (error) {
    return <ErrorMessage error={error} title="Error Loading Player Data" />;
  }
  if (!playerStats || playerStats.length === 0) {
    return (
      <EmptyState
        title="No Player Data Available"
        message="No player statistics are currently available. Please check back later or contact support if this issue persists."
      />
    );
  }
  const clubs = Array.from(
    new Set(
      playerStats
        .filter((player) => player.player_info.role !== "GK")
        .map((player) => player.player_stats?.club)
        .filter((club): club is string => Boolean(club)),
    ),
  ).sort();
  const filteredPlayerStats = playerStats.filter((player) =>
    matchesPlayerFilters(player, filters),
  );
  const filtersKey = JSON.stringify(filters);
  const myTeamId = team.filter((t) => !t.to_datetime).map((t) => t.player_id);

  const get_value_difference = (a: LastPlayerStats) => {
    if (!a.player_stats) {
      return 0;
    }
    if (a.player_stats.estimated_value === null) {
      return 0;
    }
    return a.player_stats.estimated_value - a.player_stats.price;
  };

  const myTeamStats = playerStats
    .filter((player) => {
      return (
        player.player_info.role != "GK" &&
        myTeamId.includes(player.player_info.id)
      );
    })
    .sort((a, b) => get_value_difference(a) - get_value_difference(b));

  const otherPlayersStats = filteredPlayerStats
    .filter((player) => {
      return (
        player.player_info.role != "GK" &&
        !myTeamId.includes(player.player_info.id)
      );
    })
    .sort((a, b) => get_value_difference(b) - get_value_difference(a));

  return (
    <Box flex={1} sx={{ py: 2 }}>
      <SectionHeader title="My team" />
      <PlayerStatsTable data={myTeamStats} />

      <Box sx={{ pt: 3 }}>
        <DashboardPlayerFilters
          filters={filters}
          clubs={clubs}
          onChange={setFilters}
          onReset={() => setFilters(DEFAULT_PLAYER_FILTERS)}
        />
        <SectionHeader title="Available" />
        <PlayerStatsTable key={filtersKey} data={otherPlayersStats} />
      </Box>
    </Box>
  );
};
