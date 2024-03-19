import { useState, useEffect } from "react";
import { View, TextInput, Text } from "react-native";
import AwesomeButton from "react-native-really-awesome-button";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { FontAwesome } from "@expo/vector-icons";
import * as Device from 'expo-device';

export function WS() {
  const [wsAddress, setWsAddress] = useState(`192.168.1.`);
  let getDevice = `${Device.deviceName}`
  let device = getDevice.replace(/\s+/g, '-');
  const [deviceName, setDeviceName] = useState(device);


  // Load the WebSocket address from AsyncStorage on component mount
  useEffect(() => {
    const loadWsAddress = async () => {
      try {
        const savedAddress = await AsyncStorage.getItem("address");
        if (savedAddress !== null) {
          setWsAddress(savedAddress);
        }
      } catch (error) {
        console.error("Error loading WebSocket address:", error);
      }
    };

    const loadDevice = async () => {
      try {
        const savedDevice = await AsyncStorage.getItem("device");
        if (savedDevice !== null) {
          setDeviceName(savedDevice);
        }
      } catch (error) {
        console.error("Error loading device name:", error);
      }
    };


    loadWsAddress();
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

  const saveDeviceName = async () => {
    if (deviceName !== null) {
      try {
        await AsyncStorage.setItem("device", deviceName);
      } catch (error) {
        console.error("Error saving device name:", error);
      }
    }
  };


  return (
    <>
      <Text className="text-lg font-bold">Enter server's IP</Text>
      <View className="w-full flex flex-row space-x-1 mb-4">
        <TextInput
          className="w-[80%] bg-stone-800 text-gray-100 border rounded-xl pl-4 text-lg font-semibold"
          placeholder="192.168.1.1"
          onChangeText={(text) => setWsAddress(text)}
          value={wsAddress}
        />
        <AwesomeButton
          backgroundColor="white"
          width={60}
          onPress={handleWsAddressChange}
        >
          <FontAwesome name="save" size={24} color="black" />
        </AwesomeButton>
      </View>

      <Text className="text-lg font-bold">Enter device's name</Text>
      <View className="w-full flex flex-row space-x-1">
        <TextInput
          className="w-[80%] bg-stone-800 text-gray-100 border rounded-xl pl-4 text-lg font-semibold"
          placeholder={getDevice}
          onChangeText={(text) => setDeviceName(text)}
          value={deviceName.replace(/-/g, ' ')}
        />
        <AwesomeButton
          backgroundColor="white"
          width={60}
          onPress={saveDeviceName}
        >
          <FontAwesome name="save" size={24} color="black" />
        </AwesomeButton>
      </View>

    </>
  );
}

export const webSocket = async () => {
  const wsAddress = await AsyncStorage.getItem("address");
  const getDevice = await AsyncStorage.getItem("device");
  const device = getDevice?.replace(/\s+/g, '-');
  return new WebSocket(`ws://${wsAddress}:5678/${device}`);
};
