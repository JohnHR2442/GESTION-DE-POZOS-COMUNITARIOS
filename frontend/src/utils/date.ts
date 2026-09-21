/**
 * Fecha de HOY en formato ISO (YYYY-MM-DD) usando la hora LOCAL del dispositivo,
 * NO en UTC. Evita que en la noche se marque el dia siguiente.
 */
export function localTodayIso(): string {
  const d = new Date();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}
