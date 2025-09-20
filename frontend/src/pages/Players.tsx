import React, { useContext, useState } from "react";
import {
  Box,
  Paper,
  Drawer,
  Button,
  IconButton,
  Typography,
  useTheme,
  useMediaQuery
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { type LastPlayerStats } from "../client";
import { HockeyPlayerSearch } from "../components/player/HockeyPlayerSearch";
import { PlayerDashboard } from "../components/player/PlayerDashboard";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { EmptyState } from "../components/common/EmptyState";
import { PlayerStatsContext } from "../context/PlayerStatsContext";

export const Players: React.FC = () => {
  const { playerStats, loading, error } = useContext(PlayerStatsContext);
  const [selectedPlayer, setSelectedPlayer] = useState<LastPlayerStats | null>(
    null,
  );
  const [drawerOpen, setDrawerOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

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

  const drawerWidth = 300;

  return (
    <Box sx={{ display: "flex", height: "100%", flexDirection: isMobile ? "column" : "row" }}>
      {!isMobile ? (
        <Paper
          elevation={2}
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            height: "100%",
          }}
        >
          <HockeyPlayerSearch
            players={playerStats}
            setSelectedHockeyPlayer={setSelectedPlayer}
            selectedPlayer={selectedPlayer}
          />
        </Paper>
      ) : (
        <>
          <Box sx={{ p: 1 }}>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => setDrawerOpen(true)}
            >
              Search Player
            </Button>
          </Box>

          <Drawer
            variant="temporary"
            anchor="bottom"
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
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
            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", p: 2, borderBottom: 1, borderColor: "divider" }}>
              <Typography variant="h6">
                Select Player
              </Typography>
              <IconButton onClick={() => setDrawerOpen(false)}>
                <CloseIcon />
              </IconButton>
            </Box>
            <Box sx={{ flex: 1, overflow: "hidden" }}>
              <HockeyPlayerSearch
                players={playerStats}
                setSelectedHockeyPlayer={(player) => {
                  setSelectedPlayer(player);
                  setDrawerOpen(false);
                }}
                selectedPlayer={selectedPlayer}
              />
            </Box>
          </Drawer>
        </>
      )}

      <Box
        sx={{
          flexGrow: 1,
          height: isMobile ? "calc(100% - 56px)" : "100%",
        }}
      >
        <PlayerDashboard selectedPlayer={selectedPlayer} />
      </Box>
    </Box>
  );
};
