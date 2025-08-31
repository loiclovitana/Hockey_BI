import React, { useContext } from "react";
import { type Team } from "../../client";
import { PlayerStatsContext } from "../../context/PlayerStatsContext";
import { ErrorMessage } from "../common/ErrorMessage";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { EmptyState } from "../common/EmptyState";

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

  return (
    <div>
      {/* Component content will be added here */}
    </div>
  );
};