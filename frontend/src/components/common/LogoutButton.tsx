import { Button } from "@mui/material";
import { LogoutOutlined } from "@mui/icons-material";
import { useDashboard } from "../../hooks/useDashboard";

export const LogoutButton = () => {
  const { setDashboardData } = useDashboard();

  const handleLogout = () => {
    setDashboardData(null);
  };

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
