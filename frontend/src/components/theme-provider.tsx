"use client";
import React, { createContext, useContext, useEffect, useState, useCallback } from "react";

type Theme = "light" | "dark";
interface ThemeCtx {
  theme: Theme;
  setTheme: (t: Theme) => void;
  toggle: () => void;
}

const ThemeContext = createContext<ThemeCtx | null>(null);
const STORAGE_KEY = "app-theme";

export const ThemeProvider: React.FC<{ children: React.ReactNode; defaultTheme?: Theme }> = ({ children, defaultTheme = "light" }) => {
  const [theme, setThemeState] = useState<Theme>(defaultTheme);

  // 载入首选项（系统优先）
  useEffect(() => {
    const saved = (typeof window !== 'undefined' && localStorage.getItem(STORAGE_KEY)) as Theme | null;
    if (saved === 'light' || saved === 'dark') {
      setThemeState(saved);
      return;
    }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setThemeState('dark');
    }
  }, []);

  // 应用到 html
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') root.classList.add('dark'); else root.classList.remove('dark');
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const setTheme = useCallback((t: Theme) => setThemeState(t), []);
  const toggle = useCallback(() => setThemeState(t => t === 'dark' ? 'light' : 'dark'), []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
};
