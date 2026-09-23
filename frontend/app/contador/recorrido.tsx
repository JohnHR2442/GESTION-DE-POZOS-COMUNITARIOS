import React, { useState, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, TextInput } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useFocusEffect } from "expo-router";
import { api, apiErrorMessage } from "@/src/api/client";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { Header } from "@/src/components/Header";
import { Calendar, DiaCalendario } from "@/src/components/Calendar";
import { AppModal } from "@/src/components/AppModal";
import { Button } from "@/src/components/Button";
import { formatFecha, nombreMes, capitalize } from "@/src/utils/format";
import { spacing, radius, fontSize } from "@/src/theme/colors";

export default function ContadorRecorrido() {
  const { colors } = useTheme();
  const { pozo } = useAuth();
  const insets = useSafeAreaInsets();
  const accent = pozo?.accent || colors.brand;
  const now = new Date();
  const [year] = useState(now.getFullYear());
  const [month] = useState(now.getMonth() + 1);
  const [dias, setDias] = useState<DiaCalendario[]>([]);
  const [dssMap, setDssMap] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);

  const [selDia, setSelDia] = useState<DiaCalendario | null>(null);
  const [step, setStep] = useState<"choose" | "confirm">("choose");
  const [tipo, setTipo] = useState<"turno_caido" | "emergencia">("turno_caido");
  const [motivo, setMotivo] = useState("");

  const load = useCallback(async () => {
    try {
      const [cal, dss] = await Promise.all([
        api.get("/turnos/calendario", { params: { year, month } }),
        api.get("/dias-sin-servicio"),
      ]);
      setDias(cal.data.dias);
      const map: Record<string, string> = {};
      dss.data.forEach((d: any) => { map[d.fecha] = d.id; });
      setDssMap(map);
    } catch {
      // silencioso
    } finally {
      setLoading(false);
    }
  }, [year, month]);

  useFocusEffect(useCallback(() => { load(); }, [load]));
  const flash = (t: string) => { setBanner(t); setTimeout(() => setBanner(null), 3500); };

  const openDay = (d: DiaCalendario) => {
    if (d.festivo && !dssMap[d.fecha]) { flash("Ese dia ya es festivo"); return; }
    setSelDia(d); setTipo("turno_caido"); setMotivo(""); setStep("choose");
  };
  const close = () => setSelDia(null);

  const quitar = async () => {
    if (!selDia) return;
    setWorking(true);
    try {
      await api.delete(`/dias-sin-servicio/${dssMap[selDia.fecha]}`);
      flash(`Recorrido quitado el ${formatFecha(selDia.fecha)}`);
      close(); await load();
    } catch (e) { flash(apiErrorMessage(e)); } finally { setWorking(false); }
  };

  const confirmar = async () => {
    if (!selDia) return;
    setWorking(true);
    try {
      await api.post("/dias-sin-servicio", { fecha: selDia.fecha, tipo, motivo: motivo || undefined });
      flash(`Recorrido registrado el ${formatFecha(selDia.fecha)}`);
      close(); await load();
    } catch (e) { flash(apiErrorMessage(e)); } finally { setWorking(false); }
  };

  const yaMarcado = selDia ? !!dssMap[selDia.fecha] : false;
  const tipoColor = tipo === "turno_caido" ? colors.success : colors.error;

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Header title="Recorrido" subtitle={pozo ? `Pozo ${pozo.nombre}` : ""} accent={accent} />
      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xl }}>
        {banner ? (
          <View style={[styles.banner, { backgroundColor: accent }]}>
            <Feather name="check-circle" size={18} color="#FFFFFF" />
            <Text style={styles.bannerText}>{banner}</Text>
          </View>
        ) : null}
        <Text style={[styles.hint, { color: colors.muted }]}>Toca un dia para registrar o quitar un recorrido (dia sin servicio). La rotacion de turnos se recorre automaticamente.</Text>
        <Text style={[styles.section, { color: colors.onSurface }]}>{capitalize(nombreMes(month))} {year}</Text>
        {loading ? (
          <ActivityIndicator color={accent} style={{ marginTop: spacing.lg }} />
        ) : (
          <View style={[styles.calCard, { backgroundColor: colors.surfaceSecondary }]}>
            <Calendar dias={dias} accent={accent} onDayPress={openDay} />
            <View style={styles.legend}>
              <Legend color={colors.success} label="Turno caido" />
              <Legend color={colors.error} label="Emergencia / festivo" />
            </View>
          </View>
        )}
      </ScrollView>

      <AppModal visible={!!selDia} onClose={close} title={selDia ? formatFecha(selDia.fecha) : ""}>
        {yaMarcado ? (
          <>
            <Text style={[styles.hint, { color: colors.muted }]}>Este dia ya tiene un recorrido registrado.</Text>
            <Button title="Quitar recorrido" onPress={quitar} disabled={working} icon={<Feather name="trash-2" size={18} color="#FFFFFF" />} style={{ backgroundColor: colors.error }} />
          </>
        ) : step === "choose" ? (
          <>
            <Text style={[styles.hint, { color: colors.muted }]}>¿Por que es el recorrido?</Text>
            <Pressable testID="tipo-turno-caido" onPress={() => { setTipo("turno_caido"); setStep("confirm"); }} style={[styles.opt, { backgroundColor: colors.success + "22" }]}>
              <Feather name="check-circle" size={22} color={colors.success} />
              <Text style={[styles.optLabel, { color: colors.onSurface }]}>Turno caido</Text>
              <Feather name="chevron-right" size={20} color={colors.muted} />
            </Pressable>
            <Pressable testID="tipo-emergencia" onPress={() => { setTipo("emergencia"); setStep("confirm"); }} style={[styles.opt, { backgroundColor: colors.errorSoft }]}>
              <Feather name="alert-triangle" size={22} color={colors.error} />
              <Text style={[styles.optLabel, { color: colors.onSurface }]}>Emergencia</Text>
              <Feather name="chevron-right" size={20} color={colors.muted} />
            </Pressable>
          </>
        ) : (
          <>
            <Text style={[styles.confirmText, { color: colors.onSurface }]}>
              ¿Seguro que quieres ese dia{" "}
              <Text style={{ color: tipoColor, fontWeight: "800" }}>{selDia ? formatFecha(selDia.fecha) : ""}</Text>?
            </Text>
            {tipo === "emergencia" ? (
              <TextInput
                testID="motivo-input"
                placeholder="Escribe la razon de la emergencia"
                placeholderTextColor={colors.muted}
                value={motivo}
                onChangeText={setMotivo}
                style={[styles.input, { borderColor: colors.border, color: colors.onSurface }]}
                multiline
              />
            ) : null}
            <Button
              title="Confirmar"
              onPress={confirmar}
              disabled={working || (tipo === "emergencia" && !motivo.trim())}
              icon={<Feather name="check" size={18} color="#FFFFFF" />}
              style={{ backgroundColor: tipoColor, marginTop: spacing.md }}
            />
            <Pressable onPress={() => setStep("choose")} style={{ marginTop: spacing.sm, alignItems: "center" }}>
              <Text style={{ color: colors.muted }}>Regresar</Text>
            </Pressable>
          </>
        )}
      </AppModal>
    </View>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  const { colors } = useTheme();
  return (
    <View style={styles.legendItem}>
      <View style={[styles.legendDot, { backgroundColor: color }]} />
      <Text style={[styles.legendText, { color: colors.muted }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: { flexDirection: "row", alignItems: "center", gap: spacing.sm, padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.md },
  bannerText: { color: "#FFFFFF", fontWeight: "700", flex: 1 },
  hint: { fontSize: fontSize.base, marginBottom: spacing.md },
  section: { fontSize: fontSize.lg, fontWeight: "700", marginTop: spacing.sm, marginBottom: spacing.md },
  calCard: { borderRadius: radius.lg, padding: spacing.md },
  legend: { flexDirection: "row", gap: spacing.lg, marginTop: spacing.md, paddingLeft: spacing.xs },
  legendItem: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  legendDot: { width: 12, height: 12, borderRadius: 6 },
  legendText: { fontSize: fontSize.sm },
  opt: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.lg, borderRadius: radius.md, marginBottom: spacing.sm, minHeight: 56 },
  optLabel: { flex: 1, fontSize: fontSize.lg, fontWeight: "700" },
  confirmText: { fontSize: fontSize.lg, marginBottom: spacing.md, lineHeight: 24 },
  input: { borderWidth: 1, borderRadius: radius.md, padding: spacing.md, minHeight: 80, textAlignVertical: "top", fontSize: fontSize.base },
});
