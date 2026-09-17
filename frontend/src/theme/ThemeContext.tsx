import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { storage } from "@/src/utils/storage";
import { lightColors, darkColors, AppColors } from "./colors";

type Mode = "light" | "dark";

interface ThemeValue {
  mode: Mode;
  isDark: boolean;
  colors: AppColors;
  toggle: () => void;
  ready: boolean;
}

const ThemeContext = createContext<ThemeValue | undefined>(undefined);
const THEME_KEY = "theme_mode";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<Mode>("light");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      const saved = await storage.getItem<string>(THEME_KEY, "light");
      if (saved === "dark" || saved === "light") setMode(saved);
      setReady(true);
    })();
  }, []);

  const toggle = useCallback(() => {
    setMode((prev) => {
      const next = prev === "light" ? "dark" : "light";
      storage.setItem(THEME_KEY, next);
      return next;
    });
  }, []);

  const value: ThemeValue = {
    mode,
    isDark: mode === "dark",
    colors: mode === "dark" ? darkColors : lightColors,
    toggle,
    ready,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme debe usarse dentro de ThemeProvider");
  return ctx;
}
