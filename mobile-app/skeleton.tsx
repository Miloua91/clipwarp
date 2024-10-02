import React, { useCallback, useEffect, useRef } from "react";
import {
  Animated,
  StyleProp,
  ViewStyle,
  View,
  Text,
  Pressable,
  TextInput,
  StyleSheet,
  DimensionValue,
} from "react-native";
import { getLocales } from "expo-localization";
import {
  Entypo,
  FontAwesome6,
  FontAwesome,
  MaterialIcons,
} from "@expo/vector-icons";

const deviceLanguage = getLocales()?.[0]?.languageCode;
const bgColor = "#252422";
const cardColor = "#403d39";

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
  bgColor = "#eee",
  borderRadius = 8,
  style,
}: SkeletonProps) => {
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
    backgroundColor: bgColor,
    borderRadius,
  };

  return <Animated.View style={[style, animatedStyle]} />;
};

export function Skeleton() {
  return (
    <View
      className={`mb-2 w-[97%] py-2 rounded-xl bg-stone-800`}
      style={styles.card}
    >
      <View className="px-2 w-full border-b border-stone-600 my-1 pb-4 flex flex-col">
        <SkeletonLoader width="100%" height={28} />
        <View className="flex items-end mt-2">
          <SkeletonLoader width={200} height={19} />
        </View>
      </View>
      <View className="flex flex-row justify-between py-2 px-3">
        <Pressable className="active:bg-stone-600 w-[2rem] h-9 p-1 rounded">
          <FontAwesome name="clipboard" size={26} color="white" />
        </Pressable>
        <Pressable className="active:bg-stone-600 w-15 h-9 p-1 rounded">
          <Entypo name="share" size={26} color="white" />
        </Pressable>
        <Pressable className="active:bg-stone-600 w-15 h-9 px-1 py-[2px] rounded">
          <MaterialIcons name="open-in-browser" size={32} color="white" />
        </Pressable>
        <Pressable
          className={`active:bg-red-500 w-15 h-9 p-1 rounded ${deviceLanguage === "ar" ? "rotate-180" : ""}`}
        >
          <FontAwesome6 name="delete-left" size={28} color="white" />
        </Pressable>
      </View>
    </View>
  );
}
const styles = StyleSheet.create({
  card: {
    backgroundColor: `${cardColor}`,
  },
  text: {
    textAlign: "right",
  },
});
