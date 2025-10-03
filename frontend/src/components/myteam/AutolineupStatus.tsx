import React, { useState } from "react";
import {
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
} from "@mui/material";
import { type Manager } from "../../client";
import { LoginForm, type LoginFormField } from "../common/LoginForm";
import {
  registerForAutolinupMyteamAutolineupRegisterPost,
  unregisterForAutolinupMyteamAutolineupUnregisterPost,
} from "../../client";

interface AutolineupStatusProps {
  manager: Manager;
  onUpdate: (manager: Manager) => void;
}

interface TeamLoginData extends Record<string, string> {
  hmPassword: string;
}

const teamLoginFields: LoginFormField[] = [
  { key: "hmPassword", label: "HM Password", type: "password" },
];

export const AutolineupStatus: React.FC<AutolineupStatusProps> = ({
  manager,
  onUpdate,
}) => {
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");

  const handleClick = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };
  const isRegistering = !manager.autolineup;

  const handleSubmit = async (formData: TeamLoginData) => {
    setError("");

    if (!manager.email) {
      setError("No email set");
      return;
    }

    const { error, data } = isRegistering
      ? await registerForAutolinupMyteamAutolineupRegisterPost({
          body: {
            hm_user: manager.email,
            hm_password: formData.hmPassword,
          },
        })
      : await unregisterForAutolinupMyteamAutolineupUnregisterPost({
          body: {
            hm_user: manager.email,
            hm_password: formData.hmPassword,
          },
        });
    if (data) {
      onUpdate(data);
    }
    if (error) {
      setError(
        error.detail?.toString() || "An error occurred. Please try again.",
      );
      return;
    }

    handleClose();
  };

  return (
    <>
      <Chip
        label={manager.autolineup ? "Autolineup ON" : "Autolineup OFF"}
        color={manager.autolineup ? "success" : "default"}
        variant="outlined"
        onClick={handleClick}
        clickable
      />

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {isRegistering ? "Autolineup registration" : "Disable Autolineup"}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {isRegistering
              ? "Your password will be saved encrypted for this functionality to work."
              : "All information concerning your password will be completely erased."}
          </Typography>
          {error && (
            <Typography variant="body2" color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}
          <LoginForm<TeamLoginData>
            fields={teamLoginFields}
            buttonText={
              isRegistering ? "Activate autolineup" : "Deactivate autolineup"
            }
            loadingText={isRegistering ? "Registering..." : "Unregistering..."}
            onSubmit={handleSubmit}
          />
        </DialogContent>
      </Dialog>
    </>
  );
};
