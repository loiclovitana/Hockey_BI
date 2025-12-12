import React, { useState, useEffect, useMemo, useContext } from "react";
import { Box, Drawer, IconButton, Typography } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { TeamValueChart } from "./TeamValueChart";
import { TransferListTable } from "./TransferListTable";
import { HockeyPlayerSearch } from "../player/HockeyPlayerSearch";
import { AdaptationsList } from "./AdaptationsList";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";
import {
  teamValueEvolutionMyteamTeamValueEvolutionPost,
  type TeamModification,
  type TeamValueEvolution,
  type DashBoardData,
} from "../../client";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { ErrorMessage } from "../common/ErrorMessage";
import type { Credentials } from "../../context/DashboardContext";

interface TeamAnalyticsViewProps {
  team: number;
  dashboardData: DashBoardData;
  credentials: Credentials;
}

export const TeamAnalyticsView: React.FC<TeamAnalyticsViewProps> = ({
  team,
  dashboardData,
  credentials,
}) => {
  const { playerStats } = useContext(PlayerStatsContext);
  const [teamValueEvolution, setTeamValueEvolution] =
    useState<TeamValueEvolution | null>(null);
  const [adaptedTeamEvolution, setAdaptedTeamEvolution] =
    useState<TeamValueEvolution | null>(null);
  const [teamModifications, setTeamModifications] = useState<
    TeamModification[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [adaptedLoading, setAdaptedLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTransfertDay, setSelectedTransfertDay] = useState<
    string | null
  >(null);
  const [selectedTransfertId, setSelectedTransfertId] = useState<number | null>(
    null,
  );

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
   * FETCH base team evolution (without modifications)
   */
  useEffect(() => {
    const fetchBaseTeamValue = async () => {
      if (!dashboardData.my_teams[team]) {
        return;
      }

      const teamCode = dashboardData.my_teams[team][0]?.team;
      if (!teamCode) {
        return;
      }

      setLoading(true);
      setError(null);

      try {
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
      } catch (err) {
        setError("An unexpected error occurred");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchBaseTeamValue();
  }, [team, dashboardData, credentials]);

  /**
   * FETCH adapted team evolution (with modifications)
   */
  useEffect(() => {
    const fetchAdaptedTeamValue = async () => {
      if (!dashboardData.my_teams[team]) {
        return;
      }

      const teamCode = dashboardData.my_teams[team][0]?.team;
      if (!teamCode) {
        return;
      }

      // Only fetch if there are modifications
      if (!teamModifications || teamModifications.length === 0) {
        setAdaptedTeamEvolution(null);
        return;
      }

      setAdaptedLoading(true);

      try {
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
      } catch (err) {
        console.error("Error fetching adapted team evolution:", err);
      } finally {
        setAdaptedLoading(false);
      }
    };

    fetchAdaptedTeamValue();
  }, [team, dashboardData, credentials, teamModifications]);

  const transfertTimes = useMemo(() => {
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
    if (!selectedTransfertId) return null;
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

  return (
    <>
      {loading && <LoadingSpinner message="Loading team value evolution..." />}

      {error && <ErrorMessage error={error} title="Error Loading Team Data" />}

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
            adaptedLoading={adaptedLoading}
          />
          <TransferListTable
            transfers={dashboardData.my_teams[team] || []}
            selectedDate={selectedTransfertDay}
            selectedPlayerId={selectedTransfertId}
            onPlayerSelect={setSelectedTransfertId}
          />
        </Box>
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
    </>
  );
};
