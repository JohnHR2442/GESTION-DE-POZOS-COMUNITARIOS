import React, { useState } from "react";
import {
  View, Text, TextInput, StyleSheet, KeyboardAvoidingView, Platform, ScrollView, Pressable,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { useTheme } from "@/src/theme/ThemeContext";
import { api, apiErrorMessage } from "@/src/api/client";
import { Button } from "@/src/components/Button";
import { spacing, radius, fontSize } from "@/src/theme/colors";

export default function Recuperar() {
  const { colors } = useTheme();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [pass1, setPass1] = useState("");
  const [pass2, setPass2] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const brand = colors.brand;

  const pedirCodigo = async () => {
    setError("");
    if (!email.trim()) { setError("Escribe tu correo."); return; }
    setLoading(true);
    try {
      await api.post("/auth/reset/request", { email: email.trim().toLowerCase() });
      setStep(2);
    } catch (e) {
      setError(apiErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const verificarCodigo = async () => {
    setError("");
    if (code.trim().length !== 6) { setError("El codigo es de 6 digitos."); return; }
    setLoading(true);
    try {
      await api.post("/auth/reset/verify", { email: email.trim().toLowerCase(), code: code.trim() });
      setStep(3);
    } catch (e) {
      setError(apiErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const guardarPassword = async () => {
    setError("");
    if (pass1.length < 6) { setError("La contrasena debe tener al menos 6 caracteres."); return; }
    if (pass1 !== pass2) { setError("Las contrasenas no coinciden."); return; }
    setLoading(true);
    try {
      await api.post("/auth/reset/confirm", { email: email.trim().toLowerCase(), code: code.trim(), new_password: pass1 });
      setStep(4);
    } catch (e) {
      setError(apiErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = [styles.input, { backgroundColor: colors.surfaceSecondary, color: colors.onSurface, borderColor: colors.border }];

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.surface }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={[styles.container, { paddingTop: insets.top + spacing.md, paddingBottom: insets.bottom + spacing.xl }]} keyboardShouldPersistTaps="handled">
        {step !== 4 ? (
          <Pressable onPress={() => (step === 1 ? router.back() : setStep((s) => (s - 1) as any))} style={styles.back} testID="recuperar-back">
            <Feather name="arrow-left" size={24} color={colors.onSurface} />
          </Pressable>
        ) : null}

        <View style={[styles.logo, { backgroundColor: brand }]}>
          <Feather name={step === 4 ? "check" : "lock"} size={32} color="#FFFFFF" />
        </View>
        <Text style={[styles.title, { color: colors.onSurface }]}>Recuperar contrasena</Text>

        <View style={styles.steps}>
          {[1, 2, 3].map((n) => (
            <View key={n} style={[styles.stepDot, { backgroundColor: step >= n ? brand : colors.border }]} />
          ))}
        </View>

        {step === 1 ? (
          <>
            <Text style={[styles.hint, { color: colors.onSurfaceTertiary }]}>
              Escribe el correo de tu cuenta. El codigo se enviara al comisariado, quien te lo dara.
            </Text>
            <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Correo del socio</Text>
            <TextInput testID="reset-email" value={email} onChangeText={setEmail} placeholder="Escribe tu correo" placeholderTextColor={colors.muted} autoCapitalize="none" keyboardType="email-address" style={inputStyle} />
            {error ? <Text style={[styles.error, { color: colors.error }]} testID="reset-error">{error}</Text> : null}
            <Button title="Siguiente" testID="reset-next" onPress={pedirCodigo} loading={loading} style={{ marginTop: spacing.lg }} />
          </>
        ) : null}

        {step === 2 ? (
          <>
            <Text style={[styles.hint, { color: colors.onSurfaceTertiary }]}>
              Introduce el codigo de 6 digitos que te dio el comisariado. Vence en 15 minutos.
            </Text>
            <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Codigo</Text>
            <TextInput testID="reset-code" value={code} onChangeText={(t) => setCode(t.replace(/[^0-9]/g, ""))} placeholder="000000" placeholderTextColor={colors.muted} keyboardType="number-pad" maxLength={6} style={[inputStyle, styles.codeInput]} />
            {error ? <Text style={[styles.error, { color: colors.error }]} testID="reset-error">{error}</Text> : null}
            <Button title="Entrar" testID="reset-verify" onPress={verificarCodigo} loading={loading} style={{ marginTop: spacing.lg }} />
          </>
        ) : null}

        {step === 3 ? (
          <>
            <Text style={[styles.hint, { color: colors.onSurfaceTertiary }]}>Crea tu nueva contrasena.</Text>
            <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Nueva contrasena</Text>
            <TextInput testID="reset-pass1" value={pass1} onChangeText={setPass1} placeholder="Nueva contrasena" placeholderTextColor={colors.muted} secureTextEntry style={inputStyle} />
            <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Confirmar contrasena</Text>
            <TextInput testID="reset-pass2" value={pass2} onChangeText={setPass2} placeholder="Repite la contrasena" placeholderTextColor={colors.muted} secureTextEntry style={inputStyle} />
            {error ? <Text style={[styles.error, { color: colors.error }]} testID="reset-error">{error}</Text> : null}
            <Button title="Guardar contrasena" testID="reset-save" onPress={guardarPassword} loading={loading} variant="success" style={{ marginTop: spacing.lg }} />
          </>
        ) : null}

        {step === 4 ? (
          <>
            <Text style={[styles.hint, { color: colors.onSurfaceTertiary, textAlign: "center" }]}>
              Tu contrasena se actualizo correctamente. Ya puedes iniciar sesion.
            </Text>
            <Button title="Ir a iniciar sesion" testID="reset-done" onPress={() => router.replace("/")} style={{ marginTop: spacing.lg }} />
          </>
        ) : null}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: spacing.xl },
  back: { width: 44, height: 44, justifyContent: "center", marginBottom: spacing.sm },
  logo: { width: 72, height: 72, borderRadius: radius.lg, alignItems: "center", justifyContent: "center", marginBottom: spacing.lg, alignSelf: "flex-start" },
  title: { fontSize: fontSize.xxl, fontWeight: "800" },
  steps: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.md, marginBottom: spacing.lg },
  stepDot: { flex: 1, height: 6, borderRadius: 3 },
  hint: { fontSize: fontSize.base, marginBottom: spacing.md, lineHeight: 20 },
  label: { fontSize: fontSize.base, fontWeight: "600", marginTop: spacing.md, marginBottom: spacing.xs },
  input: { minHeight: 56, borderRadius: radius.md, borderWidth: 1, paddingHorizontal: spacing.md, fontSize: fontSize.lg },
  codeInput: { textAlign: "center", fontSize: fontSize.xxl, letterSpacing: 8, fontWeight: "800" },
  error: { marginTop: spacing.md, fontSize: fontSize.base, fontWeight: "600" },
});
