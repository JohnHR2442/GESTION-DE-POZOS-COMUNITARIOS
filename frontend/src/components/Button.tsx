import React from "react";
import { Pressable, Text, ActivityIndicator, StyleSheet, ViewStyle, View } from "react-native";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";
import { useTheme } from "@/src/theme/ThemeContext";
import { spacing, radius, fontSize } from "@/src/theme/colors";

interface Props {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "danger" | "success" | "outline";
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  color?: string;
  testID?: string;
  style?: ViewStyle;
}

export function Button({
  title,
  onPress,
  variant = "primary",
  loading,
  disabled,
  icon,
  color,
  testID,
  style,
}: Props) {
  const { colors } = useTheme();

  const bg = (() => {
    if (color) return color;
    switch (variant) {
      case "secondary": return colors.surfaceTertiary;
      case "danger": return colors.error;
      case "success": return colors.success;
      case "outline": return "transparent";
      default: return colors.brand;
    }
  })();

  const fg = (() => {
    switch (variant) {
      case "secondary": return colors.onSurfaceTertiary;
      case "outline": return colors.brand;
      case "danger": return colors.onError;
      case "success": return colors.onSuccess;
      default: return colors.onBrand;
    }
  })();

  const handlePress = () => {
    if (Platform.OS !== "web") Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => {});
    onPress();
  };

  return (
    <Pressable
      testID={testID}
      onPress={handlePress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.btn,
        {
          backgroundColor: bg,
          opacity: disabled ? 0.5 : pressed ? 0.85 : 1,
          borderWidth: variant === "outline" ? 1.5 : 0,
          borderColor: colors.brand,
        },
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={fg} />
      ) : (
        <View style={styles.content}>
          {icon}
          <Text style={[styles.label, { color: fg }]}>{title}</Text>
        </View>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    minHeight: 56,
    borderRadius: radius.md,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.lg,
  },
  content: { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  label: { fontSize: fontSize.lg, fontWeight: "700" },
});
