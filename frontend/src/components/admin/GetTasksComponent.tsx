import React, { useState } from "react";
import {
  Button,
  Typography,
  Alert,
  CircularProgress,
  Box,
  Chip,
  Card,
  CardContent,
  Divider,
} from "@mui/material";
import { getTasksAdminTasksGet } from "../../client/sdk.gen";
import type { Task } from "../../client/types.gen";
import { TaskDetailsDialog } from "./TaskDetailsDialog";

interface GetTasksComponentProps {
  token: string;
}

export const GetTasksComponent: React.FC<GetTasksComponentProps> = ({
  token,
}) => {
  const [loading, setLoading] = useState(false);
  const [tasks, setTasks] = useState<Task[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const handleGetTasks = async () => {
    setLoading(true);
    setError(null);
    setTasks(null);

    try {
      const response = await getTasksAdminTasksGet({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.data) {
        setTasks(response.data);
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
      <Typography variant="h6" gutterBottom>
        Task History
      </Typography>

      <Button
        variant="contained"
        onClick={handleGetTasks}
        disabled={loading}
        fullWidth
      >
        {loading ? <CircularProgress size={24} /> : "Get Tasks"}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {tasks && tasks.length === 0 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          No tasks found
        </Alert>
      )}

      {tasks && tasks.length > 0 && (
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
