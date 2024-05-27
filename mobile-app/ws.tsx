import { useState, useEffect } from "react";
import { View, TextInput, Text, StyleSheet } from "react-native";
import AwesomeButton from "react-native-really-awesome-button";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { FontAwesome } from "@expo/vector-icons";
import * as Device from "expo-device";
import * as Updates from "expo-updates";

const bgColor = "#252422";
const cardColor = "#403d39";

export function WS() {
  const [wsAddress, setWsAddress] = useState(`192.168.1.`);
  const [wsPort, setWsPort] = useState(`42069`);
  let getDevice = `${Device.deviceName}`;
  let device = getDevice.replace(/\s+/g, "-");
  const [deviceName, setDeviceName] = useState(device);

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
      <View className="space-x-1 mb-4  border rounded-xl" style={styles.card}>
        <Text className="mx-2 text-lg font-semibold py-1 text-white">
          Enter server's IP
        </Text>
        <TextInput
          className="w-full pl-4 text-lg m-1 bottom-2 text-white"
          placeholder="IP address"
          onChangeText={(text) => setWsAddress(text)}
          value={wsAddress}
        />
        <View className="absolute right-0 mx-2 my-1">
          <AwesomeButton
            backgroundColor="#403d39"
            width={60}
            onPress={handleWsAddressChange}
          >
            <FontAwesome name="save" size={24} color="white" />
          </AwesomeButton>
        </View>
      </View>

      <View className="space-x-1 mb-4 border rounded-xl" style={styles.card}>
        <Text className="mx-2 text-lg font-semibold py-1 text-white">
          Enter server's port
        </Text>
        <TextInput
          className="w-full pl-4 text-lg m-1 bottom-2 text-white"
          placeholder="IP address"
          onChangeText={(text) => setWsPort(text)}
          value={wsPort}
        />
        <View className="absolute right-0 mx-2 my-1">
          <AwesomeButton
            backgroundColor="#403d39"
            width={60}
            onPress={handleWsPortChange}
          >
            <FontAwesome name="save" size={24} color="white" />
          </AwesomeButton>
        </View>
      </View>

      <View className="space-x-1 mb-4 border rounded-xl" style={styles.card}>
        <Text className="mx-2 text-lg font-semibold py-1 text-white">
          Enter device's name
        </Text>
        <TextInput
          className="w-full pl-4 text-lg m-1 bottom-2 text-white"
          placeholder={getDevice}
          onChangeText={(text) => setDeviceName(text)}
          value={deviceName.replace(/-/g, " ")}
        />
        {!deviceName.trim() && (
          <Text className="text-red-500 p-1">Please enter a device name</Text>
        )}
        <View className="absolute right-0 mx-2 my-1">
          <AwesomeButton
            backgroundColor="#403d39"
            width={60}
            onPress={saveDeviceName}
          >
            <FontAwesome name="save" size={24} color="white" />
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
    `ws://${wsAddress}:${wsPort ?? "42069"}/${device ?? "Phone"}`,
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: `${cardColor}`,
  },
  background: {
    backgroundColor: `${bgColor}`,
  },
});
