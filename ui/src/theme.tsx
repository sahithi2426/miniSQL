import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface ThemeColors {
  base: string;
  surface: string;
  elevated: string;
  border: string;
  hi: string;
  mid: string;
  lo: string;
  accent: string;
  accentDim: string;
  red: string;
  green: string;
  val: string;
}

const dark: ThemeColors = {
  base: '#09090b',
  surface: '#0f0f12',
  elevated: '#141418',
  border: '#1c1c22',
  hi: '#f4f4f5',
  mid: '#71717a',
  lo: '#3f3f46',
  accent: '#00d4aa',
  accentDim: 'rgba(0,212,170,0.08)',
  red: '#f87171',
  green: '#4ade80',
  val: '#a1a1aa',
};

const light: ThemeColors = {
  base: '#ffffff',
  surface: '#f8fafb',
  elevated: '#f1f4f7',
  border: '#dfe3e8',
  hi: '#0f172a',
  mid: '#64748b',
  lo: '#94a3b8',
  accent: '#0d9488',
  accentDim: 'rgba(13,148,136,0.06)',
  red: '#dc2626',
  green: '#059669',
  val: '#475569',
};

interface ThemeCtx {
  C: ThemeColors;
  isDark: boolean;
  toggle: () => void;
}

const ThemeContext = createContext<ThemeCtx>({
  C: dark,
  isDark: true,
  toggle: () => {},
});

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('minisql-theme');
    return saved ? saved === 'dark' : true;
  });

  useEffect(() => {
    localStorage.setItem('minisql-theme', isDark ? 'dark' : 'light');

    // update CSS variables for scrollbar / selection / global styles
    const root = document.documentElement;
    const c = isDark ? dark : light;
    root.style.setProperty('--theme-base', c.base);
    root.style.setProperty('--theme-surface', c.surface);
    root.style.setProperty('--theme-border', c.border);
    root.style.setProperty('--theme-hi', c.hi);
    root.style.setProperty('--theme-mid', c.mid);
    root.style.setProperty('--theme-lo', c.lo);
    root.style.setProperty('--theme-accent', c.accent);
    root.style.setProperty('--theme-val', c.val);
    root.style.setProperty('--theme-elevated', c.elevated);

    // set body background + color
    document.body.style.backgroundColor = c.base;
    document.body.style.color = c.hi;
    const rootEl = document.getElementById('root');
    if (rootEl) {
      rootEl.style.backgroundColor = c.base;
      rootEl.style.color = c.hi;
    }
  }, [isDark]);

  return (
    <ThemeContext.Provider value={{ C: isDark ? dark : light, isDark, toggle: () => setIsDark(p => !p) }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
