import React, { useState, useEffect, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Feather from "@react-native-vector-icons/feather";
import * as Print from "expo-print";
import { api } from "@/src/api/client";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { Header } from "@/src/components/Header";
import { AppModal } from "@/src/components/AppModal";
import { Button } from "@/src/components/Button";
import { Calendar, DiaCalendario } from "@/src/components/Calendar";
import { mesesHistorial, formatFecha, capitalize, nombreMes } from "@/src/utils/format";
import { spacing, radius, fontSize } from "@/src/theme/colors";

const MESES_OPCIONES = mesesHistorial();
const SEMANA = ["L", "M", "M", "J", "V", "S", "D"];

// Calendario del mes en HTML para el PDF (mismos colores que la pantalla de Inicio)
function calendarioHtml(mes: DiaCalendario[], socioId: string | undefined, accent: string): string {
  if (!mes.length) return "";
  const offset = (new Date(mes[0].fecha + "T00:00:00").getDay() + 6) % 7;
  const celdas: string[] = Array(offset).fill("<td></td>");
  mes.forEach((d) => {
    const verde = d.sin_servicio && d.tipo === "turno_caido";
    const rojo = d.festivo || (d.sin_servicio && d.tipo !== "turno_caido");
    const punto = verde ? "#16A34A" : rojo ? "#DC2626" : d.socio_id === socioId ? accent : "";
    const fondo = d.socio_id === socioId && !verde && !rojo ? "#E0F2FE" : verde ? "#DCFCE7" : rojo ? "#FEE2E2" : "#fff";
    celdas.push(`<td style="background:${fondo}"><div class="n">${d.dia}</div>${punto ? `<div class="dot" style="background:${punto}"></div>` : ""}</td>`);
  });
  while (celdas.length % 7) celdas.push("<td></td>");
  const filas = [];
  for (let i = 0; i < celdas.length; i += 7) filas.push(`<tr>${celdas.slice(i, i + 7).join("")}</tr>`);
  return `
    <h2>Calendario del mes</h2>
    <table class="cal"><thead><tr>${SEMANA.map((s) => `<th>${s}</th>`).join("")}</tr></thead><tbody>${filas.join("")}</tbody></table>
    <p class="ley"><span class="dot" style="background:${accent}"></span> Tu turno
    <span class="dot" style="background:#16A34A"></span> Turno caído
    <span class="dot" style="background:#DC2626"></span> Emergencia / festivo</p>`;
}

export default function Historial() {
  const { colors } = useTheme();
  const { user, pozo } = useAuth();
  const insets = useSafeAreaInsets();
  const accent = pozo?.accent || colors.brand;
  const [sel, setSel] = useState(MESES_OPCIONES[0]);
  const [showPicker, setShowPicker] = useState(false);
  const [dias, setDias] = useState<any[]>([]);
  const [mes, setMes] = useState<DiaCalendario[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { year: sel.year, month: sel.month };
      const [res, cal] = await Promise.all([
        api.get("/historial", { params }),
        api.get("/turnos/calendario", { params }),
      ]);
      setDias(res.data.dias);
      setMes(cal.data.dias);
    } catch {
      // silencioso
    } finally {
      setLoading(false);
    }
  }, [sel]);

  useEffect(() => { load(); }, [load]);

  const exportarPDF = async () => {
    const filas = dias.length
      ? dias.map((d) => `<tr><td>${formatFecha(d.fecha)}</td><td>${d.sin_servicio ? "Sin servicio" : d.festivo ? "Festivo" : "Turno asignado"}</td></tr>`).join("")
      : `<tr><td colspan="2">Sin turnos en este mes</td></tr>`;
    const html = `
      <html><head><meta charset="utf-8" />
      <style>
        body{font-family:Arial,Helvetica,sans-serif;padding:24px;color:#0F172A}
        h1{color:${accent}}
        table{width:100%;border-collapse:collapse;margin-top:16px}
        th,td{border:1px solid #CBD5E1;padding:8px;text-align:left}
        th{background:${accent};color:#fff}
        h2{font-size:16px;margin-top:24px}
        table.cal{table-layout:fixed;page-break-inside:avoid}
        table.cal th,table.cal td{text-align:center;height:46px;padding:4px}
        table.cal th{height:auto}
        .n{font-weight:bold}
        .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-top:4px}
        .ley{font-size:12px;color:#475569}
        .ley .dot{margin:0 4px 0 12px}
      </style></head>
      <body>
        <h1>Turnos de Pozo - ${pozo?.nombre || ""}</h1>
        <p><strong>Socio:</strong> ${user?.nombre || ""}</p>
        <p><strong>Periodo:</strong> ${capitalize(nombreMes(sel.month))} ${sel.year}</p>
        <table><thead><tr><th>Fecha</th><th>Estado</th></tr></thead><tbody>${filas}</tbody></table>
        ${calendarioHtml(mes, user?.id, accent)}
      </body></html>`;
    try {
      await Print.printAsync({ html });
    } catch {
      // usuario cancelo o no disponible
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Header title="Historial" subtitle="Mis turnos por mes" accent={accent} />
      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xl }}>
        <Pressable onPress={() => setShowPicker(true)} testID="month-dropdown" style={[styles.dropdown, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}>
          <Feather name="calendar" size={20} color={accent} />
          <Text style={[styles.dropdownText, { color: colors.onSurface }]}>{sel.label}</Text>
          <Feather name="chevron-down" size={20} color={colors.muted} />
        </Pressable>

        <Button title="Exportar a PDF" testID="btn-export-pdf" onPress={exportarPDF} color={accent} icon={<Feather name="download" size={20} color="#FFFFFF" />} style={{ marginTop: spacing.md }} />

        <Text style={[styles.section, { color: colors.onSurface }]}>
          {loading ? "Cargando..." : `${dias.length} turno${dias.length === 1 ? "" : "s"} en ${sel.label}`}
        </Text>

        {loading ? (
          <ActivityIndicator color={accent} style={{ marginTop: spacing.lg }} />
        ) : dias.length === 0 ? (
          <View style={styles.empty}>
            <Feather name="calendar" size={40} color={colors.muted} />
            <Text style={[styles.emptyText, { color: colors.muted }]}>No tuviste turnos este mes</Text>
          </View>
        ) : (
          dias.map((d) => (
            <View key={d.fecha} style={[styles.dayRow, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]} testID={`hist-${d.fecha}`}>
              <View style={[styles.dayCircle, { backgroundColor: accent }]}>
                <Text style={styles.dayNum}>{d.dia}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={[styles.dayDate, { color: colors.onSurface }]}>{formatFecha(d.fecha)}</Text>
                <Text style={[styles.dayState, { color: d.sin_servicio ? colors.error : d.festivo ? colors.warning : colors.success }]}>
                  {d.sin_servicio ? "Sin servicio" : d.festivo ? "Festivo" : "Turno asignado"}
                </Text>
              </View>
              <Feather name="droplet" size={18} color={accent} />
            </View>
          ))
        )}

        {!loading && mes.length ? (
          <>
            <Text style={[styles.section, { color: colors.onSurface }]}>Calendario de {sel.label}</Text>
            <View style={[styles.calCard, { backgroundColor: colors.surfaceSecondary }]} testID="historial-calendario">
              <Calendar dias={mes} accent={accent} highlightSocioId={user?.id} />
              <View style={styles.legend}>
                <Leyenda color={accent} label="Tu turno" />
                <Leyenda color={colors.success} label="Turno caído" />
                <Leyenda color={colors.error} label="Emergencia / festivo" />
              </View>
            </View>
          </>
        ) : null}
      </ScrollView>

      <AppModal visible={showPicker} onClose={() => setShowPicker(false)} title="Selecciona el mes" testID="month-picker-modal">
        {MESES_OPCIONES.map((m) => (
          <Pressable
            key={`${m.year}-${m.month}`}
            testID={`month-opt-${m.year}-${m.month}`}
            onPress={() => { setSel(m); setShowPicker(false); }}
            style={[styles.opt, { borderColor: colors.divider }]}
          >
            <Text style={[styles.optText, { color: colors.onSurface }]}>{m.label}</Text>
            {sel.year === m.year && sel.month === m.month ? <Feather name="check" size={20} color={accent} /> : null}
          </Pressable>
        ))}
      </AppModal>
    </View>
  );
}

function Leyenda({ color, label }: { color: string; label: string }) {
  const { colors } = useTheme();
  return (
    <View style={styles.legendItem}>
      <View style={[styles.legendDot, { backgroundColor: color }]} />
      <Text style={[styles.legendText, { color: colors.muted }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  calCard: { borderRadius: radius.lg, padding: spacing.md },
  legend: { flexDirection: "row", flexWrap: "wrap", gap: spacing.lg, marginTop: spacing.md, paddingLeft: spacing.xs },
  legendItem: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  legendDot: { width: 12, height: 12, borderRadius: 6 },
  legendText: { fontSize: fontSize.sm },
  dropdown: { flexDirection: "row", alignItems: "center", gap: spacing.md, minHeight: 56, borderRadius: radius.md, borderWidth: 1, paddingHorizontal: spacing.lg },
  dropdownText: { flex: 1, fontSize: fontSize.lg, fontWeight: "700" },
  section: { fontSize: fontSize.lg, fontWeight: "700", marginTop: spacing.xl, marginBottom: spacing.md },
  empty: { alignItems: "center", padding: spacing.xxl, gap: spacing.md },
  emptyText: { fontSize: fontSize.base },
  dayRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, marginBottom: spacing.sm },
  dayCircle: { width: 44, height: 44, borderRadius: 22, alignItems: "center", justifyContent: "center" },
  dayNum: { color: "#FFFFFF", fontSize: fontSize.lg, fontWeight: "800" },
  dayDate: { fontSize: fontSize.lg, fontWeight: "700" },
  dayState: { fontSize: fontSize.sm, fontWeight: "600", marginTop: 2 },
  opt: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingVertical: spacing.md, borderBottomWidth: 1 },
  optText: { fontSize: fontSize.lg },
});
