import React from "react";
import { PerfilContent } from "@/src/components/PerfilContent";
import { useAuth } from "@/src/auth/AuthContext";

export default function ContadorPerfil() {
  const { pozo } = useAuth();
  return <PerfilContent accent={pozo?.accent} />;
}
