import { useState, useEffect } from "react";
import { View, TextInput, Text } from "react-native";
import AwesomeButton from "react-native-really-awesome-button";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { FontAwesome } from "@expo/vector-icons";

export function WS() {
  const [wsAddress, setWsAddress] = useState(`192.168.1.`);

  // Load the WebSocket address from AsyncStorage on component mount
  useEffect(() => {
    const loadWsAddress = async () => {
      try {
        const savedAddress = await AsyncStorage.getItem("address");
        if (savedAddress !== null) {
          setWsAddress(savedAddress);
          console.log(savedAddress);
        }
      } catch (error) {
        console.error("Error loading WebSocket address:", error);
      }
    };

    loadWsAddress();
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

  return (
    <>
      <Text className="text-lg font-bold">Enter server's IP</Text>
      <View className="w-full flex flex-row space-x-1">
        <TextInput
          className="w-fit border-2 rounded pl-4 text-lg font-semibold"
          placeholder="Enter WebSocket address"
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
    </>
  );
}

export const webSocket = async () => {
  const wsAddress = await AsyncStorage.getItem("address");
  return new WebSocket(`ws://${wsAddress}:5678/69`);
};
