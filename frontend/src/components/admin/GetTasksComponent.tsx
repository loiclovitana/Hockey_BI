import React, { useState, useEffect } from "react";
import {
  Typography,
  Alert,
  CircularProgress,
  Box,
  Chip,
  Card,
  CardContent,
  Divider,
  Pagination,
  IconButton,
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import { getTasksAdminTasksGet } from "../../client/sdk.gen";
import type { Task } from "../../client/types.gen";
import { TaskDetailsDialog } from "./TaskDetailsDialog";

interface GetTasksComponentProps {
  token: string;
}

const ITEMS_PER_PAGE = 5;

export const GetTasksComponent: React.FC<GetTasksComponentProps> = ({
  token,
}) => {
  const [loading, setLoading] = useState(false);
  const [tasks, setTasks] = useState<Task[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [page, setPage] = useState(1);
  const [totalTasks, setTotalTasks] = useState(0);

  const handleGetTasks = async (currentPage: number) => {
    setLoading(true);
    setError(null);

    try {
      const response = await getTasksAdminTasksGet({
        headers: {
          Authorization: `Bearer ${token}`,
        },
        query:{
          limit: ITEMS_PER_PAGE,
          offset: (currentPage - 1) * ITEMS_PER_PAGE
        }
      });
      if (response.data) {
        setTasks(response.data);
        // Note: You may need to update this if the API returns total count
        // For now, assuming if we get less than ITEMS_PER_PAGE, it's the last page
        if (response.data.length < ITEMS_PER_PAGE) {
          setTotalTasks((currentPage - 1) * ITEMS_PER_PAGE + response.data.length);
        } else {
          setTotalTasks(currentPage * ITEMS_PER_PAGE + 1); // At least one more page
        }
      }
      if (response.error) {
        setError(`Couldn't get tasks ${response.error}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleGetTasks(page);
  }, [page, token]);

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
  };

  const handleCloseDialog = () => {
    setSelectedTask(null);
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " - " + date.toLocaleTimeString();
  };
  const timeDiff = (start: string, end: string) => {
    const date_start = new Date(start);
    const date_end = new Date(end);
    const diffMs = date_end.getTime() - date_start.getTime();

    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);
    const milliseconds = diffMs % 1000;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else if (seconds > 0) {
      return `${seconds}s`;
    } else {
      return `${milliseconds}ms`;
    }
  };

  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">
          Task History
        </Typography>
        <IconButton
          size="small"
          onClick={() => handleGetTasks(page)}
          disabled={loading}
        >
          <RefreshIcon fontSize="small" />
        </IconButton>
      </Box>

      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {!loading && tasks && tasks.length === 0 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          No tasks found
        </Alert>
      )}

      {!loading && tasks && tasks.length > 0 && (
        <Box sx={{ pt: 2 }}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {tasks.map((task) => (
              <Card
                key={task.id}
                onClick={() => handleTaskClick(task)}
                sx={{
                  cursor: "pointer",
                  "&:hover": { bgcolor: "action.hover" },
                }}
                elevation={2}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                    }}
                  >
                    <Typography variant="subtitle1" fontWeight="bold">
                      {task.name}
                    </Typography>
                    <Chip
                      label={task.error ? "Failed" : "Success"}
                      color={task.error ? "error" : "success"}
                      size="small"
                    />
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                    }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      {formatDateTime(task.start_at)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {timeDiff(task.start_at, task.end_at)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>

          {totalTasks > ITEMS_PER_PAGE && (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
              <Pagination
                count={Math.ceil(totalTasks / ITEMS_PER_PAGE)}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}
        </Box>
      )}

      <TaskDetailsDialog
        task={selectedTask}
        open={!!selectedTask}
        onClose={handleCloseDialog}
      />
    </>
  );
};
