import React from "react";
import { Box, Typography } from "@mui/material";

interface SectionHeaderProps {
  title: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({ title }) => {
  return (
    <Box
      sx={{
        background: (theme) =>
          `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.primary.light} 90%)`,
        color: "white",
        p: 1,
        borderRadius: 1,
      }}
    >
      <Typography variant="subtitle1" fontWeight="bold">
        {title}
      </Typography>
    </Box>
  );
};
