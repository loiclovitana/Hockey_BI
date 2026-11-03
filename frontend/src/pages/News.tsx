import React, { useContext, useMemo, useState } from "react";
import {
  Box,
  Button,
  ButtonGroup,
  Chip,
  Drawer,
  IconButton,
  Link,
  Typography,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import SearchIcon from "@mui/icons-material/Search";
import type { LastPlayerStats } from "../client";
import { PlayerNewsFeed } from "../components/news/PlayerNewsFeed";
import { HockeyPlayerSearch } from "../components/player/HockeyPlayerSearch";
import { PlayerStatsContext } from "../context/PlayerStatsContext";
import { useDashboard } from "../hooks/useDashboard";
import type { PlayerNewsFilters } from "../hooks/usePlayerNews";

export const News: React.FC = () => {
  const { dashboardData } = useDashboard();
  const { playerStats } = useContext(PlayerStatsContext);
  const [selectedTeam, setSelectedTeam] = useState<number | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<LastPlayerStats | null>(
    null,
  );
  const [searchOpen, setSearchOpen] = useState(false);
  const team =
    selectedTeam === null ? undefined : dashboardData?.my_teams[selectedTeam];

  const filters = useMemo<PlayerNewsFilters>(() => {
    if (selectedPlayer) {
      return {
        season_id: selectedPlayer.player_info.season_id,
        player_ids: [selectedPlayer.player_info.id],
      };
    }
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
  }, [team, playerStats, selectedPlayer]);

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
            variant={!team && !selectedPlayer ? "contained" : "outlined"}
            aria-pressed={!team && !selectedPlayer}
            onClick={() => {
              setSelectedTeam(null);
              setSelectedPlayer(null);
            }}
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
              onClick={() => {
                setSelectedTeam(index);
                setSelectedPlayer(null);
              }}
              sx={{ minHeight: 44 }}
            >
              Team {index + 1}
            </Button>
          ))}
        </ButtonGroup>
      )}

      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
        <Button
          variant="outlined"
          startIcon={<SearchIcon />}
          disabled={!playerStats?.length}
          onClick={() => setSearchOpen(true)}
          sx={{ minHeight: 44 }}
        >
          Search players
        </Button>
        {selectedPlayer && (
          <Chip
            label={selectedPlayer.player_info.name}
            onDelete={() => setSelectedPlayer(null)}
            sx={{ alignSelf: "center" }}
          />
        )}
      </Box>

      <PlayerNewsFeed key={JSON.stringify(filters)} filters={filters} />

      <Drawer
        variant="temporary"
        anchor="bottom"
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        sx={{
          "& .MuiDrawer-paper": {
            width: "100%",
            height: "80vh",
            boxSizing: "border-box",
            borderTopLeftRadius: 16,
            borderTopRightRadius: 16,
          },
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            p: 2,
            borderBottom: 1,
            borderColor: "divider",
          }}
        >
          <Typography variant="h6">Select Player</Typography>
          <IconButton
            aria-label="Close player search"
            onClick={() => setSearchOpen(false)}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        <Box sx={{ flex: 1, overflow: "hidden" }}>
          <HockeyPlayerSearch
            players={playerStats ?? []}
            selectedPlayer={selectedPlayer}
            setSelectedHockeyPlayer={(player) => {
              setSelectedPlayer(player);
              setSelectedTeam(null);
              setSearchOpen(false);
            }}
          />
        </Box>
      </Drawer>
    </Box>
  );
};
