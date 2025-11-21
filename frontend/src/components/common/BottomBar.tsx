import React from "react";
import { BottomNavigation, BottomNavigationAction } from "@mui/material";
import {
  Dashboard as DashboardIcon,
  Sports as SportsIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import { useNavigate, useLocation } from "react-router-dom";

const menuItems = [
  { text: "Dashboard", icon: <DashboardIcon />, path: "/" },
  { text: "Players", icon: <SportsIcon />, path: "/players" },
  { text: "Transfer Analytics", icon: <TrendingUpIcon />, path: "/transfer-analytics" },
];

export const BottomBar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const currentIndex = menuItems.findIndex(
    (item) => item.path === location.pathname,
  );

  return (
    <BottomNavigation
      value={currentIndex}
      onChange={(_event, newValue) => {
        if (newValue >= 0 && newValue < menuItems.length) {
          handleNavigation(menuItems[newValue].path);
        }
      }}
      showLabels
      sx={{ position: "fixed", bottom: 0, left: 0, right: 0 }}
    >
      {menuItems.map((item) => (
        <BottomNavigationAction
          key={item.text}
          label={item.text}
          icon={item.icon}
        />
      ))}
    </BottomNavigation>
  );
};
