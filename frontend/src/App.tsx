import  { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import {
  ThemeProvider,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
} from "@mui/material";
import { Menu as MenuIcon } from "@mui/icons-material";
import { theme } from "./theme";
import { Sidebar } from "./components/common/Sidebar";
import { Dashboard } from "./pages/Dashboard";
import { Players } from "./pages/Players";
import { PlayerStatsProvider } from "./context/PlayerStatsProvider";

import { client } from './client/client.gen';

const backend_url = import.meta.env.VITE_BACKEND_URL;

client.setConfig({
  baseUrl: backend_url? backend_url:'http://localhost:8000/',
});

const SIDEBAR_WIDTH = "240px";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <PlayerStatsProvider>
        <Router>
        <Box sx={{ display: "flex", height: "100vh" }}>
          <AppBar
            position="fixed"
            sx={{
              zIndex: (theme) => theme.zIndex.drawer + 1,
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="toggle sidebar"
                edge="start"
                onClick={handleSidebarToggle}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div">
                Hockey BI
              </Typography>
            </Toolbar>
          </AppBar>

          <Box sx={{ display: "flex",  flex: 1,
            maxHeight:"100vh"
            , pt: (theme) => `${theme.mixins.toolbar.minHeight}px` }}>
            <Sidebar open={sidebarOpen} width={SIDEBAR_WIDTH}/>

            <Box
              component="main"
              sx={{
                 marginLeft: sidebarOpen ? 0 : "-"+SIDEBAR_WIDTH,
                 flex: 1,
                transition: (theme) =>
                  theme.transitions.create("margin-left", {
                    easing: theme.transitions.easing.easeInOut,
                    duration: theme.transitions.duration.short,
                  }),
              }}
            >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/players" element={<Players />} />
            </Routes>
          </Box>
        </Box>
        </Box>
        </Router>
      </PlayerStatsProvider>
    </ThemeProvider>
  );
}

export default App;
