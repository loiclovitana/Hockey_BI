import React from "react";
import { BottomNavigation, BottomNavigationAction } from "@mui/material";
import {
  Dashboard as DashboardIcon,
  Sports as SportsIcon,
  TrendingUp as TrendingUpIcon,
  Newspaper as NewspaperIcon,
} from "@mui/icons-material";
import { useNavigate, useLocation } from "react-router-dom";

const menuItems = [
  { text: "Dashboard", icon: <DashboardIcon />, path: "/" },
  { text: "Players", icon: <SportsIcon />, path: "/players" },
  { text: "News", icon: <NewspaperIcon />, path: "/news" },
  {
    text: "History",
    icon: <TrendingUpIcon />,
    path: "/transfer-analytics",
  },
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
      sx={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        height: "calc(56px + env(safe-area-inset-bottom, 0px))",
        pb: "env(safe-area-inset-bottom, 0px)",
        pl: "env(safe-area-inset-left, 0px)",
        pr: "env(safe-area-inset-right, 0px)",
      }}
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
