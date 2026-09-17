import React, { useState } from "react";
import { View, Text, StyleSheet, Switch, TextInput, ScrollView } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { apiErrorMessage } from "@/src/api/client";
import { Button } from "./Button";
import { Header } from "./Header";
import { spacing, radius, fontSize } from "@/src/theme/colors";

export function PerfilContent({ accent }: { accent?: string }) {
  const { colors, isDark, toggle } = useTheme();
  const { user, pozo, signOut, changePassword } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [msg, setMsg] = useState<{ type: "ok" | "err"; text: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = async () => {
    setMsg(null);
    if (!current || next.length < 6) {
      setMsg({ type: "err", text: "La nueva contrasena debe tener al menos 6 caracteres." });
      return;
    }
    setLoading(true);
    try {
      await changePassword(current, next);
      setMsg({ type: "ok", text: "Contrasena actualizada correctamente." });
      setCurrent(""); setNext("");
    } catch (e) {
      setMsg({ type: "err", text: apiErrorMessage(e) });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await signOut();
    router.replace("/");
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Header title="Perfil" subtitle={pozo ? `Pozo ${pozo.nombre}` : ""} accent={accent} />
      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + 100 }}>
        <View style={[styles.card, { backgroundColor: colors.surfaceSecondary }]}>
          <View style={[styles.avatar, { backgroundColor: accent || colors.brand }]}>
            <Text style={styles.avatarText}>{user?.nombre?.charAt(0) || "?"}</Text>
          </View>
          <Text style={[styles.name, { color: colors.onSurface }]}>{user?.nombre}</Text>
          <Text style={[styles.email, { color: colors.muted }]}>{user?.email}</Text>
          <View style={[styles.rolePill, { backgroundColor: (accent || colors.brand) + "22" }]}>
            <Text style={[styles.roleText, { color: accent || colors.brand }]}>
              {user?.rol === "contador" ? "Contador" : "Socio"}
            </Text>
          </View>
        </View>

        <View style={[styles.row, { backgroundColor: colors.surfaceSecondary }]}>
          <Feather name="moon" size={20} color={colors.onSurface} />
          <Text style={[styles.rowLabel, { color: colors.onSurface }]}>Modo oscuro</Text>
          <Switch value={isDark} onValueChange={toggle} testID="toggle-dark-mode" />
        </View>

        <Text style={[styles.section, { color: colors.onSurface }]}>Cambiar contrasena</Text>
        <TextInput
          testID="input-current-password"
          value={current}
          onChangeText={setCurrent}
          placeholder="Contrasena actual"
          placeholderTextColor={colors.muted}
          secureTextEntry
          style={[styles.input, { backgroundColor: colors.surfaceSecondary, color: colors.onSurface, borderColor: colors.border }]}
        />
        <TextInput
          testID="input-new-password"
          value={next}
          onChangeText={setNext}
          placeholder="Nueva contrasena"
          placeholderTextColor={colors.muted}
          secureTextEntry
          style={[styles.input, { backgroundColor: colors.surfaceSecondary, color: colors.onSurface, borderColor: colors.border }]}
        />
        {msg ? (
          <Text style={[styles.msg, { color: msg.type === "ok" ? colors.success : colors.error }]} testID="password-msg">
            {msg.text}
          </Text>
        ) : null}
        <Button title="Actualizar contrasena" testID="btn-change-password" onPress={handleChange} loading={loading} color={accent} style={{ marginTop: spacing.md }} />

        <Button
          title="Cerrar sesion"
          testID="btn-logout"
          variant="danger"
          onPress={handleLogout}
          icon={<Feather name="log-out" size={20} color="#FFFFFF" />}
          style={{ marginTop: spacing.xxl }}
        />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { alignItems: "center", padding: spacing.xl, borderRadius: radius.lg, marginBottom: spacing.lg },
  avatar: { width: 72, height: 72, borderRadius: 36, alignItems: "center", justifyContent: "center" },
  avatarText: { color: "#FFFFFF", fontSize: fontSize.xxl, fontWeight: "800" },
  name: { fontSize: fontSize.xl, fontWeight: "800", marginTop: spacing.md },
  email: { fontSize: fontSize.base, marginTop: 2 },
  rolePill: { paddingHorizontal: spacing.md, paddingVertical: 6, borderRadius: radius.pill, marginTop: spacing.sm },
  roleText: { fontSize: fontSize.sm, fontWeight: "700" },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.lg, borderRadius: radius.md, minHeight: 60 },
  rowLabel: { flex: 1, fontSize: fontSize.lg, fontWeight: "600" },
  section: { fontSize: fontSize.lg, fontWeight: "700", marginTop: spacing.xl, marginBottom: spacing.md },
  input: { minHeight: 56, borderRadius: radius.md, borderWidth: 1, paddingHorizontal: spacing.md, fontSize: fontSize.lg, marginBottom: spacing.md },
  msg: { fontSize: fontSize.base, fontWeight: "600", marginBottom: spacing.xs },
});
