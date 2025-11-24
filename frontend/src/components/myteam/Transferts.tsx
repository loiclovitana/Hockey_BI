import React, { useContext } from "react";
import { Box } from "@mui/material";
import { PlayerStatsTable } from "../PlayerStatsTable";
import { type LastPlayerStats, type Team } from "../../client/";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { ErrorMessage } from "../common/ErrorMessage";
import { EmptyState } from "../common/EmptyState";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";

interface TransfertsProps {
  team:  Team[];
}

export const Transferts: React.FC<TransfertsProps> = ({ team }) => {

  const { playerStats, loading, error } = useContext(PlayerStatsContext);
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
  const transferts = team.filter(p => p.from_datetime || p.to_datetime).map((t) => t.player_id);
  const transferedPlayer = playerStats.filter(p =>transferts.includes(p.player_info.id));


  return (
    <Box sx={{ px: 2 }}>
      <PlayerStatsTable data={transferedPlayer} />
    </Box>
  );
};
