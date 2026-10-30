import React, { useContext, useMemo } from "react";
import { Box, Button, Stack } from "@mui/material";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";
import {
  usePlayerNews,
  type PlayerNewsFilters,
} from "../../hooks/usePlayerNews";
import { EmptyState } from "../common/EmptyState";
import { ErrorMessage } from "../common/ErrorMessage";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { PlayerNewsCard } from "./PlayerNewsCard";

interface PlayerNewsFeedProps {
  filters: PlayerNewsFilters;
}

export const PlayerNewsFeed: React.FC<PlayerNewsFeedProps> = ({ filters }) => {
  const { playerStats } = useContext(PlayerStatsContext);
  const { news, loading, error, hasMore, loadMore, retry } =
    usePlayerNews(filters);
  const players = useMemo(
    () =>
      new Map(playerStats?.map((player) => [player.player_info.id, player])),
    [playerStats],
  );

  return (
    <Stack spacing={1} aria-busy={loading}>
      {news.map((item) => (
        <PlayerNewsCard
          key={item.id}
          news={item}
          player={
            item.player_id === null ? undefined : players.get(item.player_id)
          }
        />
      ))}

      {error ? (
        <Box sx={{ textAlign: "center" }}>
          <ErrorMessage error={error} title="Error Loading News" />
          <Button variant="outlined" onClick={retry}>
            Try again
          </Button>
        </Box>
      ) : loading ? (
        <Box sx={{ py: 3 }}>
          <LoadingSpinner message="Loading player news..." />
        </Box>
      ) : news.length === 0 ? (
        <EmptyState
          title="No News Available"
          message={
            filters.player_ids
              ? "No news for this team's players in the current season."
              : "No player news is currently available. Please check back later."
          }
        />
      ) : (
        hasMore && (
          <Button variant="outlined" onClick={loadMore} sx={{ minHeight: 44 }}>
            Load more
          </Button>
        )
      )}
    </Stack>
  );
};
