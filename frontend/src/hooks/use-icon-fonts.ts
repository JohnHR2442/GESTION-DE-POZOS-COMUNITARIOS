// Icon font loader for Expo apps. Fonts are loaded from a CDN only under
// Expo Go (StoreClient), where bundled .ttf assets can resolve as 0 bytes on
// Android. Native dev/prod builds and web pass an empty map, so useFonts
// resolves to [true, null] immediately and the font bundled with
// @react-native-vector-icons/feather is used.
// FEATHER_VERSION must match @react-native-vector-icons/feather in package.json.
// Usage: const [loaded, error] = useIconFonts();

import Constants, { ExecutionEnvironment } from "expo-constants";
import { useFonts } from "expo-font";

const FEATHER_VERSION = "14.0.0";

const iconFontMap = (): Record<string, string> => ({
  Feather: `https://cdn.jsdelivr.net/npm/@react-native-vector-icons/feather@${FEATHER_VERSION}/fonts/Feather.ttf`,
});

export const useIconFonts = (): readonly [boolean, Error | null] =>
  useFonts(
    Constants.executionEnvironment === ExecutionEnvironment.StoreClient
      ? iconFontMap()
      : {},
  );
