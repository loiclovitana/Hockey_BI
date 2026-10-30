import React from "react";
import {
  Box,
  Chip,
  IconButton,
  Paper,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import ArrowRightAltRoundedIcon from "@mui/icons-material/ArrowRightAltRounded";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import type { LastPlayerStats, PlayerNews } from "../../client";

interface PlayerNewsCardProps {
  news: PlayerNews;
  player?: LastPlayerStats;
}

const CLUB_CODES = new Set([
  "AJO",
  "AMB",
  "BER",
  "BIE",
  "DAV",
  "FRI",
  "GEN",
  "KLO",
  "LAN",
  "LAU",
  "LUG",
  "RAP",
  "ZSC",
  "ZUG",
]);

const getClubCode = (team: string | null | undefined) => {
  const code = team?.trim().toUpperCase();
  return code && CLUB_CODES.has(code) ? code : null;
};

const TeamIdentity: React.FC<{ team: string | null }> = ({ team }) => {
  const code = getClubCode(team);

  return code ? (
    <Tooltip title={code}>
      <Box
        component="img"
        src={`/club/${code}.webp`}
        alt={code}
        sx={{ width: 28, height: 28, objectFit: "contain", flexShrink: 0 }}
      />
    </Tooltip>
  ) : (
    <Typography variant="body2" sx={{ overflowWrap: "anywhere", minWidth: 0 }}>
      {team ?? "Unknown team"}
    </Typography>
  );
};

export const PlayerNewsCard: React.FC<PlayerNewsCardProps> = ({
  news,
  player,
}) => {
  const name = player?.player_info.name ?? news.player_name;
  const team = player?.player_stats?.club ?? news.current_team;
  const club = getClubCode(team);
  const isTransfer = news.info_type === "Transfert";
  const availabilityLabel =
    news.info_type === "Injury" ? "Injury duration" : "Availability";
  const articleUrl = new URL(news.article.article_url, news.article.base_url);
  const date = new Date(`${news.article.article_date}T00:00:00`);

  return (
    <Paper component="article" variant="outlined" sx={{ p: 1.5 }}>
      <Stack spacing={0.5}>
        <Stack direction="row" spacing={1} alignItems="center">
          {club && <TeamIdentity team={club} />}
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <Typography
              component="h2"
              variant="subtitle2"
              sx={{ overflowWrap: "anywhere" }}
            >
              {name}
            </Typography>
            {!club && !isTransfer && team && (
              <Typography variant="body2" color="text.secondary">
                {team}
              </Typography>
            )}
          </Box>
          <Tooltip title="Read article">
            <IconButton
              component="a"
              href={articleUrl.href}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`Read article about ${name}`}
              size="small"
              sx={{ minWidth: 44, minHeight: 44, flexShrink: 0 }}
            >
              <OpenInNewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>

        {isTransfer && (
          <Stack
            direction="row"
            spacing={2}
            alignItems="center"
            justifyContent="center"
            sx={{ textAlign: "center" }}
          >
            <TeamIdentity team={news.current_team} />
            <ArrowRightAltRoundedIcon
              titleAccess="Transfers to"
              color="primary"
              sx={{ fontSize: 28, flexShrink: 0 }}
            />
            <TeamIdentity team={news.new_team} />
          </Stack>
        )}

        <Stack
          direction="row"
          useFlexGap
          flexWrap="wrap"
          gap={1}
          alignItems="center"
        >
          <Tooltip title={news.confirmed ? "Confirmed" : "Speculative"}>
            <Chip
              icon={
                news.confirmed ? (
                  <CheckCircleIcon titleAccess="Confirmed" />
                ) : (
                  <HelpOutlineIcon titleAccess="Speculative" />
                )
              }
              label={isTransfer ? "Transfer" : news.info_type}
              size="small"
              sx={{
                height: 20,
                px: 0.75,
                gap: 0.5,
                fontSize: "0.75rem",
                "& .MuiChip-icon": {
                  fontSize: 14,
                  m: 0,
                  flexShrink: 0,
                  color: news.confirmed ? "success.main" : "warning.main",
                },
                "& .MuiChip-label": {
                  px: 0,
                  display: "flex",
                  alignItems: "center",
                  height: "100%",
                  lineHeight: 1,
                },
              }}
            />
          </Tooltip>
          {news.availability_time && (
            <Stack
              direction="row"
              spacing={0.5}
              alignItems="center"
              sx={{ minWidth: 0 }}
            >
              <Tooltip title={availabilityLabel}>
                <AccessTimeIcon
                  titleAccess={availabilityLabel}
                  color="action"
                  sx={{ fontSize: 14, flexShrink: 0 }}
                />
              </Tooltip>
              <Typography
                variant="caption"
                sx={{ overflowWrap: "anywhere", minWidth: 0 }}
              >
                {news.availability_time}
              </Typography>
            </Stack>
          )}
          <Typography
            component="time"
            dateTime={news.article.article_date}
            variant="caption"
            color="text.secondary"
            sx={{ ml: "auto", whiteSpace: "nowrap" }}
          >
            {date.toLocaleDateString(undefined, {
              day: "numeric",
              month: "short",
              year: "numeric",
            })}
          </Typography>
        </Stack>
      </Stack>
    </Paper>
  );
};
