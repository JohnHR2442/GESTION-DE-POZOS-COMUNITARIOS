import React, { useEffect } from "react";
import { View, Text, StyleSheet, FlatList } from "react-native";
import { Feather } from "@expo/vector-icons";
import { AppModal } from "./AppModal";
import { Button } from "./Button";
import { useTheme } from "@/src/theme/ThemeContext";
import { useNotifications } from "@/src/notifications/NotificationsContext";
import { formatFechaHora } from "@/src/utils/format";
import { spacing, radius, fontSize } from "@/src/theme/colors";

const ICONS: Record<string, any> = {
  emergencia: "alert-triangle",
  sin_servicio: "slash",
  multa: "dollar-sign",
  turno: "clock",
};

export function NotificacionesModal({ visible, onClose }: { visible: boolean; onClose: () => void }) {
  const { colors } = useTheme();
  const { items, markAll, reload, requestWebPermission } = useNotifications();

  useEffect(() => {
    if (visible) {
      reload();
      requestWebPermission();
    }
  }, [visible, reload, requestWebPermission]);

  return (
    <AppModal visible={visible} onClose={onClose} title="Notificaciones" testID="notif-modal">
      {items.length === 0 ? (
        <View style={styles.empty}>
          <Feather name="bell-off" size={40} color={colors.muted} />
          <Text style={[styles.emptyText, { color: colors.muted }]}>No tienes notificaciones</Text>
        </View>
      ) : (
        <>
          <Button title="Marcar todas como leidas" variant="secondary" onPress={markAll} testID="notif-mark-all" style={{ marginBottom: spacing.md }} />
          <FlatList
            data={items}
            scrollEnabled={false}
            keyExtractor={(n) => n.id}
            renderItem={({ item }) => (
              <View style={[styles.item, { backgroundColor: item.leida ? colors.surfaceTertiary : colors.brandSoft }]} testID={`notif-${item.id}`}>
                <Feather name={ICONS[item.tipo] || "bell"} size={20} color={colors.brand} style={{ marginTop: 2 }} />
                <View style={{ flex: 1 }}>
                  <Text style={[styles.itemTitle, { color: colors.onSurface }]}>{item.titulo}</Text>
                  <Text style={[styles.itemMsg, { color: colors.onSurfaceTertiary }]}>{item.mensaje}</Text>
                  <Text style={[styles.itemDate, { color: colors.muted }]}>{formatFechaHora(item.fecha)}</Text>
                </View>
              </View>
            )}
          />
        </>
      )}
    </AppModal>
  );
}

const styles = StyleSheet.create({
  empty: { alignItems: "center", padding: spacing.xl, gap: spacing.md },
  emptyText: { fontSize: fontSize.base },
  item: { flexDirection: "row", gap: spacing.md, padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.sm },
  itemTitle: { fontSize: fontSize.base, fontWeight: "700" },
  itemMsg: { fontSize: fontSize.base, marginTop: 2 },
  itemDate: { fontSize: fontSize.sm, marginTop: 4 },
});
