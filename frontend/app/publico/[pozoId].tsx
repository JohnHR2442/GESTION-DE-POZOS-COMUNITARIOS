import React, { useEffect, useState, useCallback } from "react";
import {
  View, Text, StyleSheet, FlatList, Pressable, RefreshControl, Platform, Linking, ActivityIndicator,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import * as Clipboard from "expo-clipboard";
import { useLocalSearchParams, useRouter } from "expo-router";
import { api } from "@/src/api/client";
import { useTheme } from "@/src/theme/ThemeContext";
import { AppModal } from "@/src/components/AppModal";
import { Button } from "@/src/components/Button";
import { spacing, radius, fontSize } from "@/src/theme/colors";

interface SocioPublico {
  id: string;
  nombre: string;
  telefono: string | null;
  orden: number;
  en_turno: boolean;
}

export default function PublicView() {
  const { colors } = useTheme();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { pozoId } = useLocalSearchParams<{ pozoId: string }>();
  const [socios, setSocios] = useState<SocioPublico[]>([]);
  const [pozoNombre, setPozoNombre] = useState("");
  const [accent, setAccent] = useState(colors.brand);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [callTarget, setCallTarget] = useState<SocioPublico | null>(null);
  const [copied, setCopied] = useState(false);

  const load = useCallback(async () => {
    try {
      const [sociosRes, pozosRes] = await Promise.all([
        api.get(`/pozos/${pozoId}/socios`),
        api.get(`/pozos`),
      ]);
      setSocios(sociosRes.data);
      const p = pozosRes.data.find((x: any) => x.id === pozoId);
      if (p) { setPozoNombre(p.nombre); setAccent(p.accent); }
    } catch {
      // silencioso
    } finally {
      setLoading(false);
    }
  }, [pozoId]);

  useEffect(() => {
    load();
    const t = setInterval(load, 60000);
    return () => clearInterval(t);
  }, [load]);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const handleCall = (s: SocioPublico) => {
    if (!s.telefono) return;
    if (Platform.OS === "web") {
      setCopied(false);
      setCallTarget(s);
    } else {
      Linking.openURL(`tel:${s.telefono}`);
    }
  };

  const copyNumber = async () => {
    if (callTarget?.telefono) {
      await Clipboard.setStringAsync(callTarget.telefono);
      setCopied(true);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { backgroundColor: accent, paddingTop: insets.top + spacing.md }]}>
        <Pressable onPress={() => router.back()} hitSlop={10} testID="public-back">
          <Feather name="arrow-left" size={24} color="#FFFFFF" />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>Pozo {pozoNombre}</Text>
          <Text style={styles.headerSub}>Socios y turno actual</Text>
        </View>
        <Pressable onPress={onRefresh} hitSlop={10} testID="public-refresh">
          <Feather name="refresh-cw" size={20} color="#FFFFFF" />
        </Pressable>
      </View>

      {loading ? (
        <ActivityIndicator color={accent} style={{ marginTop: spacing.xxl }} />
      ) : (
        <FlatList
          data={socios}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xl }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={accent} />}
          renderItem={({ item }) => (
            <View style={[styles.row, { backgroundColor: colors.surfaceSecondary, borderColor: item.en_turno ? colors.success : colors.border, borderWidth: item.en_turno ? 2 : 1 }]} testID={`socio-row-${item.orden}`}>
              <View style={[styles.numCircle, { backgroundColor: accent + "22" }]}>
                <Text style={[styles.num, { color: accent }]}>{item.orden}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={[styles.name, { color: colors.onSurface }]}>{item.nombre}</Text>
                {item.en_turno ? (
                  <View style={[styles.turnoBadge, { backgroundColor: colors.successSoft }]}>
                    <Feather name="droplet" size={12} color={colors.success} />
                    <Text style={[styles.turnoText, { color: colors.success }]}>En turno</Text>
                  </View>
                ) : (
                  <Text style={[styles.inactivo, { color: colors.muted }]}>Inactivo</Text>
                )}
              </View>
              {item.telefono ? (
                <Pressable onPress={() => handleCall(item)} style={[styles.callBtn, { backgroundColor: accent }]} testID={`call-${item.orden}`}>
                  <Feather name="phone" size={18} color="#FFFFFF" />
                </Pressable>
              ) : null}
            </View>
          )}
        />
      )}

      <AppModal visible={!!callTarget} onClose={() => setCallTarget(null)} title="Llamar" testID="call-modal">
        <Text style={[styles.modalName, { color: colors.onSurface }]}>{callTarget?.nombre}</Text>
        <Text style={[styles.modalPhone, { color: colors.brand }]}>{callTarget?.telefono}</Text>
        <Button title={copied ? "Numero copiado" : "Copiar numero"} onPress={copyNumber} variant={copied ? "success" : "primary"} icon={<Feather name={copied ? "check" : "copy"} size={18} color="#FFFFFF" />} style={{ marginTop: spacing.lg }} />
      </AppModal>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.lg },
  headerTitle: { color: "#FFFFFF", fontSize: fontSize.xl, fontWeight: "800" },
  headerSub: { color: "rgba(255,255,255,0.85)", fontSize: fontSize.sm },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.md, borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.sm },
  numCircle: { width: 40, height: 40, borderRadius: 20, alignItems: "center", justifyContent: "center" },
  num: { fontSize: fontSize.lg, fontWeight: "800" },
  name: { fontSize: fontSize.lg, fontWeight: "700" },
  turnoBadge: { flexDirection: "row", alignItems: "center", gap: 4, alignSelf: "flex-start", paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill, marginTop: 4 },
  turnoText: { fontSize: fontSize.sm, fontWeight: "700" },
  inactivo: { fontSize: fontSize.base, marginTop: 4 },
  callBtn: { width: 48, height: 48, borderRadius: 24, alignItems: "center", justifyContent: "center" },
  modalName: { fontSize: fontSize.xl, fontWeight: "700", textAlign: "center" },
  modalPhone: { fontSize: fontSize.xxl, fontWeight: "800", textAlign: "center", marginTop: spacing.sm },
});
