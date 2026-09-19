import { Platform } from "react-native";
import Constants from "expo-constants";
import { storage } from "@/src/utils/storage";
import { api } from "@/src/api/client";

const INSTALL_KEY = "push_installation_id";

function makeId(): string {
  return "inst_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 12);
}

export async function getInstallationId(): Promise<string> {
  let id = await storage.getItem<string>(INSTALL_KEY, "");
  if (!id) {
    id = makeId();
    await storage.setItem(INSTALL_KEY, id);
  }
  return id;
}

/**
 * Obtiene (y solicita si hace falta) el token push del dispositivo.
 * Devuelve null en web o si el usuario no concede permiso.
 */
async function obtenerToken(): Promise<string | null> {
  if (Platform.OS === "web") return null;
  try {
    const Notifications = await import("expo-notifications");
    const actual = await Notifications.getPermissionsAsync();
    let status = actual.status;
    if (status !== "granted" && actual.canAskAgain) {
      const req = await Notifications.requestPermissionsAsync();
      status = req.status;
    }
    if (status !== "granted") return null;

    const projectId =
      (Constants as any)?.expoConfig?.extra?.eas?.projectId ??
      (Constants as any)?.easConfig?.projectId;
    const tokenData = await Notifications.getExpoPushTokenAsync(
      projectId ? { projectId } : undefined,
    );
    return tokenData.data;
  } catch {
    // expo-notifications no disponible (Expo Go / entorno sin credenciales)
    return null;
  }
}

/**
 * Registra el dispositivo en el backend, opcionalmente siguiendo pozos.
 * Se llama al iniciar sesion y al abrir la app.
 */
export async function registrarPush(pozoIds: string[] = [], userId?: string | null) {
  if (Platform.OS === "web") return;
  const token = await obtenerToken();
  if (!token) return;
  const installation_id = await getInstallationId();
  try {
    await api.post("/push/register", {
      expo_token: token,
      installation_id,
      pozo_ids: pozoIds,
      user_id: userId ?? null,
    });
  } catch {
    // silencioso
  }
}

/** Empieza a seguir un pozo desde la vista publica. */
export async function seguirPozo(pozoId: string): Promise<boolean> {
  if (Platform.OS === "web") return false;
  const token = await obtenerToken();
  const installation_id = await getInstallationId();
  if (!token) return false; // sin permiso no tiene sentido seguir
  try {
    await api.post("/push/register", {
      expo_token: token,
      installation_id,
      pozo_ids: [pozoId],
      user_id: null,
    });
    await api.post("/push/seguir", { installation_id, pozo_id: pozoId });
    return true;
  } catch {
    return false;
  }
}

/** Deja de seguir un pozo. */
export async function dejarPozo(pozoId: string): Promise<void> {
  const installation_id = await getInstallationId();
  try {
    await api.post("/push/dejar", { installation_id, pozo_id: pozoId });
  } catch {
    // silencioso
  }
}

/** Lista de pozos que sigue este dispositivo. */
export async function estadoPozos(): Promise<string[]> {
  const installation_id = await getInstallationId();
  try {
    const res = await api.get("/push/estado", { params: { installation_id } });
    return res.data.pozo_ids || [];
  } catch {
    return [];
  }
}
