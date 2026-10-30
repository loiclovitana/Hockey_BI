import assert from "node:assert/strict";
import { test } from "node:test";
import {
  DEFAULT_PLAYER_FILTERS,
  matchesPlayerFilters,
} from "../src/components/myteam/playerFilters.ts";

const player = {
  player_info: { id: 1, role: "FW", foreigner: false },
  player_stats: { price: 2.5, club: "BER", appearances: 5 },
};

test("filters are unrestricted by default, including players without statistics", () => {
  assert.equal(matchesPlayerFilters(player, DEFAULT_PLAYER_FILTERS), true);
  assert.equal(
    matchesPlayerFilters(
      { ...player, player_stats: null },
      DEFAULT_PLAYER_FILTERS,
    ),
    true,
  );
});

test("Swiss only selects non-foreign players, including those without statistics", () => {
  const foreignPlayer = {
    ...player,
    player_info: { ...player.player_info, foreigner: true },
  };
  const filters = { ...DEFAULT_PLAYER_FILTERS, swissOnly: true };

  assert.equal(
    matchesPlayerFilters(foreignPlayer, DEFAULT_PLAYER_FILTERS),
    true,
  );
  assert.equal(matchesPlayerFilters(foreignPlayer, filters), false);
  assert.equal(matchesPlayerFilters(player, filters), true);
  assert.equal(
    matchesPlayerFilters({ ...player, player_stats: null }, filters),
    true,
  );
  assert.equal(
    matchesPlayerFilters({ ...foreignPlayer, player_stats: null }, filters),
    false,
  );
});

test("price change eligibility starts at exactly five appearances", () => {
  const filters = { ...DEFAULT_PLAYER_FILTERS, eligibleOnly: true };
  for (const [appearances, eligible] of [
    [4, false],
    [5, true],
    [6, true],
    [null, false],
    [undefined, false],
  ]) {
    assert.equal(
      matchesPlayerFilters(
        { ...player, player_stats: { ...player.player_stats, appearances } },
        filters,
      ),
      eligible,
    );
  }
  assert.equal(
    matchesPlayerFilters({ ...player, player_stats: null }, filters),
    false,
  );
});

test("price bounds are inclusive and support decimals and open ends", () => {
  for (const [minPrice, maxPrice, matches] of [
    ["2.5", "2.5", true],
    ["2.6", "", false],
    ["", "2.4", false],
    ["0", "", true],
    ["", "0", false],
    ["3", "2", false],
  ]) {
    assert.equal(
      matchesPlayerFilters(player, {
        ...DEFAULT_PLAYER_FILTERS,
        minPrice,
        maxPrice,
      }),
      matches,
    );
  }
});

test("role, price, team selections, eligibility and Swiss only combine", () => {
  const filters = {
    role: "FW",
    minPrice: "2",
    maxPrice: "3",
    clubs: ["BER", "ZSC"],
    eligibleOnly: true,
    swissOnly: true,
  };
  assert.equal(matchesPlayerFilters(player, filters), true);
  assert.equal(
    matchesPlayerFilters(
      { ...player, player_info: { ...player.player_info, foreigner: true } },
      filters,
    ),
    false,
  );
  assert.equal(
    matchesPlayerFilters(
      { ...player, player_info: { ...player.player_info, role: "DF" } },
      filters,
    ),
    false,
  );
  assert.equal(
    matchesPlayerFilters(
      { ...player, player_stats: { ...player.player_stats, club: "ZSC" } },
      filters,
    ),
    true,
  );
  assert.equal(
    matchesPlayerFilters(
      { ...player, player_stats: { ...player.player_stats, club: "GEN" } },
      filters,
    ),
    false,
  );
  assert.equal(
    matchesPlayerFilters(
      { ...player, player_stats: { ...player.player_stats, price: 4 } },
      filters,
    ),
    false,
  );
});

test("players with missing statistics cannot match active statistics filters", () => {
  for (const filter of [
    { minPrice: "1" },
    { maxPrice: "3" },
    { clubs: ["BER"] },
    { eligibleOnly: true },
  ]) {
    assert.equal(
      matchesPlayerFilters(
        { ...player, player_stats: null },
        { ...DEFAULT_PLAYER_FILTERS, ...filter },
      ),
      false,
    );
  }
});
