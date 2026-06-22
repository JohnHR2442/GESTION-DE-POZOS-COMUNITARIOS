export const lightColors = {
  surface: "#F8FAFC",
  onSurface: "#0F172A",
  surfaceSecondary: "#FFFFFF",
  onSurfaceSecondary: "#0F172A",
  surfaceTertiary: "#F1F5F9",
  onSurfaceTertiary: "#334155",
  surfaceInverse: "#0F172A",
  onSurfaceInverse: "#F8FAFC",
  brand: "#0284C7",
  onBrand: "#FFFFFF",
  brandSoft: "#E0F2FE",
  onBrandSoft: "#0369A1",
  success: "#16A34A",
  onSuccess: "#FFFFFF",
  successSoft: "#DCFCE7",
  warning: "#F59E0B",
  onWarning: "#FFFFFF",
  error: "#DC2626",
  onError: "#FFFFFF",
  errorSoft: "#FEE2E2",
  border: "#E2E8F0",
  borderStrong: "#CBD5E1",
  divider: "#F1F5F9",
  muted: "#94A3B8",
  pageBackdrop: "#E2E8F0",
};

export const darkColors: typeof lightColors = {
  surface: "#0F172A",
  onSurface: "#F1F5F9",
  surfaceSecondary: "#1E293B",
  onSurfaceSecondary: "#F8FAFC",
  surfaceTertiary: "#334155",
  onSurfaceTertiary: "#CBD5E1",
  surfaceInverse: "#F8FAFC",
  onSurfaceInverse: "#0F172A",
  brand: "#38BDF8",
  onBrand: "#082F49",
  brandSoft: "#0C4A6E",
  onBrandSoft: "#38BDF8",
  success: "#22C55E",
  onSuccess: "#052E16",
  successSoft: "#14532D",
  warning: "#FBBF24",
  onWarning: "#451A03",
  error: "#EF4444",
  onError: "#450A0A",
  errorSoft: "#7F1D1D",
  border: "#334155",
  borderStrong: "#475569",
  divider: "#1E293B",
  muted: "#64748B",
  pageBackdrop: "#020617",
};

export const wellAccent: Record<string, { light: string; dark: string }> = {
  isidro: { light: "#0EA5E9", dark: "#38BDF8" },
  zapata: { light: "#10B981", dark: "#34D399" },
  cardenas: { light: "#F59E0B", dark: "#FBBF24" },
};

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, xxxl: 48 };
export const radius = { sm: 6, md: 12, lg: 20, pill: 999 };
export const fontSize = { sm: 12, base: 14, lg: 16, xl: 20, xxl: 24, xxxl: 30 };

export type AppColors = typeof lightColors;
