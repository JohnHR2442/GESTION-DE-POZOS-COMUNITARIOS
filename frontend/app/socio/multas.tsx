import React, { useState, useEffect, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { api } from "@/src/api/client";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { StatusBadge } from "@/src/components/Badge";
import { MultaDetailModal, Multa } from "@/src/components/MultaDetailModal";
import { formatMXN, formatFecha } from "@/src/utils/format";
import { spacing, radius, fontSize } from "@/src/theme/colors";

interface Socio { id: string; nombre: string; orden: number }

export default function SocioMultas() {
  const { colors } = useTheme();
  const { user, pozo } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const accent = pozo?.accent || colors.brand;
  const [socios, setSocios] = useState<Socio[]>([]);
  const [multas, setMultas] = useState<Multa[]>([]);
  const [expanded, setExpanded] = useState<string | null>(user?.id || null);
  const [detail, setDetail] = useState<Multa | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [s, m] = await Promise.all([api.get("/socios"), api.get("/multas")]);
      setSocios(s.data);
      setMultas(m.data);
    } catch {
      // silencioso
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.sm, borderBottomColor: colors.divider, backgroundColor: colors.surface }]}>
        <Pressable onPress={() => router.back()} hitSlop={10} testID="multas-back" style={styles.backBtn}>
          <Feather name="arrow-left" size={24} color={colors.onSurface} />
        </Pressable>
        <Text style={[styles.headerTitle, { color: colors.onSurface }]}>Multas del pozo</Text>
      </View>

      {loading ? (
        <ActivityIndicator color={accent} style={{ marginTop: spacing.xxl }} />
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xl }}>
          {socios.map((s) => {
            const sus = multas.filter((m) => m.socio_id === s.id);
            const open = expanded === s.id;
            const pendientes = sus.filter((m) => m.estado !== "pagado").length;
            return (
              <View key={s.id} style={[styles.accordion, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}>
                <Pressable onPress={() => setExpanded(open ? null : s.id)} style={styles.accHeader} testID={`socio-acc-${s.orden}`}>
                  <View style={[styles.numCircle, { backgroundColor: accent + "22" }]}>
                    <Text style={[styles.num, { color: accent }]}>{s.orden}</Text>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.accName, { color: colors.onSurface }]}>
                      {s.nombre}{s.id === user?.id ? " (tu)" : ""}
                    </Text>
                    <Text style={[styles.accSub, { color: colors.muted }]}>
                      {sus.length} multa{sus.length === 1 ? "" : "s"}{pendientes ? ` - ${pendientes} sin pagar` : ""}
                    </Text>
                  </View>
                  <Feather name={open ? "chevron-up" : "chevron-down"} size={22} color={colors.muted} />
                </Pressable>
                {open ? (
                  <View style={styles.accBody}>
                    {sus.length === 0 ? (
                      <Text style={[styles.noMultas, { color: colors.muted }]}>Sin multas registradas</Text>
                    ) : (
                      sus.map((m) => (
                        <Pressable key={m.id} onPress={() => setDetail(m)} testID={`multa-${m.id}`} style={[styles.multaRow, { borderColor: colors.divider }]}>
                          <View style={{ flex: 1 }}>
                            <Text style={[styles.multaDesc, { color: colors.onSurface }]} numberOfLines={1}>{m.descripcion}</Text>
                            <Text style={[styles.multaMeta, { color: colors.muted }]}>{formatMXN(m.monto)} - {formatFecha(m.fecha_creacion)}</Text>
                          </View>
                          <StatusBadge pagado={m.estado === "pagado"} />
                        </Pressable>
                      ))
                    )}
                  </View>
                ) : null}
              </View>
            );
          })}
        </ScrollView>
      )}

      <MultaDetailModal multa={detail} visible={!!detail} onClose={() => setDetail(null)} />
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.sm, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, borderBottomWidth: 1 },
  backBtn: { width: 40, height: 40, justifyContent: "center" },
  headerTitle: { fontSize: fontSize.xl, fontWeight: "800" },
  accordion: { borderRadius: radius.md, borderWidth: 1, marginBottom: spacing.sm, overflow: "hidden" },
  accHeader: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.md, minHeight: 64 },
  numCircle: { width: 36, height: 36, borderRadius: 18, alignItems: "center", justifyContent: "center" },
  num: { fontSize: fontSize.base, fontWeight: "800" },
  accName: { fontSize: fontSize.lg, fontWeight: "700" },
  accSub: { fontSize: fontSize.sm, marginTop: 2 },
  accBody: { paddingHorizontal: spacing.md, paddingBottom: spacing.md },
  noMultas: { fontSize: fontSize.base, paddingVertical: spacing.sm, fontStyle: "italic" },
  multaRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingVertical: spacing.md, borderTopWidth: 1 },
  multaDesc: { fontSize: fontSize.base, fontWeight: "600" },
  multaMeta: { fontSize: fontSize.sm, marginTop: 2 },
});
