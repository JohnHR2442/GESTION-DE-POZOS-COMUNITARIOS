import React, { useEffect, useState } from "react";
import {
  View, Text, TextInput, StyleSheet, KeyboardAvoidingView, Platform, ScrollView, Pressable,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useAuth, Pozo } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { api, apiErrorMessage } from "@/src/api/client";
import { Button } from "@/src/components/Button";
import { spacing, radius, fontSize } from "@/src/theme/colors";

export default function Login() {
  const { colors } = useTheme();
  const { signIn } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { pozo: pozoId } = useLocalSearchParams<{ pozo: string }>();
  const [pozo, setPozo] = useState<Pozo | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get("/pozos");
        setPozo(res.data.find((p: Pozo) => p.id === pozoId) || null);
      } catch {
        // silencioso
      }
    })();
  }, [pozoId]);

  const accent = pozo?.accent || colors.brand;

  const handleLogin = async () => {
    setError("");
    if (!email.trim() || !password) {
      setError("Ingresa tu correo y contrasena.");
      return;
    }
    setLoading(true);
    try {
      const u = await signIn(email.trim().toLowerCase(), password);
      router.replace(u.rol === "contador" ? "/contador/multas" : "/socio/inicio");
    } catch (e) {
      setError(apiErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.surface }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={[styles.container, { paddingTop: insets.top + spacing.md, paddingBottom: insets.bottom + spacing.xl }]} keyboardShouldPersistTaps="handled">
        <Pressable onPress={() => router.back()} style={styles.back} testID="login-back">
          <Feather name="arrow-left" size={24} color={colors.onSurface} />
        </Pressable>

        <View style={[styles.logo, { backgroundColor: accent }]}>
          <Feather name="droplet" size={36} color="#FFFFFF" />
        </View>
        <Text style={[styles.title, { color: colors.onSurface }]}>Iniciar sesion</Text>
        {pozo ? (
          <View style={[styles.pozoTag, { backgroundColor: accent + "22" }]}>
            <View style={[styles.dot, { backgroundColor: accent }]} />
            <Text style={[styles.pozoText, { color: accent }]}>Pozo {pozo.nombre}</Text>
          </View>
        ) : null}

        <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Correo electronico</Text>
        <TextInput
          testID="input-email"
          value={email}
          onChangeText={setEmail}
          placeholder={pozo ? `correo@${pozo.dominio}` : "tu correo"}
          placeholderTextColor={colors.muted}
          autoCapitalize="none"
          keyboardType="email-address"
          style={[styles.input, { backgroundColor: colors.surfaceSecondary, color: colors.onSurface, borderColor: colors.border }]}
        />

        <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Contrasena</Text>
        <View style={[styles.passRow, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}>
          <TextInput
            testID="input-password"
            value={password}
            onChangeText={setPassword}
            placeholder="pozo2026"
            placeholderTextColor={colors.muted}
            secureTextEntry={!showPass}
            style={[styles.passInput, { color: colors.onSurface }]}
            onSubmitEditing={handleLogin}
          />
          <Pressable onPress={() => setShowPass((s) => !s)} hitSlop={10} testID="toggle-password">
            <Feather name={showPass ? "eye-off" : "eye"} size={20} color={colors.muted} />
          </Pressable>
        </View>

        {error ? <Text style={[styles.error, { color: colors.error }]} testID="login-error">{error}</Text> : null}

        <Button title="Entrar" testID="btn-login" onPress={handleLogin} loading={loading} color={accent} style={{ marginTop: spacing.lg }} />
        <Text style={[styles.hint, { color: colors.muted }]}>Contrasena por defecto: pozo2026</Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: spacing.xl },
  back: { width: 44, height: 44, justifyContent: "center", marginBottom: spacing.sm },
  logo: { width: 72, height: 72, borderRadius: radius.lg, alignItems: "center", justifyContent: "center", marginBottom: spacing.lg, alignSelf: "flex-start" },
  title: { fontSize: fontSize.xxl, fontWeight: "800" },
  pozoTag: { flexDirection: "row", alignItems: "center", gap: spacing.sm, alignSelf: "flex-start", paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: radius.pill, marginTop: spacing.sm },
  dot: { width: 10, height: 10, borderRadius: 5 },
  pozoText: { fontSize: fontSize.base, fontWeight: "700" },
  label: { fontSize: fontSize.base, fontWeight: "600", marginTop: spacing.lg, marginBottom: spacing.xs },
  input: { minHeight: 56, borderRadius: radius.md, borderWidth: 1, paddingHorizontal: spacing.md, fontSize: fontSize.lg },
  passRow: { flexDirection: "row", alignItems: "center", minHeight: 56, borderRadius: radius.md, borderWidth: 1, paddingHorizontal: spacing.md },
  passInput: { flex: 1, fontSize: fontSize.lg },
  error: { marginTop: spacing.md, fontSize: fontSize.base, fontWeight: "600" },
  hint: { textAlign: "center", marginTop: spacing.lg, fontSize: fontSize.sm },
});
