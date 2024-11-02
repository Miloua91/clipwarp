import React, { useCallback, useEffect, useRef } from "react";
import "./global.css";
import {
  Animated,
  StyleProp,
  ViewStyle,
  View,
  Pressable,
  DimensionValue,
} from "react-native";
import { getLocales } from "expo-localization";
import {
  Entypo,
  FontAwesome6,
  Feather,
  MaterialIcons,
} from "@expo/vector-icons";
import { useTheme } from "./ThemeContext";

const deviceLanguage = getLocales()?.[0]?.languageCode;

type SkeletonProps = {
  width: DimensionValue;
  height: DimensionValue;
  borderRadius?: number;
  bgColor?: string;
  style?: StyleProp<ViewStyle>;
};

export const SkeletonLoader = ({
  width,
  height,
  borderRadius = 8,
  style,
}: SkeletonProps) => {
  const { theme, themes } = useTheme();
  const { cardSelectedBgColor } = themes[theme];

  const animation = useRef(new Animated.Value(0.5)).current;

  const startAnimation = useCallback(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(animation, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(animation, {
          toValue: 0.5,
          duration: 1000,
          useNativeDriver: true,
        }),
      ]),
    ).start();
  }, [animation]);

  useEffect(() => {
    startAnimation();
  }, [startAnimation]);

  const animatedStyle = {
    opacity: animation,
    width,
    height,
    backgroundColor: cardSelectedBgColor,
    borderRadius,
  };

  return <Animated.View style={[style, animatedStyle]} />;
};

export function Skeleton() {
  const { theme, themes } = useTheme();
  const { cardBgColor, textColor } = themes[theme];
  return (
    <View
      className={`mb-2 w-[97%] py-2 rounded-xl bg-stone-800`}
      style={{ backgroundColor: cardBgColor }}
    >
      <View className="px-2 w-full border-b border-stone-600 my-1 pb-2 flex flex-col">
        <SkeletonLoader width="100%" height={21.5} />
        <View className="flex items-end mt-2">
          <SkeletonLoader width={200} height={19.3} />
        </View>
      </View>
      <View className="flex flex-row justify-between py-2 px-3">
        <Pressable
          className={`${theme === "light" ? "active:bg-stone-300" : "active:bg-stone-600"} h-10 w-10 justify-center items-center rounded`}
        >
          <Feather name="copy" size={26} color={textColor} />
        </Pressable>
        <Pressable
          className={`${theme === "light" ? "active:bg-stone-300" : "active:bg-stone-600"} h-10 w-10 justify-center items-center rounded`}
        >
          <Entypo name="share" size={26} color={textColor} />
        </Pressable>
        <Pressable
          className={`${theme === "light" ? "active:bg-stone-300" : "active:bg-stone-600"} h-10 w-10 justify-center items-center rounded`}
        >
          <MaterialIcons name="open-in-browser" size={32} color={textColor} />
        </Pressable>
        <Pressable
          className={`${theme === "light" ? "active:bg-red-400" : "active:bg-red-500"} h-10 w-12 justify-center items-center rounded ${
            deviceLanguage === "ar" ? "rotate-180" : ""
          }`}
        >
          <FontAwesome6 name="delete-left" size={26} color={textColor} />
        </Pressable>
      </View>
    </View>
  );
}
