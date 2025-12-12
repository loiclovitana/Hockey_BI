import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Lottie from "lottie-react";
import { LoginForm, type LoginFormField } from "../common/LoginForm";
import { loadMyteamLoadPost, type DashBoardData } from "../../client";
import logoLottie from "../../assets/logo-lottie.json";
import { Container } from "@mui/material";
import { useDashboard } from "../../hooks/useDashboard";

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
  const [clickCount, setClickCount] = useState(0);
  const navigate = useNavigate();
  const { setCredentials } = useDashboard();

  const handleLottieClick = () => {
    setClickCount((prev) => prev + 1);
  };

  useEffect(() => {
    if (clickCount == 5) {
      navigate("/admin");
    }
  }, [clickCount, navigate]);

  const handleSubmit = async (formData: TeamLoginData) => {
    const response = await loadMyteamLoadPost({
      body: {
        hm_user: formData.hmUser,
        hm_password: formData.hmPassword,
      },
    });

    if (response.data) {
      setCredentials({
        hm_user: formData.hmUser,
        hm_password: formData.hmPassword,
      });
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
        pt: 2,
      }}
    >
      <Lottie
        animationData={logoLottie}
        loop={false}
        onClick={handleLottieClick}
      />
      <LoginForm<TeamLoginData>
        fields={teamLoginFields}
        buttonText="Load my HM data"
        loadingText="Loading..."
        onSubmit={handleSubmit}
      />
    </Container>
  );
};
