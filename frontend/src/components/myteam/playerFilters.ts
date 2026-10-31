import type { LastPlayerStats } from "../../client";

export interface PlayerFilters {
  role: "" | "FW" | "DF";
  minPrice: string;
  maxPrice: string;
  clubs: string[];
  eligibleOnly: boolean;
  swissOnly: boolean;
}

export const DEFAULT_PLAYER_FILTERS: PlayerFilters = {
  role: "",
  minPrice: "",
  maxPrice: "",
  clubs: [],
  eligibleOnly: false,
  swissOnly: false,
};

export const matchesPlayerFilters = (
  player: LastPlayerStats,
  filters: PlayerFilters,
): boolean => {
  const stats = player.player_stats;

  return (
    (filters.role === "" || player.player_info.role === filters.role) &&
    (filters.minPrice === "" ||
      (stats !== null && stats.price >= Number(filters.minPrice))) &&
    (filters.maxPrice === "" ||
      (stats !== null && stats.price <= Number(filters.maxPrice))) &&
    (filters.clubs.length === 0 ||
      (stats !== null && filters.clubs.includes(stats.club))) &&
    (!filters.eligibleOnly || (stats?.appearances ?? 0) >= 5) &&
    (!filters.swissOnly || player.player_info.foreigner === false)
  );
};
