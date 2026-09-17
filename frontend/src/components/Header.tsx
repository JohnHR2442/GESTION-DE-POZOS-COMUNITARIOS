import React, { useState } from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useTheme } from "@/src/theme/ThemeContext";
import { useNotifications } from "@/src/notifications/NotificationsContext";
import { NotificacionesModal } from "./NotificacionesModal";
import { spacing, fontSize } from "@/src/theme/colors";

interface Props {
  title: string;
  subtitle?: string;
  accent?: string;
  showBell?: boolean;
}

export function Header({ title, subtitle, accent, showBell = true }: Props) {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const { unread } = useNotifications();
  const [open, setOpen] = useState(false);
  const bar = accent || colors.brand;

  return (
    <View style={[styles.wrap, { backgroundColor: colors.surface, paddingTop: insets.top + spacing.sm, borderBottomColor: colors.divider }]}>
      <View style={styles.row}>
        <View style={[styles.accentBar, { backgroundColor: bar }]} />
        <View style={{ flex: 1 }}>
          <Text style={[styles.title, { color: colors.onSurface }]}>{title}</Text>
          {subtitle ? <Text style={[styles.sub, { color: colors.muted }]}>{subtitle}</Text> : null}
        </View>
        {showBell ? (
          <Pressable onPress={() => setOpen(true)} hitSlop={10} testID="notif-bell" style={styles.bell}>
            <Feather name="bell" size={24} color={colors.onSurface} />
            {unread > 0 ? (
              <View style={[styles.badge, { backgroundColor: colors.error }]}>
                <Text style={styles.badgeText}>{unread > 9 ? "9+" : unread}</Text>
              </View>
            ) : null}
          </Pressable>
        ) : null}
      </View>
      <NotificacionesModal visible={open} onClose={() => setOpen(false)} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { paddingHorizontal: spacing.lg, paddingBottom: spacing.md, borderBottomWidth: 1 },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  accentBar: { width: 4, height: 36, borderRadius: 2 },
  title: { fontSize: fontSize.xxl, fontWeight: "800" },
  sub: { fontSize: fontSize.sm, marginTop: 2 },
  bell: { width: 44, height: 44, alignItems: "center", justifyContent: "center" },
  badge: { position: "absolute", top: 6, right: 4, minWidth: 18, height: 18, borderRadius: 9, alignItems: "center", justifyContent: "center", paddingHorizontal: 4 },
  badgeText: { color: "#FFFFFF", fontSize: 10, fontWeight: "800" },
});
