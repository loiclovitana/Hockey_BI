import { useId, useState } from "react";
import {
  Autocomplete,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  MenuItem,
  Paper,
  Switch,
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import FilterListIcon from "@mui/icons-material/FilterList";
import { type PlayerFilters } from "./playerFilters";

interface DashboardPlayerFiltersProps {
  filters: PlayerFilters;
  clubs: string[];
  onChange: (filters: PlayerFilters) => void;
  onReset: () => void;
}

export const DashboardPlayerFilters = ({
  filters,
  clubs,
  onChange,
  onReset,
}: DashboardPlayerFiltersProps) => {
  const [open, setOpen] = useState(false);
  const dialogId = useId();
  const titleId = `${dialogId}-title`;
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const activeFilterCount = [
    filters.role !== "",
    filters.minPrice !== "",
    filters.maxPrice !== "",
    filters.clubs.length > 0,
    filters.eligibleOnly,
    filters.swissOnly,
  ].filter(Boolean).length;
  const invalidPriceRange =
    filters.minPrice !== "" &&
    filters.maxPrice !== "" &&
    Number(filters.minPrice) > Number(filters.maxPrice);

  const filterControls = (
    <>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "1fr 2fr 2fr" },
          gap: 2,
          alignItems: "start",
        }}
      >
        <TextField
          select
          label="Role"
          size="small"
          value={filters.role}
          onChange={(event) =>
            onChange({
              ...filters,
              role: event.target.value as PlayerFilters["role"],
            })
          }
        >
          <MenuItem value="">All roles</MenuItem>
          <MenuItem value="FW">FW</MenuItem>
          <MenuItem value="DF">DF</MenuItem>
        </TextField>
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            label="Min price"
            type="number"
            size="small"
            fullWidth
            value={filters.minPrice}
            error={invalidPriceRange}
            slotProps={{ htmlInput: { min: 0, step: "any" } }}
            onChange={(event) =>
              onChange({ ...filters, minPrice: event.target.value })
            }
          />
          <TextField
            label="Max price"
            type="number"
            size="small"
            fullWidth
            value={filters.maxPrice}
            error={invalidPriceRange}
            helperText={
              invalidPriceRange
                ? "Must be at least the minimum price"
                : undefined
            }
            slotProps={{ htmlInput: { min: 0, step: "any" } }}
            onChange={(event) =>
              onChange({ ...filters, maxPrice: event.target.value })
            }
          />
        </Box>
        <Autocomplete
          multiple
          disableCloseOnSelect
          size="small"
          options={clubs}
          value={filters.clubs}
          onChange={(_, selectedClubs) =>
            onChange({ ...filters, clubs: selectedClubs })
          }
          renderOption={({ key, ...optionProps }, club) => (
            <Box component="li" key={key} {...optionProps} sx={{ gap: 1.5 }}>
              <Box
                component="img"
                src={`/club/${club}.webp`}
                alt=""
                sx={{ width: 28, height: 28, objectFit: "contain" }}
              />
              {club}
            </Box>
          )}
          renderValue={(selectedClubs, getItemProps) =>
            selectedClubs.map((club, index) => {
              const { key, ...itemProps } = getItemProps({ index });
              return (
                <Chip
                  key={key}
                  {...itemProps}
                  size="small"
                  label={club}
                  icon={
                    <Box
                      component="img"
                      src={`/club/${club}.webp`}
                      alt=""
                      sx={{ width: 20, height: 20, objectFit: "contain" }}
                    />
                  }
                />
              );
            })
          }
          renderInput={(params) => (
            <TextField
              {...params}
              label="Teams"
              placeholder={filters.clubs.length === 0 ? "All teams" : undefined}
            />
          )}
        />
      </Box>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 1 }}>
        <FormControlLabel
          control={
            <Switch
              checked={filters.swissOnly}
              onChange={(_, checked) =>
                onChange({ ...filters, swissOnly: checked })
              }
            />
          }
          label="Swiss only"
        />
        <FormControlLabel
          control={
            <Switch
              checked={filters.eligibleOnly}
              onChange={(_, checked) =>
                onChange({ ...filters, eligibleOnly: checked })
              }
            />
          }
          label="Eligible for a price change only (at least 5 matches played)"
        />
      </Box>
    </>
  );

  if (isMobile) {
    return (
      <Box sx={{ mb: 2 }}>
        <Button
          variant="outlined"
          fullWidth
          startIcon={<FilterListIcon />}
          aria-haspopup="dialog"
          aria-expanded={open}
          aria-controls={open ? dialogId : undefined}
          onClick={() => setOpen(true)}
          sx={{ minHeight: 44 }}
        >
          Filters{activeFilterCount > 0 ? ` (${activeFilterCount})` : ""}
        </Button>
        <Dialog
          id={dialogId}
          fullScreen
          open={open}
          onClose={() => setOpen(false)}
          aria-labelledby={titleId}
        >
          <DialogTitle
            id={titleId}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            Player filters
            <IconButton
              aria-label="Close filters"
              size="large"
              onClick={() => setOpen(false)}
            >
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent dividers>
            <Box sx={{ pt: 1 }}>{filterControls}</Box>
          </DialogContent>
          <DialogActions sx={{ p: 2, justifyContent: "space-between" }}>
            <Button onClick={onReset} sx={{ minHeight: 44 }}>
              Reset filters
            </Button>
            <Button
              variant="contained"
              onClick={() => setOpen(false)}
              sx={{ minHeight: 44 }}
            >
              Show players
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  }

  return (
    <Paper component="section" aria-label="Player filters" sx={{ p: 2, mb: 2 }}>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          mb: 2,
        }}
      >
        <Typography variant="subtitle1" fontWeight="bold">
          Player filters
        </Typography>
        <Button size="small" onClick={onReset}>
          Reset filters
        </Button>
      </Box>
      {filterControls}
    </Paper>
  );
};
