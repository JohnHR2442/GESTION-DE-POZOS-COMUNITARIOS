import React from "react";
import { View, Text, Pressable, StyleSheet, Platform } from "react-native";
import * as Haptics from "expo-haptics";
import { useTheme } from "@/src/theme/ThemeContext";
import { spacing, radius, fontSize } from "@/src/theme/colors";

export interface DiaCalendario {
  fecha: string;
  dia: number;
  socio_id?: string | null;
  socio_nombre?: string | null;
  festivo?: boolean;
  sin_servicio?: boolean;
  motivo?: string | null;
}

interface Props {
  dias: DiaCalendario[];
  accent: string;
  highlightSocioId?: string | null;
  onDayPress?: (dia: DiaCalendario) => void;
}

const WEEKDAYS = ["L", "M", "M", "J", "V", "S", "D"];

// Convierte 0=Domingo..6=Sabado a indice con semana iniciando Lunes.
function mondayIndex(jsDay: number): number {
  return (jsDay + 6) % 7;
}

export function Calendar({ dias, accent, highlightSocioId, onDayPress }: Props) {
  const { colors } = useTheme();
  if (!dias.length) return null;

  const first = new Date(dias[0].fecha + "T00:00:00");
  const offset = mondayIndex(first.getDay());
  const todayIso = new Date().toISOString().split("T")[0];

  const cells: (DiaCalendario | null)[] = [];
  for (let i = 0; i < offset; i++) cells.push(null);
  dias.forEach((d) => cells.push(d));

  const press = (d: DiaCalendario) => {
    if (Platform.OS !== "web") Haptics.selectionAsync().catch(() => {});
    onDayPress?.(d);
  };

  return (
    <View>
      <View style={styles.weekRow}>
        {WEEKDAYS.map((w, i) => (
          <View key={i} style={styles.weekCell}>
            <Text style={[styles.weekText, { color: colors.muted }]}>{w}</Text>
          </View>
        ))}
      </View>
      <View style={styles.grid}>
        {cells.map((d, i) => {
          if (!d) return <View key={`e${i}`} style={styles.cell} />;
          const isMine = highlightSocioId && d.socio_id === highlightSocioId;
          const isToday = d.fecha === todayIso;
          const bg = d.sin_servicio
            ? colors.errorSoft
            : d.festivo
            ? colors.surfaceTertiary
            : isMine
            ? accent
            : colors.surfaceSecondary;
          const fg = isMine && !d.sin_servicio && !d.festivo ? "#FFFFFF" : colors.onSurface;
          return (
            <Pressable
              key={d.fecha}
              testID={`dia-${d.fecha}`}
              onPress={() => press(d)}
              style={[
                styles.cell,
                styles.dayCell,
                {
                  backgroundColor: bg,
                  borderColor: isToday ? accent : colors.border,
                  borderWidth: isToday ? 2 : 1,
                },
              ]}
            >
              <Text style={[styles.dayNum, { color: fg }]}>{d.dia}</Text>
              {d.sin_servicio ? (
                <View style={[styles.dot, { backgroundColor: colors.error }]} />
              ) : !isMine && d.socio_nombre ? (
                <View style={[styles.dot, { backgroundColor: accent }]} />
              ) : null}
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  weekRow: { flexDirection: "row", marginBottom: spacing.xs },
  weekCell: { flex: 1, alignItems: "center", paddingVertical: spacing.xs },
  weekText: { fontSize: fontSize.sm, fontWeight: "700" },
  grid: { flexDirection: "row", flexWrap: "wrap" },
  cell: { width: `${100 / 7}%`, aspectRatio: 1, padding: 2 },
  dayCell: {
    borderRadius: radius.sm,
    alignItems: "center",
    justifyContent: "center",
  },
  dayNum: { fontSize: fontSize.base, fontWeight: "600" },
  dot: { width: 6, height: 6, borderRadius: 3, marginTop: 3 },
});
