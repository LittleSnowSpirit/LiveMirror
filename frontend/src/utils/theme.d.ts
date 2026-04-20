export type ThemeMode = 'light' | 'dark' | 'system';

export const ThemeMode: {
  LIGHT: 'light';
  DARK: 'dark';
  SYSTEM: 'system';
};

export interface ThemeConfig {
  mode: ThemeMode;
  customColors: Record<string, string>;
}

export function getStoredTheme(): ThemeConfig;
export function saveThemePreference(config: ThemeConfig): void;
export function getCustomColors(): Record<string, string>;
export function saveCustomColors(colors: Record<string, string>): void;
export function getSystemTheme(): ThemeMode;
export function getEffectiveTheme(mode?: ThemeMode): 'light' | 'dark';
export function applyTheme(theme?: ThemeMode): void;
export function applyCustomColors(colors: Record<string, string>): void;
export function watchSystemTheme(callback: (theme: ThemeMode) => void): () => void;
export function resetTheme(): void;
export function exportThemeConfig(): string;
export function importThemeConfig(jsonString: string): boolean;
export function initTheme(): ThemeConfig;
