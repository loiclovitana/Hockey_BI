import { useEffect, useState } from "react";
import {
  getPlayerNewsPlayersNewsGet,
  type GetPlayerNewsPlayersNewsGetData,
  type PlayerNews,
} from "../client";

export type PlayerNewsFilters = Pick<
  NonNullable<GetPlayerNewsPlayersNewsGetData["query"]>,
  "player_ids" | "season_id"
>;

const PAGE_SIZE = 25;

// The feed remounts when filters change so pages from different teams never mix.
export const usePlayerNews = (filters: PlayerNewsFilters) => {
  const [news, setNews] = useState<PlayerNews[]>([]);
  const [offset, setOffset] = useState(0);
  const [attempt, setAttempt] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    // An empty array is omitted by the query serializer and would return all news.
    if (filters.player_ids?.length === 0) {
      setLoading(false);
      return;
    }

    const controller = new AbortController();

    const fetchNews = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data } = await getPlayerNewsPlayersNewsGet({
          query: { ...filters, limit: PAGE_SIZE, offset },
          signal: controller.signal,
          throwOnError: true,
        });
        if (controller.signal.aborted) return;

        setNews((previous) => {
          const existingIds = new Set(previous.map((item) => item.id));
          return [
            ...previous,
            ...data.filter((item) => !existingIds.has(item.id)),
          ];
        });
        setHasMore(data.length === PAGE_SIZE);
      } catch {
        if (!controller.signal.aborted) {
          setError(new Error("Unable to load player news. Please try again."));
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    };

    void fetchNews();
    return () => controller.abort();
  }, [filters, offset, attempt]);

  return {
    news,
    loading,
    error,
    hasMore,
    loadMore: () => {
      setLoading(true);
      setOffset((previous) => previous + PAGE_SIZE);
    },
    retry: () => {
      setLoading(true);
      setAttempt((previous) => previous + 1);
    },
  };
};
