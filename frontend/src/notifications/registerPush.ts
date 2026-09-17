import { Platform } from "react-native";
import { api } from "@/src/api/client";

// Registra el token nativo del dispositivo para recibir push (solo movil).
// En web no aplica: ahi se usan la Notification API + polling.
export async function registerForPush(userId: string): Promise<void> {
  if (Platform.OS === "web") return;
  try {
    const Notifications = await import("expo-notifications");
    const { status } = await Notifications.requestPermissionsAsync();
    if (status !== "granted") return;

    const tokenResp = await Notifications.getDevicePushTokenAsync();
    await api.post("/register-push", {
      user_id: userId,
      platform: Platform.OS,
      device_token: tokenResp.data,
    });
  } catch {
    // Sin build nativo (Expo Go) o sin permisos: se ignora silenciosamente.
  }
}
