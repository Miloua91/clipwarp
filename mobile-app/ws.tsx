import { useState, useEffect } from "react";
import { View, TextInput, Text } from "react-native";
import AwesomeButton from "react-native-really-awesome-button";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { FontAwesome } from "@expo/vector-icons";
import * as Device from "expo-device";
import * as Updates from "expo-updates";
import { i18n } from "./i18n";
import { getLocales } from "expo-localization";
import { useTheme } from "./ThemeContext";

const deviceLanguage = getLocales()?.[0]?.languageCode;

export function WS() {
  const [wsAddress, setWsAddress] = useState(`192.168.1.`);
  const [wsPort, setWsPort] = useState(`42069`);
  let getDevice = `${Device.deviceName}`;
  let device = getDevice.replace(/\s+/g, "-");
  const [deviceName, setDeviceName] = useState(device);
  const { theme, themes } = useTheme();
  const { cardBgColor, textColor, bgColor } = themes[theme];
  // Load the WebSocket address from AsyncStorage on component mount
  useEffect(() => {
    const loadWsAddress = async () => {
      try {
        const savedAddress = await AsyncStorage.getItem("address");
        if (savedAddress !== null) {
          setWsAddress(savedAddress);
        } else {
          await AsyncStorage.setItem("address", wsAddress);
        }
      } catch (error) {
        console.error("Error loading WebSocket address:", error);
      }
    };

    const loadWsPort = async () => {
      try {
        const savedPort = await AsyncStorage.getItem("port");
        if (savedPort !== null) {
          setWsPort(savedPort);
        } else {
          await AsyncStorage.setItem("port", wsPort);
        }
      } catch (error) {
        console.error("Error loading WebSocket port:", error);
      }
    };

    const loadDevice = async () => {
      try {
        const savedDevice = await AsyncStorage.getItem("device");
        if (savedDevice !== null) {
          setDeviceName(savedDevice);
        } else {
          await AsyncStorage.setItem("device", deviceName);
        }
      } catch (error) {
        console.error("Error loading device name:", error);
      }
    };

    loadWsAddress();
    loadWsPort();
    loadDevice();
  }, []);

  // Function to handle changing the WebSocket address
  const handleWsAddressChange = async () => {
    // Store the updated WebSocket address in AsyncStorage
    if (wsAddress !== null) {
      try {
        await AsyncStorage.setItem("address", wsAddress);
        await Updates.reloadAsync();
      } catch (error) {
        console.error("Error saving WebSocket address:", error);
      }
    }
  };

  const handleWsPortChange = async () => {
    // Store the updated WebSocket address in AsyncStorage
    if (wsPort !== null) {
      try {
        await AsyncStorage.setItem("port", wsPort);
        await new Promise((resolve) => setTimeout(resolve, 80));
        await Updates.reloadAsync();
      } catch (error) {
        console.error("Error saving WebSocket port:", error);
      }
    }
  };

  const saveDeviceName = async () => {
    if (deviceName !== null && deviceName !== "") {
      try {
        await AsyncStorage.setItem("device", deviceName);
        await new Promise((resolve) => setTimeout(resolve, 80));
        await Updates.reloadAsync();
      } catch (error) {
        console.error("Error saving device name:", error);
      }
    }
  };

  return (
    <View className="w-full m-auto mt-6">
      <View
        className="space-x-1 mb-4 border rounded-xl"
        style={{
          backgroundColor: cardBgColor,
        }}
      >
        <Text
          className="mx-2 text-[16px] font-semibold py-1"
          style={{ color: textColor }}
        >
          {i18n.t("serverIP")}
        </Text>
        <TextInput
          className={`${
            deviceLanguage === "ar" ? "pr-4 text-right" : "pl-4"
          } w-full text-lg m-1 bottom-2`}
          placeholder="IP address"
          onChangeText={(text) => setWsAddress(text)}
          value={wsAddress}
          style={{ color: textColor }}
        />
        <View
          className={`absolute ${
            deviceLanguage === "ar" ? "right-2" : "right-0"
          } mx-2`}
        >
          <AwesomeButton
            backgroundColor={bgColor}
            width={60}
            onPress={handleWsAddressChange}
          >
            <FontAwesome name="save" size={24} color={textColor} />
          </AwesomeButton>
        </View>
      </View>

      <View
        className="space-x-1 mb-4 border rounded-xl"
        style={{
          backgroundColor: cardBgColor,
        }}
      >
        <Text
          className="mx-2 text-[16px] font-semibold py-1"
          style={{ color: textColor }}
        >
          {i18n.t("serverPort")}
        </Text>
        <TextInput
          className={`${
            deviceLanguage === "ar" ? "pr-4 text-right" : "pl-4"
          } w-full text-lg m-1 bottom-2`}
          placeholder="42069"
          onChangeText={(text) => setWsPort(text)}
          value={wsPort}
          style={{ color: textColor }}
        />
        <View
          className={`absolute ${
            deviceLanguage === "ar" ? "right-2" : "right-0"
          } mx-2`}
        >
          <AwesomeButton
            backgroundColor={bgColor}
            width={60}
            onPress={handleWsPortChange}
          >
            <FontAwesome name="save" size={24} color={textColor} />
          </AwesomeButton>
        </View>
      </View>

      <View
        className="space-x-1 mb-4 border rounded-xl"
        style={{
          backgroundColor: cardBgColor,
        }}
      >
        <Text
          className="mx-2 text-[16px] font-semibold py-1"
          style={{ color: textColor }}
        >
          {i18n.t("deviceName")}
        </Text>
        <TextInput
          className={`${
            deviceLanguage === "ar" ? "pr-4 text-right" : "pl-4"
          } w-full text-lg m-1 bottom-2`}
          placeholder={getDevice}
          onChangeText={(text) => setDeviceName(text)}
          value={deviceName.replace(/-/g, " ")}
          style={{ color: textColor }}
        />
        {!deviceName.trim() && (
          <Text className="text-red-500 p-1">{i18n.t("msgDeviceName")}</Text>
        )}
        <View
          className={`absolute ${
            deviceLanguage === "ar" ? "right-2" : "right-0"
          } mx-2`}
        >
          <AwesomeButton
            backgroundColor={bgColor}
            width={60}
            onPress={saveDeviceName}
          >
            <FontAwesome name="save" size={24} color={textColor} />
          </AwesomeButton>
        </View>
      </View>
    </View>
  );
}

export const webSocket = async () => {
  const wsAddress = await AsyncStorage.getItem("address");
  const wsPort = await AsyncStorage.getItem("port");
  const getDevice = await AsyncStorage.getItem("device");
  const device = getDevice?.replace(/\s+/g, "-");
  return new WebSocket(
    `ws://${wsAddress}:${wsPort ?? "42069"}/${device ?? "Phone"}`
  );
};
