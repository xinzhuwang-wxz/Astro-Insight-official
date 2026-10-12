"use client";
import { Button } from '@/components/ui/button';
import { useTheme } from './theme-provider';
import { Moon, Sun } from 'lucide-react';
import React from 'react';

export const ThemeToggle: React.FC = () => {
  const { theme, toggle } = useTheme();
  return (
    <Button variant="outline" size="icon" aria-label="切换主题" onClick={toggle} className="transition-colors">
      {theme === 'dark' ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </Button>
  );
};
