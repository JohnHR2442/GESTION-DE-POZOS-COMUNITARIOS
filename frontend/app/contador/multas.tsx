import React, { useState, useEffect, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, TextInput, FlatList } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";
import { api, apiErrorMessage } from "@/src/api/client";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme/ThemeContext";
import { useNotifications } from "@/src/notifications/NotificationsContext";
import { Header } from "@/src/components/Header";
import { AppModal } from "@/src/components/AppModal";
import { Button } from "@/src/components/Button";
import { StatusBadge } from "@/src/components/Badge";
import { Multa } from "@/src/components/MultaDetailModal";
import { formatMXN, formatFecha } from "@/src/utils/format";
import { spacing, radius, fontSize } from "@/src/theme/colors";

interface Socio { id: string; nombre: string; orden: number }

function todayISO() {
  return new Date().toISOString().split("T")[0];
}

export default function ContadorMultas() {
  const { colors } = useTheme();
  const { pozo } = useAuth();
  const { reload: reloadNotif } = useNotifications();
  const insets = useSafeAreaInsets();
  const accent = pozo?.accent || colors.brand;

  const [multas, setMultas] = useState<Multa[]>([]);
  const [socios, setSocios] = useState<Socio[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  // form state
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Multa | null>(null);
  const [socioId, setSocioId] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [monto, setMonto] = useState("");
  const [fecha, setFecha] = useState(todayISO());
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);
  const [socioPicker, setSocioPicker] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Multa | null>(null);

  const load = useCallback(async () => {
    try {
      const [m, s] = await Promise.all([api.get("/multas"), api.get("/socios")]);
      setMultas(m.data);
      setSocios(s.data);
    } catch {
      // silencioso
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => {
    setEditing(null);
    setSocioId("");
    setDescripcion("");
    setMonto("");
    setFecha(todayISO());
    setFormError("");
    setFormOpen(true);
  };

  const openEdit = (m: Multa) => {
    setEditing(m);
    setSocioId(m.socio_id);
    setDescripcion(m.descripcion);
    setMonto(String(m.monto));
    setFecha(m.fecha_creacion);
    setFormError("");
    setFormOpen(true);
  };

  const submit = async () => {
    setFormError("");
    const montoNum = parseFloat(monto);
    if (!socioId || !descripcion.trim() || isNaN(montoNum) || montoNum <= 0) {
      setFormError("Completa socio, descripcion y un monto valido.");
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        await api.patch(`/multas/${editing.id}`, { socio_id: socioId, descripcion, monto: montoNum });
      } else {
        await api.post("/multas", { socio_id: socioId, descripcion, monto: montoNum, fecha_creacion: fecha });
        reloadNotif();
      }
      setFormOpen(false);
      await load();
    } catch (e) {
      setFormError(apiErrorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  const pagar = async (m: Multa) => {
    try {
      await api.post(`/multas/${m.id}/pagar`);
      await load();
    } catch {
      // silencioso
    }
  };

  const confirmarEliminar = async () => {
    if (!deleteTarget) return;
    try {
      await api.delete(`/multas/${deleteTarget.id}`);
      setDeleteTarget(null);
      await load();
    } catch {
      // silencioso
    }
  };

  const socioNombre = socios.find((s) => s.id === socioId)?.nombre;

  const renderMulta = ({ item: m }: { item: Multa }) => {
    const open = expanded === m.id;
    const pagado = m.estado === "pagado";
    return (
      <View style={[styles.card, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}>
        <Pressable onPress={() => setExpanded(open ? null : m.id)} style={styles.cardHead} testID={`multa-card-${m.id}`}>
          <View style={{ flex: 1 }}>
            <Text style={[styles.cardName, { color: colors.onSurface }]}>{m.socio_nombre}</Text>
            <Text style={[styles.cardMeta, { color: colors.muted }]}>{formatMXN(m.monto)} - {formatFecha(m.fecha_creacion)}</Text>
          </View>
          <StatusBadge pagado={pagado} />
          <Feather name={open ? "chevron-up" : "chevron-down"} size={20} color={colors.muted} style={{ marginLeft: spacing.sm }} />
        </Pressable>
        {open ? (
          <View style={[styles.cardBody, { borderTopColor: colors.divider }]}>
            <Text style={[styles.bodyLabel, { color: colors.muted }]}>Descripcion</Text>
            <Text style={[styles.bodyValue, { color: colors.onSurface }]}>{m.descripcion}</Text>
            {pagado ? (
              <>
                <Text style={[styles.bodyLabel, { color: colors.muted, marginTop: spacing.sm }]}>Fecha de pago</Text>
                <Text style={[styles.bodyValue, { color: colors.onSurface }]}>{formatFecha(m.fecha_pago)}</Text>
              </>
            ) : null}
            <View style={styles.actions}>
              {!pagado ? (
                <Button title="Marcar pagada" variant="success" onPress={() => pagar(m)} testID={`pagar-${m.id}`} style={{ flex: 1 }} icon={<Feather name="check" size={18} color="#FFF" />} />
              ) : null}
              <Button title="Editar" variant="secondary" onPress={() => openEdit(m)} testID={`editar-${m.id}`} style={{ flex: 1 }} icon={<Feather name="edit-2" size={16} color={colors.onSurfaceTertiary} />} />
              <Button title="" variant="danger" onPress={() => setDeleteTarget(m)} testID={`eliminar-${m.id}`} style={{ width: 56 }} icon={<Feather name="trash-2" size={18} color="#FFF" />} />
            </View>
          </View>
        ) : null}
      </View>
    );
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Header title="Multas" subtitle={pozo ? `Pozo ${pozo.nombre}` : ""} accent={accent} />
      {loading ? (
        <ActivityIndicator color={accent} style={{ marginTop: spacing.xxl }} />
      ) : multas.length === 0 ? (
        <View style={styles.empty}>
          <Feather name="file-text" size={48} color={colors.muted} />
          <Text style={[styles.emptyText, { color: colors.muted }]}>No hay multas registradas</Text>
        </View>
      ) : (
        <FlatList
          data={multas}
          keyExtractor={(m) => m.id}
          renderItem={renderMulta}
          contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + 96 }}
        />
      )}

      <Pressable onPress={openCreate} testID="fab-nueva-multa" style={[styles.fab, { backgroundColor: accent, bottom: insets.bottom + 20 }]}>
        <Feather name="plus" size={24} color="#FFFFFF" />
        <Text style={styles.fabText}>Nueva multa</Text>
      </Pressable>

      <AppModal visible={formOpen} onClose={() => setFormOpen(false)} title={editing ? "Editar multa" : "Nueva multa"} testID="multa-form-modal">
        <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Socio</Text>
        <Pressable onPress={() => setSocioPicker(true)} testID="select-socio" style={[styles.input, styles.selectRow, { backgroundColor: colors.surfaceTertiary, borderColor: colors.border }]}>
          <Text style={{ color: socioNombre ? colors.onSurface : colors.muted, fontSize: fontSize.lg }}>{socioNombre || "Selecciona un socio"}</Text>
          <Feather name="chevron-down" size={20} color={colors.muted} />
        </Pressable>

        <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Descripcion</Text>
        <TextInput testID="input-descripcion" value={descripcion} onChangeText={setDescripcion} placeholder="Motivo de la multa" placeholderTextColor={colors.muted} style={[styles.input, { backgroundColor: colors.surfaceTertiary, color: colors.onSurface, borderColor: colors.border }]} />

        <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Monto (MXN)</Text>
        <TextInput testID="input-monto" value={monto} onChangeText={setMonto} placeholder="0.00" placeholderTextColor={colors.muted} keyboardType="decimal-pad" style={[styles.input, { backgroundColor: colors.surfaceTertiary, color: colors.onSurface, borderColor: colors.border }]} />

        {!editing ? (
          <>
            <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Fecha (AAAA-MM-DD)</Text>
            <TextInput testID="input-fecha" value={fecha} onChangeText={setFecha} placeholder="2026-01-01" placeholderTextColor={colors.muted} style={[styles.input, { backgroundColor: colors.surfaceTertiary, color: colors.onSurface, borderColor: colors.border }]} />
          </>
        ) : null}

        {formError ? <Text style={[styles.err, { color: colors.error }]} testID="form-error">{formError}</Text> : null}
        <Button title={editing ? "Guardar cambios" : "Crear multa"} testID="btn-save-multa" onPress={submit} loading={saving} color={accent} style={{ marginTop: spacing.md }} />
      </AppModal>

      <AppModal visible={socioPicker} onClose={() => setSocioPicker(false)} title="Selecciona socio" testID="socio-picker-modal">
        {socios.map((s) => (
          <Pressable key={s.id} testID={`socio-opt-${s.orden}`} onPress={() => { setSocioId(s.id); setSocioPicker(false); }} style={[styles.opt, { borderColor: colors.divider }]}>
            <Text style={[styles.optText, { color: colors.onSurface }]}>{s.orden}. {s.nombre}</Text>
            {socioId === s.id ? <Feather name="check" size={20} color={accent} /> : null}
          </Pressable>
        ))}
      </AppModal>

      <AppModal visible={!!deleteTarget} onClose={() => setDeleteTarget(null)} title="Eliminar multa" testID="delete-modal">
        <Text style={{ color: colors.onSurface, fontSize: fontSize.lg, marginBottom: spacing.lg }}>
          Eliminar la multa de {deleteTarget?.socio_nombre} por {deleteTarget ? formatMXN(deleteTarget.monto) : ""}?
        </Text>
        <Button title="Si, eliminar" variant="danger" onPress={confirmarEliminar} testID="btn-confirm-delete" />
        <Button title="Cancelar" variant="secondary" onPress={() => setDeleteTarget(null)} style={{ marginTop: spacing.sm }} />
      </AppModal>
    </View>
  );
}

const styles = StyleSheet.create({
  empty: { flex: 1, alignItems: "center", justifyContent: "center", gap: spacing.md, padding: spacing.xl },
  emptyText: { fontSize: fontSize.lg },
  card: { borderRadius: radius.md, borderWidth: 1, marginBottom: spacing.sm, overflow: "hidden" },
  cardHead: { flexDirection: "row", alignItems: "center", padding: spacing.md, minHeight: 64 },
  cardName: { fontSize: fontSize.lg, fontWeight: "700" },
  cardMeta: { fontSize: fontSize.sm, marginTop: 2 },
  cardBody: { padding: spacing.md, borderTopWidth: 1 },
  bodyLabel: { fontSize: fontSize.sm, fontWeight: "600" },
  bodyValue: { fontSize: fontSize.base, fontWeight: "600", marginTop: 2 },
  actions: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.lg },
  fab: { position: "absolute", right: spacing.lg, flexDirection: "row", alignItems: "center", gap: spacing.sm, paddingHorizontal: spacing.lg, height: 56, borderRadius: radius.pill },
  fabText: { color: "#FFFFFF", fontSize: fontSize.lg, fontWeight: "800" },
  label: { fontSize: fontSize.base, fontWeight: "600", marginTop: spacing.md, marginBottom: spacing.xs },
  input: { minHeight: 56, borderRadius: radius.md, borderWidth: 1, paddingHorizontal: spacing.md, fontSize: fontSize.lg },
  selectRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  err: { fontSize: fontSize.base, fontWeight: "600", marginTop: spacing.md },
  opt: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingVertical: spacing.md, borderBottomWidth: 1 },
  optText: { fontSize: fontSize.lg },
});
