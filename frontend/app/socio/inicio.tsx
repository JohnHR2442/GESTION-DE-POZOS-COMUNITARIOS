import React, { useState, useCallback, useRef } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Feather from "@react-native-vector-icons/feather";
import { useRouter } from "expo-router";
import { useFocusEffect } from "expo-router";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
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
import { localTodayIso } from "@/src/utils/date";
import { spacing, radius, fontSize } from "@/src/theme/colors";

const EMERGENCIAS = [
  { tipo: "tuberia", label: "Fuga en tubería", icon: "git-merge" },
  { tipo: "hidrante", label: "Problema en hidrante", icon: "alert-octagon" },
  { tipo: "presion", label: "Baja presión de agua", icon: "trending-down" },
];

export default function SocioInicio() {
  const { colors } = useTheme();
  const { user, pozo } = useAuth();
  const { reload: reloadNotif } = useNotifications();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const accent = pozo?.accent || colors.brand;

  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [dias, setDias] = useState<DiaCalendario[]>([]);
  const [turnoHoy, setTurnoHoy] = useState<DiaCalendario | undefined>();
  const [seleccionado, setSeleccionado] = useState<DiaCalendario | null>(null);
  const turnoHoyCargado = useRef(false);
  const ultimoPedido = useRef(0);
  const [loading, setLoading] = useState(true);
  const [showEmergencia, setShowEmergencia] = useState(false);
  const [showNotif, setShowNotif] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);
  const [working, setWorking] = useState(false);

  const load = useCallback(async () => {
    const pedido = ++ultimoPedido.current;
    try {
      const cal = await api.get("/turnos/calendario", { params: { year, month } });
      if (pedido !== ultimoPedido.current) return; // llegó una respuesta de un mes anterior
      setDias(cal.data.dias);
      // El turno de hoy siempre se toma del mes actual, aunque se vea otro mes
      const hoyIso = localTodayIso();
      const hoy = (cal.data.dias as DiaCalendario[]).find((d) => d.fecha === hoyIso);
      if (hoy) setTurnoHoy(hoy);
      else if (!turnoHoyCargado.current) {
        const t = new Date();
        const actual = await api.get("/turnos/calendario", { params: { year: t.getFullYear(), month: t.getMonth() + 1 } });
        setTurnoHoy((actual.data.dias as DiaCalendario[]).find((d) => d.fecha === hoyIso));
      }
      turnoHoyCargado.current = true;
    } catch {
      // silencioso
    } finally {
      setLoading(false);
    }
  }, [year, month]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const cambiarMes = useCallback((delta: number) => {
    setSeleccionado(null);
    const total = year * 12 + (month - 1) + delta;
    setYear(Math.floor(total / 12));
    setMonth((total % 12) + 1);
  }, [year, month]);

  // Deslizar a la izquierda = mes siguiente; a la derecha = mes anterior
  const swipe = Gesture.Pan()
    .runOnJS(true)
    .activeOffsetX([-25, 25])
    .failOffsetY([-15, 15])
    .onEnd((e) => {
      if (e.translationX < -50) cambiarMes(1);
      else if (e.translationX > 50) cambiarMes(-1);
    });

  const flash = (text: string) => {
    setBanner(text);
    setTimeout(() => setBanner(null), 3500);
  };


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

  const actions = [
    { key: "emergencia", label: "Emergencia", icon: "alert-triangle", color: colors.error, onPress: () => setShowEmergencia(true) },
    { key: "notificaciones", label: "Notificaciones", icon: "bell", color: colors.warning, onPress: () => setShowNotif(true) },
    { key: "multas", label: "Multas", icon: "file-text", color: colors.brand, onPress: () => router.push("/socio/multas") },
    { key: "agua-sobra", label: "Agua de sobra", icon: "droplet", color: colors.success, onPress: () => router.push("/socio/agua-sobra") },
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

        <View style={styles.monthRow}>
          <Pressable onPress={() => cambiarMes(-1)} testID="mes-anterior" hitSlop={8} style={[styles.monthBtn, { backgroundColor: colors.surfaceSecondary }]}>
            <Feather name="chevron-left" size={22} color={colors.onSurface} />
          </Pressable>
          <Text style={[styles.monthTitle, { color: colors.onSurface }]} testID="mes-titulo">{capitalize(nombreMes(month))} {year}</Text>
          <Pressable onPress={() => cambiarMes(1)} testID="mes-siguiente" hitSlop={8} style={[styles.monthBtn, { backgroundColor: colors.surfaceSecondary }]}>
            <Feather name="chevron-right" size={22} color={colors.onSurface} />
          </Pressable>
        </View>
        {loading ? (
          <ActivityIndicator color={accent} style={{ marginTop: spacing.lg }} />
        ) : (
          <GestureDetector gesture={swipe}>
            <View style={[styles.calCard, { backgroundColor: colors.surfaceSecondary }]} testID="calendario-inicio">
              <Calendar dias={dias} accent={accent} highlightSocioId={user?.id} selectedFecha={seleccionado?.fecha} onDayPress={setSeleccionado} />
              <View style={styles.legend}>
                <Legend color={accent} label="Tu turno" />
                <Legend color={colors.success} label="Turno caído" />
                <Legend color={colors.error} label="Emergencia / festivo" />
              </View>
              <View style={[styles.selBox, { borderColor: colors.border }]} testID="dia-seleccionado">
                {seleccionado ? (
                  <>
                    <Text style={[styles.selFecha, { color: colors.muted }]}>{formatFecha(seleccionado.fecha)}</Text>
                    <Text style={[styles.selNombre, { color: colors.onSurface }]} testID="dia-seleccionado-nombre">
                      {seleccionado.sin_servicio
                        ? `Sin servicio${seleccionado.motivo ? ` (${seleccionado.motivo.replace(/\bcaido\b/gi, (m) => (m[0] === "C" ? "Caído" : "caído"))})` : ""}`
                        : seleccionado.festivo
                          ? "Día festivo"
                          : seleccionado.socio_nombre || "Sin asignar"}
                    </Text>
                  </>
                ) : (
                  <Text style={[styles.selFecha, { color: colors.muted }]}>Toca un día para ver a quién le toca. Desliza para cambiar de mes.</Text>
                )}
              </View>
            </View>
          </GestureDetector>
        )}
      </ScrollView>

      <AppModal visible={showEmergencia} onClose={() => setShowEmergencia(false)} title="Reportar emergencia" testID="emergencia-modal">
        <Text style={[styles.modalHint, { color: colors.muted }]}>Selecciona el tipo de emergencia. Se notificará a todo el pozo.</Text>
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
  monthRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginTop: spacing.xl, marginBottom: spacing.md },
  monthBtn: { width: 44, height: 44, borderRadius: 22, alignItems: "center", justifyContent: "center" },
  monthTitle: { fontSize: fontSize.lg, fontWeight: "700" },
  selBox: { marginTop: spacing.md, paddingTop: spacing.md, paddingHorizontal: spacing.xs, borderTopWidth: 1, minHeight: 56, justifyContent: "center" },
  selFecha: { fontSize: fontSize.sm },
  selNombre: { fontSize: fontSize.lg, fontWeight: "700", marginTop: 2 },
  calCard: { borderRadius: radius.lg, padding: spacing.md },
  legend: { flexDirection: "row", gap: spacing.lg, marginTop: spacing.md, paddingLeft: spacing.xs },
  legendItem: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  legendDot: { width: 12, height: 12, borderRadius: 6 },
  legendText: { fontSize: fontSize.sm },
  modalHint: { fontSize: fontSize.base, marginBottom: spacing.md },
  emRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.lg, borderRadius: radius.md, marginBottom: spacing.sm, minHeight: 56 },
  emLabel: { flex: 1, fontSize: fontSize.lg, fontWeight: "700" },
});
