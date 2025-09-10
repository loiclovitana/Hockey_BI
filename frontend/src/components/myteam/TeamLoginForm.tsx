import React from "react";
import Lottie from "lottie-react";
import { LoginForm, type LoginFormField } from "../common/LoginForm";
import { loadMyteamLoadPost, type DashBoardData } from "../../client";
import logoLottie from "../../../public/logo-lottie.json";
import { Container, Typography } from "@mui/material";

interface TeamLoginFormProps {
  onSuccess: (data: DashBoardData) => void;
}

interface TeamLoginData extends Record<string, string> {
  hmUser: string;
  hmPassword: string;
}

const teamLoginFields: LoginFormField[] = [
  { key: "hmUser", label: "HM Username" },
  { key: "hmPassword", label: "HM Password", type: "password" },
];

export const TeamLoginForm: React.FC<TeamLoginFormProps> = ({ onSuccess }) => {
  const handleSubmit = async (formData: TeamLoginData) => {
    const response = await loadMyteamLoadPost({
      query: {
        hm_user: formData.hmUser,
        hm_password: formData.hmPassword,
      },
    });

    if (response.data) {
      onSuccess(response.data);
    }

    if (response.error) {
      console.error(response.error);
      throw new Error("Failed to load team data");
    }
  };

  return (
    <Container
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        pt: 4,
      }}
    >
      <Typography variant="h2" gutterBottom align="center">
        Start now
      </Typography>
      <LoginForm<TeamLoginData>
        fields={teamLoginFields}
        buttonText="Load my HM data"
        loadingText="Loading..."
        onSubmit={handleSubmit}
      />
      <Lottie
        animationData={logoLottie}
        loop={false}
        //style={{ width: "50%" }}
      />
    </Container>
  );
};
