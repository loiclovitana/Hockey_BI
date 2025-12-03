import React, { useState, useEffect, useMemo, useContext } from "react";
import {
  Box,
  Typography,
  Button,
  ButtonGroup,
  Drawer,
  IconButton,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useDashboard } from "../hooks/useDashboard";
import { TeamLoginForm } from "../components/myteam/TeamLoginForm";
import { TeamValueChart } from "../components/myteam/TeamValueChart";
import { TransferListTable } from "../components/myteam/TransferListTable";
import { HockeyPlayerSearch } from "../components/player/HockeyPlayerSearch";
import { AdaptationsList } from "../components/myteam/AdaptationsList";
import { PlayerStatsContext } from "../context/PlayerStatsContext";
import {
  teamValueEvolutionMyteamTeamValueEvolutionPost,
  type TeamModification,
  type TeamValueEvolution,
} from "../client";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ErrorMessage } from "../components/common/ErrorMessage";

export const TransferAnalytics: React.FC = () => {
  const { dashboardData, setDashboardData, credentials } = useDashboard();
  const { playerStats } = useContext(PlayerStatsContext);
  const [team, setTeam] = useState(0);
  const [teamValueEvolution, setTeamValueEvolution] =
    useState<TeamValueEvolution | null>(null);
  const [adaptedTeamEvolution, setAdaptedTeamEvolution] =
    useState<TeamValueEvolution | null>(null);
  const [teamModifications, setTeamModifications] = useState<
    TeamModification[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTransfertDay, setSelectedTransfertDay] = useState<
    string | null
  >(null);
  const [selectedTransfertId, setSelectedTransfertId] = useState<number | null>(
    null,
  );

  const numberOfTeam = dashboardData?.my_teams.length ?? 0;

  /**
   * Handle player selection from search
   */
  const handlePlayerSelect = (playerId: number) => {
    if (selectedTransfertId === null) return;

    const newModification: TeamModification = {
      team_id: selectedTransfertId,
      replaced_player_id: playerId,
    };

    setTeamModifications((prev) => [...prev, newModification]);
    setSelectedTransfertId(null);
  };

  /**
   * Handle removing a modification
   */
  const handleRemoveModification = (index: number) => {
    setTeamModifications((prev) => prev.filter((_, i) => i !== index));
  };

  /**
   * FETCH both team evolutions (with and without modifications)
   */
  useEffect(() => {
    const fetchTeamValueEvolutions = async () => {
      if (
        !credentials ||
        !dashboardData ||
        numberOfTeam === 0 ||
        !dashboardData.my_teams[team]
      ) {
        return;
      }

      const teamCode = dashboardData.my_teams[team][0]?.team;
      if (!teamCode) {
        return;
      }

      setLoading(true);
      setError(null);

      try {
        // Fetch base evolution (without modifications)
        const baseResponse =
          await teamValueEvolutionMyteamTeamValueEvolutionPost({
            query: {
              team_code: teamCode,
            },
            body: {
              request: {
                hm_user: credentials.hm_user,
                hm_password: credentials.hm_password,
              },
            },
          });

        if (baseResponse.error) {
          setError("Failed to load team value evolution");
          console.error(baseResponse.error);
          return;
        }

        setTeamValueEvolution(baseResponse.data || null);

        // Fetch evolution with modifications (if any)
        if (teamModifications && teamModifications.length > 0) {
          const modifiedResponse =
            await teamValueEvolutionMyteamTeamValueEvolutionPost({
              query: {
                team_code: teamCode,
              },
              body: {
                request: {
                  hm_user: credentials.hm_user,
                  hm_password: credentials.hm_password,
                },
                transfert_modification: {
                  modifications: teamModifications,
                },
              },
            });

          if (modifiedResponse.error) {
            console.error(
              "Failed to load modified team evolution:",
              modifiedResponse.error,
            );
          } else {
            setAdaptedTeamEvolution(modifiedResponse.data || null);
          }
        } else {
          setAdaptedTeamEvolution(null);
        }
      } catch (err) {
        setError("An unexpected error occurred");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamValueEvolutions();
  }, [team, dashboardData, credentials, numberOfTeam, teamModifications]);

  const transfertTimes = useMemo(() => {
    if (!dashboardData) return new Set<string>();
    const datetimes =
      dashboardData.my_teams[team]?.flatMap((p) => [
        p.from_datetime,
        p.to_datetime,
      ]) ?? [];
    // Extract unique days (YYYY-MM-DD format)
    const days = datetimes
      .filter((dt): dt is string => dt !== undefined && dt !== null)
      .map((dt) => new Date(dt).toISOString().split("T")[0]);
    return new Set(days);
  }, [team, dashboardData]);

  const selectedTransfer = useMemo(() => {
    if (!selectedTransfertId || !dashboardData) return null;
    return dashboardData.my_teams[team]?.find(
      (t) => t.id === selectedTransfertId,
    );
  }, [selectedTransfertId, dashboardData, team]);

  const selectedTransferPlayerRole = useMemo(() => {
    if (!selectedTransfer || !playerStats) return null;
    const playerStat = playerStats.find(
      (p) => p.player_info.id === selectedTransfer.player_id,
    );
    return playerStat?.player_info.role || null;
  }, [selectedTransfer, playerStats]);

  if (!dashboardData) {
    return <TeamLoginForm onSuccess={setDashboardData} />;
  }

  return (
    <Box sx={{ py: 3 }}>
      {numberOfTeam === 0 ? (
        <Typography variant="body2" textAlign="center">
          You haven't created any team yet
        </Typography>
      ) : (
        <>
          <Box sx={{ display: "flex", justifyContent: "center", pb: 2 }}>
            <ButtonGroup variant="contained" sx={{ minWidth: "300px" }}>
              <Button
                variant={team === 0 ? "contained" : "outlined"}
                onClick={() => setTeam(0)}
                sx={{ flex: 1 }}
              >
                Team 1
              </Button>
              <Button
                variant={team === 1 ? "contained" : "outlined"}
                onClick={() => setTeam(1)}
                disabled={numberOfTeam < 2}
                sx={{ flex: 1 }}
              >
                Team 2
              </Button>
            </ButtonGroup>
          </Box>

          {loading && (
            <LoadingSpinner message="Loading team value evolution..." />
          )}

          {error && (
            <ErrorMessage error={error} title="Error Loading Team Data" />
          )}

          {!loading && !error && teamValueEvolution && (
            <Box sx={{ px: 2 }}>
              {playerStats && (
                <AdaptationsList
                  modifications={teamModifications}
                  transfers={dashboardData.my_teams[team] || []}
                  playerStats={playerStats}
                  onRemoveModification={handleRemoveModification}
                />
              )}
              <TeamValueChart
                teamEvolution={teamValueEvolution}
                adaptedTeamEvolution={adaptedTeamEvolution}
                transfertTimes={transfertTimes}
                onTransfertDayClick={setSelectedTransfertDay}
                selectedTransfertDate={selectedTransfertDay}
              />
              <TransferListTable
                transfers={dashboardData.my_teams[team] || []}
                selectedDate={selectedTransfertDay}
                selectedPlayerId={selectedTransfertId}
                onPlayerSelect={setSelectedTransfertId}
              />
            </Box>
          )}
        </>
      )}

      <Drawer
        variant="temporary"
        anchor="bottom"
        open={selectedTransfertId !== null}
        onClose={() => setSelectedTransfertId(null)}
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
          <Typography variant="h6">Select Replacement Player</Typography>
          <IconButton onClick={() => setSelectedTransfertId(null)}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Box sx={{ flex: 1, overflow: "hidden" }}>
          {playerStats && (
            <HockeyPlayerSearch
              players={playerStats.filter(
                (p) =>
                  p.player_info.role === selectedTransferPlayerRole &&
                  p.player_info.id !== selectedTransfer?.player_id,
              )}
              setSelectedHockeyPlayer={(player) => {
                if (player) {
                  handlePlayerSelect(player.player_info.id);
                }
              }}
              selectedPlayer={null}
            />
          )}
        </Box>
      </Drawer>
    </Box>
  );
};
