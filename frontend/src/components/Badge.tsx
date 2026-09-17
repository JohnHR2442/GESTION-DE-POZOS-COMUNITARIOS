import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { useTheme } from "@/src/theme/ThemeContext";
import { radius, fontSize } from "@/src/theme/colors";

export function StatusBadge({ pagado }: { pagado: boolean }) {
  const { colors } = useTheme();
  const bg = pagado ? colors.successSoft : colors.errorSoft;
  const fg = pagado ? colors.success : colors.error;
  return (
    <View style={[styles.badge, { backgroundColor: bg }]} testID={pagado ? "badge-pagado" : "badge-no-pagado"}>
      <Text style={[styles.text, { color: fg }]}>{pagado ? "Pagado" : "No pagado"}</Text>
    </View>
  );
}

export function Pill({ label, color, bg }: { label: string; color: string; bg: string }) {
  return (
    <View style={[styles.badge, { backgroundColor: bg }]}>
      <Text style={[styles.text, { color }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: radius.pill,
    alignSelf: "flex-start",
  },
  text: { fontSize: fontSize.sm, fontWeight: "700" },
});
