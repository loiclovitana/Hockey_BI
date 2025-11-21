import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AppBar, Toolbar, Typography, Box } from "@mui/material";
import { BottomBar } from "./components/common/BottomBar";
import { LogoutButton } from "./components/common/LogoutButton";
import { Dashboard } from "./pages/Dashboard";
import { Players } from "./pages/Players";
import { Admin } from "./pages/Admin";
import { TransferAnalytics } from "./pages/TransferAnalytics";
import { PlayerStatsProvider } from "./context/PlayerStatsProvider";
import { DashboardProvider } from "./context/DashboardProvider";

import { client } from "./client/client.gen";

const backend_url = import.meta.env.VITE_BACKEND_URL;

client.setConfig({
  baseUrl: backend_url ? backend_url : "http://localhost:8000/",
});

function App() {
  return (

    <PlayerStatsProvider>
      <DashboardProvider>
        <Router>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              height: "100dvh",
              width: "100vw",
            }}
          >
            <AppBar position="fixed">
              <Toolbar>
                <img
                  src="/ico.svg"
                  alt="Hockey BI Logo"
                  style={{ height: "46px", marginRight: "12px" }}
                />
                <Typography variant="h6" noWrap component="div">
                  Hockey BI
                </Typography>
                <LogoutButton />
              </Toolbar>
            </AppBar>

            <Box
              component="main"
              sx={{
                flex: 1,
                overflow: "auto",
                py: "64px",
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/players" element={<Players />} />
                <Route path="/admin" element={<Admin />} />
                <Route path="/transfer-analytics" element={<TransferAnalytics />} />
              </Routes>
            </Box>
            <BottomBar />
          </Box>
        </Router>
      </DashboardProvider>
    </PlayerStatsProvider>

  );
}

export default App;
