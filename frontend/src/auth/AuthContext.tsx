import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api, TOKEN_KEY } from "@/src/api/client";
import { storage } from "@/src/utils/storage";

export type Rol = "socio" | "contador";

export interface AppUser {
  id: string;
  nombre: string;
  email: string;
  telefono: string | null;
  rol: Rol;
  pozo_id: string;
  orden: number | null;
}

export interface Pozo {
  id: string;
  nombre: string;
  dominio: string;
  accent: string;
  festivos: string[];
  inicio: string;
}

interface AuthValue {
  user: AppUser | null;
  pozo: Pozo | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<AppUser>;
  signOut: () => Promise<void>;
  changePassword: (current: string, next: string) => Promise<void>;
}

const AuthContext = createContext<AuthValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null);
  const [pozo, setPozo] = useState<Pozo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const token = await storage.secureGet<string>(TOKEN_KEY, "");
      if (token) {
        try {
          const res = await api.get("/auth/me");
          setUser(res.data.user);
          setPozo(res.data.pozo);
        } catch {
          await storage.secureRemove(TOKEN_KEY);
        }
      }
      setLoading(false);
    })();
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const res = await api.post("/auth/login", { email, password });
    await storage.secureSet(TOKEN_KEY, res.data.access_token);
    setUser(res.data.user);
    setPozo(res.data.pozo);
    return res.data.user as AppUser;
  }, []);

  const signOut = useCallback(async () => {
    await storage.secureRemove(TOKEN_KEY);
    setUser(null);
    setPozo(null);
  }, []);

  const changePassword = useCallback(async (current: string, next: string) => {
    await api.post("/auth/change-password", {
      current_password: current,
      new_password: next,
    });
  }, []);

  return (
    <AuthContext.Provider value={{ user, pozo, loading, signIn, signOut, changePassword }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
