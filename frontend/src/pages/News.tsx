import React, { useContext, useMemo, useState } from "react";
import { Box, Button, ButtonGroup, Link, Typography } from "@mui/material";
import { PlayerNewsFeed } from "../components/news/PlayerNewsFeed";
import { PlayerStatsContext } from "../context/PlayerStatsContext";
import { useDashboard } from "../hooks/useDashboard";
import type { PlayerNewsFilters } from "../hooks/usePlayerNews";

export const News: React.FC = () => {
  const { dashboardData } = useDashboard();
  const { playerStats } = useContext(PlayerStatsContext);
  const [selectedTeam, setSelectedTeam] = useState<number | null>(null);
  const team =
    selectedTeam === null ? undefined : dashboardData?.my_teams[selectedTeam];

  const filters = useMemo<PlayerNewsFilters>(() => {
    if (!team) return {};

    // Both the player stats and dashboard endpoints return the current season.
    const seasonId =
      playerStats?.[0]?.player_info.season_id ?? team[0]?.season_id;
    const now = Date.now();
    return {
      season_id: seasonId,
      player_ids: [
        ...new Set(
          team
            .filter(
              (player) =>
                player.season_id === seasonId &&
                (!player.from_datetime ||
                  new Date(player.from_datetime).getTime() <= now) &&
                (!player.to_datetime ||
                  new Date(player.to_datetime).getTime() > now),
            )
            .map((player) => player.player_id),
        ),
      ],
    };
  }, [team, playerStats]);

  return (
    <Box sx={{ p: { xs: 1, sm: 3 }, maxWidth: 800, mx: "auto" }}>
      <Typography component="h1" variant="h5">
        Player News
      </Typography>
      <Typography
        variant="caption"
        color="text.secondary"
        component="p"
        sx={{ mb: 2 }}
      >
        Source:{" "}
        <Link
          href="https://www.swisshockeynews.ch/"
          target="_blank"
          rel="noopener noreferrer"
          color="inherit"
        >
          SwissHockeyNews
        </Link>
      </Typography>

      {dashboardData && (
        <ButtonGroup fullWidth aria-label="Filter news by team" sx={{ mb: 2 }}>
          <Button
            variant={!team ? "contained" : "outlined"}
            aria-pressed={!team}
            onClick={() => setSelectedTeam(null)}
            sx={{ minHeight: 44 }}
          >
            ALL
          </Button>
          {[0, 1].map((index) => (
            <Button
              key={index}
              variant={
                team && selectedTeam === index ? "contained" : "outlined"
              }
              aria-pressed={!!team && selectedTeam === index}
              disabled={!dashboardData.my_teams[index]}
              onClick={() => setSelectedTeam(index)}
              sx={{ minHeight: 44 }}
            >
              Team {index + 1}
            </Button>
          ))}
        </ButtonGroup>
      )}

      <PlayerNewsFeed key={JSON.stringify(filters)} filters={filters} />
    </Box>
  );
};
