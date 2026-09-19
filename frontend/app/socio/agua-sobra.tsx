import React, { useState, useEffect, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { api } from "@/src/api/client";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { useNotifications } from "@/src/notifications/NotificationsContext";
import { AppModal } from "@/src/components/AppModal";
import { Button } from "@/src/components/Button";
import { spacing, radius, fontSize } from "@/src/theme/colors";

type Step = "menu" | "confirm" | "done";
type Tipo = "add" | "remove";

export default function AguaSobra() {
  const { colors } = useTheme();
  const { pozo } = useAuth();
  const { reload: reloadNotif } = useNotifications();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const accent = pozo?.accent || colors.brand;

  const [horasActuales, setHorasActuales] = useState(0);
  const [step, setStep] = useState<Step>("menu");
  const [confirm, setConfirm] = useState<{ tipo: Tipo; horas: number } | null>(null);
  const [pickerFor, setPickerFor] = useState<Tipo | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    try {
      const res = await api.get("/agua-sobra/mias");
      setHorasActuales(res.data.horas_sobra);
    } catch {
      // silencioso
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const opciones = (max: number) => Array.from({ length: max }, (_, i) => i + 1);

  const elegir = (tipo: Tipo, horas: number) => {
    setPickerFor(null);
    setConfirm({ tipo, horas });
    setStep("confirm");
  };

  const confirmar = async () => {
    if (!confirm) return;
    setSaving(true);
    try {
      const url = confirm.tipo === "add" ? "/agua-sobra/agregar" : "/agua-sobra/quitar";
      await api.post(url, { horas: confirm.horas });
      if (confirm.tipo === "add") reloadNotif();
      setStep("done");
    } catch {
      // silencioso
    } finally {
      setSaving(false);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.sm, borderBottomColor: colors.divider }]}>
        <Pressable onPress={() => router.back()} hitSlop={10} testID="agua-back" style={styles.backBtn}>
          <Feather name="arrow-left" size={24} color={colors.onSurface} />
        </Pressable>
        <Text style={[styles.headerTitle, { color: colors.onSurface }]}>Agua de sobra</Text>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xl }}>
        {step === "menu" ? (
          <>
            <View style={[styles.iconWrap, { backgroundColor: accent }]}>
              <Feather name="droplet" size={32} color="#FFFFFF" />
            </View>

            <Text style={[styles.question, { color: colors.onSurface }]}>¿Cuantas horas te sobran?</Text>
            <Pressable onPress={() => setPickerFor("add")} testID="combo-agregar" style={[styles.combo, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}>
              <Text style={[styles.comboText, { color: colors.muted }]}>Selecciona las horas</Text>
              <Feather name="chevron-down" size={22} color={colors.muted} />
            </Pressable>

            <View style={[styles.divider, { backgroundColor: colors.divider }]} />

            <Text style={[styles.question, { color: colors.onSurface }]}>Quitar horas de sobra</Text>
            {horasActuales > 0 ? (
              <>
                <Text style={[styles.actual, { color: colors.muted }]}>Tienes {horasActuales} hora{horasActuales === 1 ? "" : "s"} de sobra</Text>
                <Pressable onPress={() => setPickerFor("remove")} testID="combo-quitar" style={[styles.combo, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}>
                  <Text style={[styles.comboText, { color: colors.muted }]}>Selecciona las horas a quitar</Text>
                  <Feather name="chevron-down" size={22} color={colors.muted} />
                </Pressable>
              </>
            ) : (
              <Text style={[styles.actual, { color: colors.muted }]}>No tienes horas de sobra registradas.</Text>
            )}
          </>
        ) : null}

        {step === "confirm" && confirm ? (
          <View style={styles.centerBlock}>
            <Text style={[styles.confirmMsg, { color: colors.onSurface }]}>
              {confirm.tipo === "add" ? "¿Estas seguro que te sobran " : "¿Estas seguro de las horas que ya no te sobran "}
              <Text style={{ color: colors.error, fontWeight: "800" }}>{confirm.horas} hora{confirm.horas === 1 ? "" : "s"}</Text>
              ?
            </Text>
            <Button title="Seguro" testID="btn-seguro" onPress={confirmar} loading={saving} color={accent} style={{ marginTop: spacing.xl, width: "100%" }} />
            <Button title="Cancelar" variant="secondary" onPress={() => { setConfirm(null); setStep("menu"); }} style={{ marginTop: spacing.sm, width: "100%" }} />
          </View>
        ) : null}

        {step === "done" ? (
          <View style={styles.centerBlock}>
            <View style={[styles.iconWrap, { backgroundColor: colors.success }]}>
              <Feather name="check" size={40} color="#FFFFFF" />
            </View>
            <Text style={[styles.listo, { color: colors.onSurface }]}>Listo</Text>
            <Button title="OK" testID="btn-ok" onPress={() => router.replace("/socio/inicio")} color={accent} style={{ marginTop: spacing.xl, width: "100%" }} />
          </View>
        ) : null}
      </ScrollView>

      <AppModal visible={pickerFor !== null} onClose={() => setPickerFor(null)} title="Selecciona las horas" testID="horas-picker">
        {opciones(pickerFor === "remove" ? horasActuales : 24).map((h) => (
          <Pressable key={h} testID={`hora-${h}`} onPress={() => elegir(pickerFor!, h)} style={[styles.opt, { borderColor: colors.divider }]}>
            <Text style={[styles.optText, { color: colors.onSurface }]}>{h} hora{h === 1 ? "" : "s"}</Text>
            <Feather name="chevron-right" size={20} color={colors.muted} />
          </Pressable>
        ))}
      </AppModal>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.sm, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, borderBottomWidth: 1 },
  backBtn: { width: 40, height: 40, justifyContent: "center" },
  headerTitle: { fontSize: fontSize.xl, fontWeight: "800" },
  iconWrap: { width: 72, height: 72, borderRadius: radius.lg, alignItems: "center", justifyContent: "center", alignSelf: "center", marginVertical: spacing.lg },
  question: { fontSize: fontSize.xl, fontWeight: "800", marginBottom: spacing.md },
  combo: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", minHeight: 56, borderRadius: radius.md, borderWidth: 1, paddingHorizontal: spacing.lg },
  comboText: { fontSize: fontSize.lg },
  divider: { height: 1, marginVertical: spacing.xl },
  actual: { fontSize: fontSize.base, marginBottom: spacing.md },
  centerBlock: { alignItems: "center", paddingTop: spacing.xxl },
  confirmMsg: { fontSize: fontSize.xl, fontWeight: "700", textAlign: "center", lineHeight: 30 },
  listo: { fontSize: 40, fontWeight: "800", marginTop: spacing.lg },
  opt: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingVertical: spacing.md, borderBottomWidth: 1 },
  optText: { fontSize: fontSize.lg, fontWeight: "600" },
});
