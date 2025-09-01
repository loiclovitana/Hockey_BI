import React, { useEffect, useState, type ReactNode } from 'react';
import { getLatestPlayerStatsPlayersLatestGet, type LastPlayerStats } from '../client/';
import { PlayerStatsContext, type PlayerStatsContextType } from './PlayerStatsContext';

interface PlayerStatsProviderProps {
  children: ReactNode;
}

export const PlayerStatsProvider: React.FC<PlayerStatsProviderProps> = ({ children }) => {
  const [playerStats, setPlayerStats] = useState<LastPlayerStats[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<unknown | null>(null);

  const fetchPlayerStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getLatestPlayerStatsPlayersLatestGet();
      if (response.data) {
        setPlayerStats(response.data);
      }
      if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch player stats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlayerStats();
  }, []);

  const value : PlayerStatsContextType = {
    playerStats,
    loading,
    error,
    refetch: fetchPlayerStats,
  };

  return (
    <PlayerStatsContext.Provider value={value}>
      {children}
    </PlayerStatsContext.Provider>
  );
};