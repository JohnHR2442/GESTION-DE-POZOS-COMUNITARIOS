import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from "react";
import { Platform } from "react-native";
import { api } from "@/src/api/client";
import { storage } from "@/src/utils/storage";
import { useAuth } from "@/src/auth/AuthContext";

export interface Notif {
  id: string;
  tipo: string;
  titulo: string;
  mensaje: string;
  fecha: string;
  leida: boolean;
}

interface NotifValue {
  items: Notif[];
  unread: number;
  reload: () => Promise<void>;
  markAll: () => Promise<void>;
  requestWebPermission: () => Promise<void>;
}

const NotificationsContext = createContext<NotifValue | undefined>(undefined);

const LAST_SEEN_KEY = "notif_last_seen";
const POLL_MS = 30000;

async function fireNotification(titulo: string, mensaje: string) {
  if (Platform.OS === "web") {
    try {
      if (typeof window !== "undefined" && "Notification" in window && Notification.permission === "granted") {
        new Notification(titulo, { body: mensaje });
      }
    } catch {
      // ignore
    }
  } else {
    try {
      const Notifications = await import("expo-notifications");
      await Notifications.scheduleNotificationAsync({
        content: { title: titulo, body: mensaje },
        trigger: null,
      });
    } catch {
      // expo-notifications no disponible en este entorno (Expo Go)
    }
  }
}

export function NotificationsProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [items, setItems] = useState<Notif[]>([]);
  const [unread, setUnread] = useState(0);
  const lastSeenRef = useRef<string>("");
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const reload = useCallback(async () => {
    if (!user) return;
    try {
      const res = await api.get("/notificaciones");
      const data: Notif[] = res.data;
      setItems(data);
      setUnread(data.filter((n) => !n.leida).length);
    } catch {
      // silencioso
    }
  }, [user]);

  const poll = useCallback(async () => {
    if (!user) return;
    try {
      const since = lastSeenRef.current;
      const res = await api.get("/notificaciones/pendientes", {
        params: since ? { since } : {},
      });
      const { pendientes, no_leidas, server_time } = res.data;
      // Notificar nuevos eventos posteriores al ultimo visto
      if (since && Array.isArray(pendientes)) {
        for (const n of pendientes) {
          await fireNotification(n.titulo, n.mensaje);
        }
      }
      lastSeenRef.current = server_time;
      await storage.setItem(LAST_SEEN_KEY, server_time);
      setUnread(no_leidas);
      if (Array.isArray(pendientes) && pendientes.length) await reload();
    } catch {
      // silencioso
    }
  }, [user, reload]);

  useEffect(() => {
    if (!user) {
      setItems([]);
      setUnread(0);
      if (timer.current) clearInterval(timer.current);
      return;
    }
    (async () => {
      const saved = await storage.getItem<string>(LAST_SEEN_KEY, "");
      lastSeenRef.current = saved || new Date().toISOString();
      registerForPush(user.id);
      await reload();
      await poll();
    })();
    timer.current = setInterval(poll, POLL_MS);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [user, poll, reload]);

  const markAll = useCallback(async () => {
    if (!user) return;
    try {
      await api.post("/notificaciones/leer-todas");
      setUnread(0);
      setItems((prev) => prev.map((n) => ({ ...n, leida: true })));
    } catch {
      // silencioso
    }
  }, [user]);

  const requestWebPermission = useCallback(async () => {
    if (Platform.OS === "web") {
      try {
        if (typeof window !== "undefined" && "Notification" in window && Notification.permission === "default") {
          await Notification.requestPermission();
        }
      } catch {
        // ignore
      }
    } else {
      try {
        const Notifications = await import("expo-notifications");
        await Notifications.requestPermissionsAsync();
      } catch {
        // ignore
      }
    }
  }, []);

  return (
    <NotificationsContext.Provider value={{ items, unread, reload, markAll, requestWebPermission }}>
      {children}
    </NotificationsContext.Provider>
  );
}

export function useNotifications(): NotifValue {
  const ctx = useContext(NotificationsContext);
  if (!ctx) throw new Error("useNotifications debe usarse dentro de NotificationsProvider");
  return ctx;
}
