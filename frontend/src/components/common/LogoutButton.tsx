import { Button } from "@mui/material";
import { LoginOutlined, LogoutOutlined } from "@mui/icons-material";
import { Link } from "react-router-dom";
import { useDashboard } from "../../hooks/useDashboard";

export const LogoutButton = () => {
  const { dashboardData, setDashboardData, setCredentials } = useDashboard();

  const handleLogout = () => {
    setDashboardData(null);
    setCredentials(null);
  };

  if (!dashboardData) {
    return (
      <Button
        component={Link}
        to="/"
        color="inherit"
        startIcon={<LoginOutlined />}
        sx={{ ml: "auto" }}
      >
        Login
      </Button>
    );
  }

  return (
    <Button
      color="inherit"
      onClick={handleLogout}
      startIcon={<LogoutOutlined />}
      sx={{ ml: "auto" }}
    >
      Logout
    </Button>
  );
};
