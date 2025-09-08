import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#d25419ff",
    },
    secondary: {
      main: "#dc0000ff",
    },
    background: {
      default: "#1c1815ff",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});
