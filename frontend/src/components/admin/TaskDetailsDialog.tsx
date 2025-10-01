import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Divider,
  Paper,
  Alert,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import type { Task } from "../../client/types.gen";

interface TaskDetailsDialogProps {
  task: Task | null;
  open: boolean;
  onClose: () => void;
}

export const TaskDetailsDialog: React.FC<TaskDetailsDialogProps> = ({
  task,
  open,
  onClose,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (!task) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      fullScreen={isMobile}
    >
      <DialogTitle>Task Details: {task.name}</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" component="div" gutterBottom>
            <strong>ID:</strong> {task.id}
          </Typography>
          <Typography variant="body2" component="div" gutterBottom>
            <strong>Status:</strong>{" "}
            <Chip
              label={task.error ? "Failed" : "Success"}
              color={task.error ? "error" : "success"}
              size="small"
            />
          </Typography>
          <Typography variant="body2" component="div" gutterBottom>
            <strong>Start Time:</strong> {formatDateTime(task.start_at)}
          </Typography>
          <Typography variant="body2" component="div" gutterBottom>
            <strong>End Time:</strong> {formatDateTime(task.end_at)}
          </Typography>
        </Box>

        {task.error && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="error" gutterBottom>
              Error Message:
            </Typography>
            <Paper
              sx={{
                p: 2,
                bgcolor: "error.light",
                color: "error.contrastText",
                fontFamily: "monospace",
                fontSize: "0.875rem",
                overflowX: "auto",
                mb: 2,
              }}
            >
              {task.error}
            </Paper>
          </>
        )}

        {task.stacktrace && (
          <>
            <Typography variant="subtitle2" color="error" gutterBottom>
              Stack Trace:
            </Typography>
            <Paper
              sx={{
                p: 2,
                bgcolor: "grey.900",
                color: "grey.100",
                fontFamily: "monospace",
                fontSize: "0.75rem",
                overflowX: "auto",
                whiteSpace: "pre-wrap",
              }}
            >
              {task.stacktrace}
            </Paper>
          </>
        )}

        {!task.error && (
          <Alert severity="success">
            Task completed successfully with no errors
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};
