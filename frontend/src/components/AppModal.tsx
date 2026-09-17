import React from "react";
import { Modal, View, Text, Pressable, StyleSheet, ScrollView } from "react-native";
import { Feather } from "@expo/vector-icons";
import { useTheme } from "@/src/theme/ThemeContext";
import { spacing, radius, fontSize } from "@/src/theme/colors";

interface Props {
  visible: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  testID?: string;
}

export function AppModal({ visible, onClose, title, children, testID }: Props) {
  const { colors } = useTheme();
  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable
          testID={testID}
          style={[styles.card, { backgroundColor: colors.surfaceSecondary }]}
          onPress={(e) => e.stopPropagation()}
        >
          {title ? (
            <View style={styles.header}>
              <Text style={[styles.title, { color: colors.onSurface }]} numberOfLines={2}>
                {title}
              </Text>
              <Pressable onPress={onClose} testID="modal-close" hitSlop={10}>
                <Feather name="x" size={24} color={colors.muted} />
              </Pressable>
            </View>
          ) : null}
          <ScrollView style={{ maxHeight: 480 }} contentContainerStyle={{ padding: spacing.lg }}>
            {children}
          </ScrollView>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: "rgba(2,6,23,0.55)",
    alignItems: "center",
    justifyContent: "center",
    padding: spacing.lg,
  },
  card: { width: "100%", maxWidth: 440, borderRadius: radius.lg, overflow: "hidden" },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: spacing.lg,
    paddingBottom: spacing.sm,
  },
  title: { fontSize: fontSize.xl, fontWeight: "800", flex: 1, paddingRight: spacing.sm },
});
