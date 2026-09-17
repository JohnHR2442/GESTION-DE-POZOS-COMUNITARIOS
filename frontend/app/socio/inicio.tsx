import React, { useState, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { useFocusEffect } from "expo-router";
import { api, apiErrorMessage } from "@/src/api/client";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { useNotifications } from "@/src/notifications/NotificationsContext";
import { Header } from "@/src/components/Header";
import { Calendar, DiaCalendario } from "@/src/components/Calendar";
import { AppModal } from "@/src/components/AppModal";
import { Button } from "@/src/components/Button";
import { NotificacionesModal } from "@/src/components/NotificacionesModal";
import { formatFecha, nombreMes, capitalize } from "@/src/utils/format";
import { spacing, radius, fontSize } from "@/src/theme/colors";

const EMERGENCIAS = [
  { tipo: "tuberia", label: "Fuga en tuberia", icon: "git-merge" },
  { tipo: "hidrante", label: "Problema en hidrante", icon: "alert-octagon" },
  { tipo: "presion", label: "Baja presion de agua", icon: "trending-down" },
];

export default function SocioInicio() {
  const { colors } = useTheme();
  const { user, pozo } = useAuth();
  const { reload: reloadNotif } = useNotifications();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const accent = pozo?.accent || colors.brand;

  const now = new Date();
  const [year] = useState(now.getFullYear());
  const [month] = useState(now.getMonth() + 1);
  const [dias, setDias] = useState<DiaCalendario[]>([]);
  const [dssMap, setDssMap] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [showEmergencia, setShowEmergencia] = useState(false);
  const [showRecorrido, setShowRecorrido] = useState(false);
  const [showNotif, setShowNotif] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);
  const [working, setWorking] = useState(false);

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

  const flash = (text: string) => {
    setBanner(text);
    setTimeout(() => setBanner(null), 3500);
  };

  const todayIso = new Date().toISOString().split("T")[0];
  const turnoHoy = dias.find((d) => d.fecha === todayIso);

  const reportarEmergencia = async (tipo: string, label: string) => {
    setWorking(true);
    try {
      await api.post("/emergencias", { tipo });
      setShowEmergencia(false);
      flash(`Emergencia reportada: ${label}`);
      reloadNotif();
    } catch (e) {
      flash(apiErrorMessage(e));
    } finally {
      setWorking(false);
    }
  };

  const toggleSinServicio = async (dia: DiaCalendario) => {
    setWorking(true);
    try {
      if (dssMap[dia.fecha]) {
        await api.delete(`/dias-sin-servicio/${dssMap[dia.fecha]}`);
        flash(`Servicio restablecido el ${formatFecha(dia.fecha)}`);
      } else {
        await api.post("/dias-sin-servicio", { fecha: dia.fecha });
        flash(`Dia sin servicio: ${formatFecha(dia.fecha)}`);
      }
      await load();
      reloadNotif();
    } catch (e) {
      flash(apiErrorMessage(e));
    } finally {
      setWorking(false);
    }
  };

  const actions = [
    { key: "emergencia", label: "Emergencia", icon: "alert-triangle", color: colors.error, onPress: () => setShowEmergencia(true) },
    { key: "recorrido", label: "Recorrido", icon: "map", color: accent, onPress: () => setShowRecorrido(true) },
    { key: "notificaciones", label: "Notificaciones", icon: "bell", color: colors.warning, onPress: () => setShowNotif(true) },
    { key: "multas", label: "Multas", icon: "file-text", color: colors.brand, onPress: () => router.push("/socio/multas") },
  ];

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Header title={`Hola, ${user?.nombre?.split(" ")[0] || ""}`} subtitle={pozo ? `Pozo ${pozo.nombre}` : ""} accent={accent} />
      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xl }}>
        {banner ? (
          <View style={[styles.banner, { backgroundColor: accent }]} testID="inicio-banner">
            <Feather name="check-circle" size={18} color="#FFFFFF" />
            <Text style={styles.bannerText}>{banner}</Text>
          </View>
        ) : null}

        <View style={[styles.turnoCard, { backgroundColor: accent }]} testID="turno-hoy-card">
          <Feather name="droplet" size={28} color="#FFFFFF" />
          <View style={{ flex: 1 }}>
            <Text style={styles.turnoLabel}>Turno de hoy</Text>
            <Text style={styles.turnoName}>
              {turnoHoy?.sin_servicio ? "Sin servicio" : turnoHoy?.socio_nombre || "Sin asignar"}
            </Text>
          </View>
        </View>

        <View style={styles.grid}>
          {actions.map((a) => (
            <Pressable key={a.key} onPress={a.onPress} testID={`action-${a.key}`} style={[styles.actionCard, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}>
              <View style={[styles.actionIcon, { backgroundColor: a.color + "22" }]}>
                <Feather name={a.icon as any} size={24} color={a.color} />
              </View>
              <Text style={[styles.actionLabel, { color: colors.onSurface }]}>{a.label}</Text>
            </Pressable>
          ))}
        </View>

        <Text style={[styles.section, { color: colors.onSurface }]}>{capitalize(nombreMes(month))} {year}</Text>
        {loading ? (
          <ActivityIndicator color={accent} style={{ marginTop: spacing.lg }} />
        ) : (
          <View style={[styles.calCard, { backgroundColor: colors.surfaceSecondary }]}>
            <Calendar dias={dias} accent={accent} highlightSocioId={user?.id} />
            <View style={styles.legend}>
              <Legend color={accent} label="Tu turno" />
              <Legend color={colors.error} label="Sin servicio" />
            </View>
          </View>
        )}
      </ScrollView>

      <AppModal visible={showEmergencia} onClose={() => setShowEmergencia(false)} title="Reportar emergencia" testID="emergencia-modal">
        <Text style={[styles.modalHint, { color: colors.muted }]}>Selecciona el tipo de emergencia. Se notificara a todo el pozo.</Text>
        {EMERGENCIAS.map((e) => (
          <Pressable
            key={e.tipo}
            testID={`emergencia-${e.tipo}`}
            disabled={working}
            onPress={() => reportarEmergencia(e.tipo, e.label)}
            style={[styles.emRow, { backgroundColor: colors.errorSoft }]}
          >
            <Feather name={e.icon as any} size={22} color={colors.error} />
            <Text style={[styles.emLabel, { color: colors.onSurface }]}>{e.label}</Text>
            <Feather name="chevron-right" size={20} color={colors.muted} />
          </Pressable>
        ))}
      </AppModal>

      <AppModal visible={showRecorrido} onClose={() => setShowRecorrido(false)} title="Recorrido del pozo" testID="recorrido-modal">
        <Text style={[styles.modalHint, { color: colors.muted }]}>Toca un dia para marcarlo o quitarlo como dia sin servicio.</Text>
        <Calendar dias={dias} accent={accent} highlightSocioId={user?.id} onDayPress={toggleSinServicio} />
      </AppModal>

      <NotificacionesModal visible={showNotif} onClose={() => setShowNotif(false)} />
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
  turnoCard: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.lg, borderRadius: radius.lg, marginBottom: spacing.lg },
  turnoLabel: { color: "rgba(255,255,255,0.85)", fontSize: fontSize.sm, fontWeight: "600" },
  turnoName: { color: "#FFFFFF", fontSize: fontSize.xl, fontWeight: "800", marginTop: 2 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  actionCard: { width: "47.5%", borderRadius: radius.md, borderWidth: 1, padding: spacing.lg, alignItems: "flex-start", gap: spacing.md, minHeight: 110 },
  actionIcon: { width: 48, height: 48, borderRadius: radius.md, alignItems: "center", justifyContent: "center" },
  actionLabel: { fontSize: fontSize.lg, fontWeight: "700" },
  section: { fontSize: fontSize.lg, fontWeight: "700", marginTop: spacing.xl, marginBottom: spacing.md },
  calCard: { borderRadius: radius.lg, padding: spacing.md },
  legend: { flexDirection: "row", gap: spacing.lg, marginTop: spacing.md, paddingLeft: spacing.xs },
  legendItem: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  legendDot: { width: 12, height: 12, borderRadius: 6 },
  legendText: { fontSize: fontSize.sm },
  modalHint: { fontSize: fontSize.base, marginBottom: spacing.md },
  emRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.lg, borderRadius: radius.md, marginBottom: spacing.sm, minHeight: 56 },
  emLabel: { flex: 1, fontSize: fontSize.lg, fontWeight: "700" },
});
