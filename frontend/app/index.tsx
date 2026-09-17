import React, { useEffect, useState } from "react";
import { View, Text, Pressable, StyleSheet, ScrollView, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { useRouter, Redirect } from "expo-router";
import { api } from "@/src/api/client";
import { useAuth, Pozo } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { Button } from "@/src/components/Button";
import { spacing, radius, fontSize } from "@/src/theme/colors";

export default function Landing() {
  const { colors } = useTheme();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [pozos, setPozos] = useState<Pozo[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get("/pozos");
        setPozos(res.data);
      } catch {
        // silencioso
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (!authLoading && user) {
    return <Redirect href={user.rol === "contador" ? "/contador/multas" : "/socio/inicio"} />;
  }

  return (
    <ScrollView
      contentContainerStyle={[styles.container, { paddingTop: insets.top + spacing.xxl, paddingBottom: insets.bottom + spacing.xl }]}
      style={{ backgroundColor: colors.surface }}
    >
      <View style={[styles.logo, { backgroundColor: colors.brand }]}>
        <Feather name="droplet" size={40} color={colors.onBrand} />
      </View>
      <Text style={[styles.title, { color: colors.onSurface }]}>Turnos de Pozo</Text>
      <Text style={[styles.subtitle, { color: colors.muted }]}>
        Gestion de turnos de agua comunitaria
      </Text>

      <Text style={[styles.section, { color: colors.onSurface }]}>Selecciona tu pozo</Text>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xl }} />
      ) : (
        <View style={styles.pozos}>
          {pozos.map((p) => {
            const active = selected === p.id;
            return (
              <Pressable
                key={p.id}
                testID={`pozo-card-${p.id}`}
                onPress={() => setSelected(p.id)}
                style={[
                  styles.pozoCard,
                  {
                    backgroundColor: colors.surfaceSecondary,
                    borderColor: active ? p.accent : colors.border,
                    borderWidth: active ? 3 : 1,
                  },
                ]}
              >
                <View style={[styles.pozoDot, { backgroundColor: p.accent }]} />
                <Text style={[styles.pozoName, { color: colors.onSurface }]}>{p.nombre}</Text>
                {active ? <Feather name="check-circle" size={22} color={p.accent} /> : null}
              </Pressable>
            );
          })}
        </View>
      )}

      <View style={styles.actions}>
        <Button
          title="Iniciar sesion"
          testID="btn-iniciar-sesion"
          disabled={!selected}
          onPress={() => router.push(`/login?pozo=${selected}`)}
          icon={<Feather name="log-in" size={20} color={colors.onBrand} />}
        />
        <Button
          title="Soy usuario (ver turnos)"
          testID="btn-soy-usuario"
          variant="outline"
          disabled={!selected}
          onPress={() => router.push(`/publico/${selected}`)}
          icon={<Feather name="users" size={20} color={colors.brand} />}
        />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: spacing.xl, alignItems: "center" },
  logo: {
    width: 88,
    height: 88,
    borderRadius: radius.lg,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.lg,
  },
  title: { fontSize: fontSize.xxxl, fontWeight: "800" },
  subtitle: { fontSize: fontSize.base, marginTop: spacing.xs, textAlign: "center" },
  section: { fontSize: fontSize.lg, fontWeight: "700", alignSelf: "flex-start", marginTop: spacing.xxl, marginBottom: spacing.md },
  pozos: { width: "100%", gap: spacing.md },
  pozoCard: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: radius.md,
    padding: spacing.lg,
    minHeight: 64,
    gap: spacing.md,
  },
  pozoDot: { width: 16, height: 16, borderRadius: 8 },
  pozoName: { flex: 1, fontSize: fontSize.lg, fontWeight: "700" },
  actions: { width: "100%", gap: spacing.md, marginTop: spacing.xxl },
});
