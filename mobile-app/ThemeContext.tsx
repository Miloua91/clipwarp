import React, {
  createContext,
  useContext,
  ReactNode,
  useEffect,
  useState,
} from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useColorScheme } from "nativewind";

type Theme = "light" | "dark";

interface ThemeStyles {
  bgColor: string;
  cardBgColor: string;
  cardSelectedBgColor: string;
  textColor: string;
  textSelectedColor: string;
  textNonSelectedColor: string;
}

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  themes: Record<Theme, ThemeStyles>;
}

const darkTheme: ThemeStyles = {
  bgColor: "#252422",
  cardBgColor: "#403d39",
  cardSelectedBgColor: "#c2c2c2",
  textColor: "#ffffff",
  textSelectedColor: "#111827",
  textNonSelectedColor: "#f3f4f6",
};

const lightTheme: ThemeStyles = {
  bgColor: "#ffffff",
  cardBgColor: "#f0f0f0",
  cardSelectedBgColor: "#c2c2c2",
  textColor: "#000000",
  textSelectedColor: "#1f2937",
  textNonSelectedColor: "#4b5563",
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = "user_theme_choice";

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const { colorScheme: systemTheme, toggleColorScheme: systemToggleTheme } =
    useColorScheme();
  const [theme, setTheme] = useState<Theme>(systemTheme as Theme);

  const themes: Record<Theme, ThemeStyles> = {
    light: lightTheme,
    dark: darkTheme,
  };

  useEffect(() => {
    const loadTheme = async () => {
      const storedTheme = await AsyncStorage.getItem(THEME_STORAGE_KEY);
      if (storedTheme) {
        setTheme(storedTheme as Theme);
      }
    };
    loadTheme();
  }, []);

  const toggleTheme = async () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    await AsyncStorage.setItem(THEME_STORAGE_KEY, newTheme);
    systemToggleTheme();
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, themes }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
