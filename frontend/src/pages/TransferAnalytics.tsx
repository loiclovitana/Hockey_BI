import React, { useState, useEffect, useMemo } from "react";
import { Box, Typography, Button, ButtonGroup } from "@mui/material";
import { useDashboard } from "../hooks/useDashboard";
import { TeamLoginForm } from "../components/myteam/TeamLoginForm";
import { Transferts } from "../components/myteam/Transferts";
import {
  teamValueEvolutionMyteamTeamValueEvolutionPost,
  type TeamModification,
  type TeamValueEvolution
} from "../client";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ErrorMessage } from "../components/common/ErrorMessage";

export const TransferAnalytics: React.FC = () => {
  const { dashboardData, setDashboardData, credentials } = useDashboard();
  const [team, setTeam] = useState(0);
  const [teamValueEvolution, setTeamValueEvolution] = useState<TeamValueEvolution | null>(null);
  const [adaptedTeamEvolution, setAdaptedTeamEvolution] = useState<TeamValueEvolution | null>(null);
  const [teamModifications,setTeamModifications] = useState<TeamModification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTransfertDay, setSelectedTransfertDay] = useState<string | null>(null);

  const numberOfTeam = dashboardData?.my_teams.length ?? 0;

  /**
   * FETCH both team evolutions (with and without modifications)
   */
  useEffect(() => {
    const fetchTeamValueEvolutions = async () => {
      if (!credentials || !dashboardData || numberOfTeam === 0 || !dashboardData.my_teams[team]) {
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
        const baseResponse = await teamValueEvolutionMyteamTeamValueEvolutionPost({
          query: {
            team_code: teamCode,
          },
          body: {
            request: {
              hm_user: credentials.hm_user,
              hm_password: credentials.hm_password,
            }
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
          const modifiedResponse = await teamValueEvolutionMyteamTeamValueEvolutionPost({
            query: {
              team_code: teamCode,
            },
            body: {
              request: {
                hm_user: credentials.hm_user,
                hm_password: credentials.hm_password,
              },
              transfert_modification: {
                modifications: teamModifications
              }
            },
          });

          if (modifiedResponse.error) {
            console.error("Failed to load modified team evolution:", modifiedResponse.error);
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

  const transfertTimes = useMemo(()=>{
    if (!dashboardData) return new Set<string>();
    const datetimes = dashboardData.my_teams[team]?.flatMap(p=>[p.from_datetime,p.to_datetime]) ?? [];
    // Extract unique days (YYYY-MM-DD format)
    const days = datetimes
      .filter((dt): dt is string => dt !== undefined && dt !== null)
      .map(dt => new Date(dt).toISOString().split('T')[0]);
    return new Set(days);
  },[team,dashboardData])

  if (!dashboardData) {
    return <TeamLoginForm onSuccess={setDashboardData} />;
  }

  return (
    <Box sx={{ py: 3 }}>
      <Typography variant="h5" textAlign="center" gutterBottom>
        Transfer Analytics
      </Typography>

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

          {loading && <LoadingSpinner message="Loading team value evolution..." />}

          {error && <ErrorMessage error={error} title="Error Loading Team Data" />}

          {!loading && !error && teamValueEvolution && (
            <Box sx={{ px: 2 }}>
             <Transferts
               teamEvolution={teamValueEvolution}
               adaptedTeamEvolution={adaptedTeamEvolution}
               transfertTimes={transfertTimes}
               onTransfertDayClick={setSelectedTransfertDay}
             />
            </Box>
          )}
        </>
      )}
    </Box>
  );
};
