import React, { useState, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, useWindowDimensions } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useFocusEffect } from "expo-router";
import { BarChart, PieChart } from "react-native-chart-kit";
import { api } from "@/src/api/client";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { Header } from "@/src/components/Header";
import { formatMXN } from "@/src/utils/format";
import { spacing, radius, fontSize } from "@/src/theme/colors";

export default function Estadisticas() {
  const { colors, isDark } = useTheme();
  const { pozo } = useAuth();
  const insets = useSafeAreaInsets();
  const { width } = useWindowDimensions();
  const accent = pozo?.accent || colors.brand;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const res = await api.get("/estadisticas");
      setData(res.data);
    } catch {
      // silencioso
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const chartWidth = Math.min(width, 480) - spacing.lg * 2 - spacing.md * 2;

  const chartConfig = {
    backgroundGradientFrom: colors.surfaceSecondary,
    backgroundGradientTo: colors.surfaceSecondary,
    decimalPlaces: 0,
    color: (opacity = 1) => (isDark ? `rgba(56,189,248,${opacity})` : `rgba(2,132,199,${opacity})`),
    labelColor: () => colors.muted,
    barPercentage: 0.6,
  };

  const kpis = data
    ? [
        { label: "Mis turnos (ano)", value: String(data.mis_turnos), icon: "calendar", color: accent },
        { label: "Mis multas", value: String(data.mis_multas), icon: "file-text", color: colors.brand },
        { label: "Monto pendiente", value: formatMXN(data.monto_pendiente), icon: "alert-circle", color: colors.error },
        { label: "Monto pagado", value: formatMXN(data.monto_pagado), icon: "check-circle", color: colors.success },
      ]
    : [];

  const pieData = data
    ? [
        { name: "Pagadas", count: data.multas_pagadas, color: colors.success, legendFontColor: colors.muted, legendFontSize: 13 },
        { name: "No pagadas", count: data.multas_no_pagadas, color: colors.error, legendFontColor: colors.muted, legendFontSize: 13 },
      ].filter((d) => d.count > 0)
    : [];

  const topSocios = data ? [...data.por_socio].sort((a, b) => b.multas - a.multas).slice(0, 5) : [];
  const barData = {
    labels: topSocios.map((s: any) => s.nombre.split(" ")[0]),
    datasets: [{ data: topSocios.map((s: any) => s.multas) }],
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Header title="Estadisticas" subtitle={pozo ? `Pozo ${pozo.nombre}` : ""} accent={accent} />
      {loading ? (
        <ActivityIndicator color={accent} style={{ marginTop: spacing.xxl }} />
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xl }}>
          <View style={styles.kpiGrid}>
            {kpis.map((k) => (
              <View key={k.label} style={[styles.kpi, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]} testID={`kpi-${k.icon}`}>
                <Feather name={k.icon as any} size={20} color={k.color} />
                <Text style={[styles.kpiValue, { color: colors.onSurface }]}>{k.value}</Text>
                <Text style={[styles.kpiLabel, { color: colors.muted }]}>{k.label}</Text>
              </View>
            ))}
          </View>

          <Text style={[styles.section, { color: colors.onSurface }]}>Estado de multas del pozo</Text>
          <View style={[styles.card, { backgroundColor: colors.surfaceSecondary }]}>
            {pieData.length ? (
              <PieChart
                data={pieData}
                width={chartWidth}
                height={180}
                chartConfig={chartConfig}
                accessor="count"
                backgroundColor="transparent"
                paddingLeft="8"
              />
            ) : (
              <Text style={[styles.emptyChart, { color: colors.muted }]}>Aun no hay multas registradas</Text>
            )}
          </View>

          <Text style={[styles.section, { color: colors.onSurface }]}>Multas por socio (top 5)</Text>
          <View style={[styles.card, { backgroundColor: colors.surfaceSecondary }]}>
            {topSocios.some((s: any) => s.multas > 0) ? (
              <BarChart
                data={barData}
                width={chartWidth}
                height={220}
                chartConfig={chartConfig}
                fromZero
                showValuesOnTopOfBars
                yAxisLabel=""
                yAxisSuffix=""
                style={{ borderRadius: radius.md }}
              />
            ) : (
              <Text style={[styles.emptyChart, { color: colors.muted }]}>Sin datos para mostrar</Text>
            )}
          </View>

          <View style={[styles.card, { backgroundColor: colors.surfaceSecondary, flexDirection: "row", justifyContent: "space-around" }]}>
            <MiniStat label="Emergencias" value={data?.emergencias ?? 0} color={colors.error} />
            <MiniStat label="Dias sin servicio" value={data?.dias_sin_servicio ?? 0} color={colors.warning} />
            <MiniStat label="Total multas" value={data?.total_multas ?? 0} color={colors.brand} />
          </View>
        </ScrollView>
      )}
    </View>
  );
}

function MiniStat({ label, value, color }: { label: string; value: number; color: string }) {
  const { colors } = useTheme();
  return (
    <View style={{ alignItems: "center" }}>
      <Text style={{ color, fontSize: fontSize.xxl, fontWeight: "800" }}>{value}</Text>
      <Text style={{ color: colors.muted, fontSize: fontSize.sm, marginTop: 2, textAlign: "center" }}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  kpiGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  kpi: { width: "47.5%", borderRadius: radius.md, borderWidth: 1, padding: spacing.lg, gap: spacing.xs },
  kpiValue: { fontSize: fontSize.xl, fontWeight: "800", marginTop: spacing.xs },
  kpiLabel: { fontSize: fontSize.sm },
  section: { fontSize: fontSize.lg, fontWeight: "700", marginTop: spacing.xl, marginBottom: spacing.md },
  card: { borderRadius: radius.lg, padding: spacing.md, alignItems: "center", marginBottom: spacing.md },
  emptyChart: { fontSize: fontSize.base, padding: spacing.xl },
});
