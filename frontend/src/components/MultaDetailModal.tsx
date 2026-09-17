import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { AppModal } from "./AppModal";
import { StatusBadge } from "./Badge";
import { useTheme } from "@/src/theme/ThemeContext";
import { formatMXN, formatFecha } from "@/src/utils/format";
import { spacing, fontSize } from "@/src/theme/colors";

export interface Multa {
  id: string;
  socio_id: string;
  socio_nombre: string;
  descripcion: string;
  monto: number;
  estado: string;
  fecha_creacion: string;
  fecha_pago: string | null;
}

export function MultaDetailModal({
  multa, visible, onClose,
}: { multa: Multa | null; visible: boolean; onClose: () => void }) {
  const { colors } = useTheme();
  if (!multa) return null;
  const pagado = multa.estado === "pagado";

  const Field = ({ label, value }: { label: string; value: string }) => (
    <View style={styles.field}>
      <Text style={[styles.label, { color: colors.muted }]}>{label}</Text>
      <Text style={[styles.value, { color: colors.onSurface }]}>{value}</Text>
    </View>
  );

  return (
    <AppModal visible={visible} onClose={onClose} title="Detalle de multa" testID="multa-detail-modal">
      <View style={styles.badgeRow}>
        <StatusBadge pagado={pagado} />
      </View>
      <Field label="Socio" value={multa.socio_nombre} />
      <Field label="Descripcion" value={multa.descripcion} />
      <Field label="Monto" value={formatMXN(multa.monto)} />
      <Field label="Fecha de creacion" value={formatFecha(multa.fecha_creacion)} />
      {pagado ? <Field label="Fecha de pago" value={formatFecha(multa.fecha_pago)} /> : null}
    </AppModal>
  );
}

const styles = StyleSheet.create({
  badgeRow: { marginBottom: spacing.md },
  field: { marginBottom: spacing.md },
  label: { fontSize: fontSize.sm, fontWeight: "600", marginBottom: 2 },
  value: { fontSize: fontSize.lg, fontWeight: "600" },
});
