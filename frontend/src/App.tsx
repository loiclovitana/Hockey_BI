import React, { useState } from "react";
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
import { Sidebar } from "./components/Sidebar";
import { Dashboard } from "./pages/Dashboard";
import { Players } from "./pages/Players";
import { Analytics } from "./pages/Analytics";
import { Settings } from "./pages/Settings";

import { client } from './client/client.gen';

client.setConfig({
  baseUrl: 'http://localhost:8000/',
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
      <Router>
        <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
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

          <Box sx={{ display: "flex", flexDirection: "row", flex: 1,
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
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Box>
        </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
