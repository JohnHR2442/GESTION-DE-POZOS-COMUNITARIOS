import React from "react";
import { View, StyleSheet, Platform, useWindowDimensions } from "react-native";
import { useTheme } from "@/src/theme/ThemeContext";

// En web envuelve la app en un marco centrado de 480px que simula un telefono.
// En movil simplemente ocupa toda la pantalla.
export function PhoneFrame({ children }: { children: React.ReactNode }) {
  const { colors } = useTheme();
  const { width } = useWindowDimensions();

  if (Platform.OS !== "web") {
    return <View style={{ flex: 1, backgroundColor: colors.surface }}>{children}</View>;
  }

  const isLarge = width >= 600;

  return (
    <View style={[styles.page, { backgroundColor: isLarge ? colors.pageBackdrop : colors.surface }]}>
      <View
        style={[
          styles.frame,
          {
            backgroundColor: colors.surface,
            maxWidth: 480,
            ...(isLarge
              ? ({ boxShadow: "0 10px 40px rgba(15, 23, 42, 0.25)" } as any)
              : {}),
          },
        ]}
      >
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
    height: "100%" as any,
  },
  frame: {
    flex: 1,
    width: "100%",
    alignSelf: "center",
    overflow: "hidden",
  },
});
