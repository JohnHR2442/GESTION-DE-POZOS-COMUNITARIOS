// Formato Mexico: montos MXN y fechas DD/MM/YYYY.

export function formatMXN(value: number): string {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    minimumFractionDigits: 2,
  }).format(value || 0);
}

const MESES = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
];

export const MESES_NOMBRES = MESES;

// Acepta "YYYY-MM-DD" o ISO datetime.
export function formatFecha(value?: string | null): string {
  if (!value) return "-";
  const datePart = value.split("T")[0];
  const [y, m, d] = datePart.split("-");
  if (!y || !m || !d) return value;
  return `${d}/${m}/${y}`;
}

export function formatFechaHora(value?: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (isNaN(date.getTime())) return formatFecha(value);
  const dd = String(date.getDate()).padStart(2, "0");
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const yyyy = date.getFullYear();
  const hh = String(date.getHours()).padStart(2, "0");
  const min = String(date.getMinutes()).padStart(2, "0");
  return `${dd}/${mm}/${yyyy} ${hh}:${min}`;
}

export function nombreMes(month: number): string {
  return MESES[month - 1] || "";
}

export function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Lista de meses para el dropdown del historial.
// enero -> 12 meses anteriores; febrero -> 12 anteriores + enero actual;
// marzo en adelante -> meses del ano actual hasta el mes actual.
export function mesesHistorial(): { year: number; month: number; label: string }[] {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1; // 1-12
  const result: { year: number; month: number; label: string }[] = [];

  if (month === 1) {
    for (let m = 12; m >= 1; m--) {
      result.push({ year: year - 1, month: m, label: `${capitalize(MESES[m - 1])} ${year - 1}` });
    }
  } else if (month === 2) {
    result.push({ year, month: 1, label: `${capitalize(MESES[0])} ${year}` });
    for (let m = 12; m >= 1; m--) {
      result.push({ year: year - 1, month: m, label: `${capitalize(MESES[m - 1])} ${year - 1}` });
    }
  } else {
    for (let m = month; m >= 1; m--) {
      result.push({ year, month: m, label: `${capitalize(MESES[m - 1])} ${year}` });
    }
  }
  return result;
}
