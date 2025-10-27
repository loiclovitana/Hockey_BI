import React from "react";
import { Box } from "@mui/material";

interface ValueWithDifferenceProps {
  value: number;
  baseValue: number;
  decimals?: number;
}

export const ValueWithDifference: React.FC<ValueWithDifferenceProps> = ({
  value,
  baseValue,
  decimals = 1,
}) => {
  const difference = value - baseValue;
  const sign = difference > 0 ? "+" : "";
  const color =
    difference > 0
      ? "success.main"
      : difference < 0
        ? "error.main"
        : "text.primary";

  return (
    <Box component="span">
      {value.toFixed(decimals)}{" "}
      <Box component="span" sx={{ color }}>
        ({sign}
        {difference.toFixed(decimals)})
      </Box>
    </Box>
  );
};
