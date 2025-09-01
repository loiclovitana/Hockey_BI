import { createContext } from 'react';
import type { LastPlayerStats } from '../client/';

export interface PlayerStatsContextType {
  playerStats: LastPlayerStats[] | null;
  loading: boolean;
  error: unknown | null;
  refetch: () => Promise<void>;
}

export const PlayerStatsContext = createContext<PlayerStatsContextType>({ playerStats: null, loading: false, error: null, refetch: async () => { } });