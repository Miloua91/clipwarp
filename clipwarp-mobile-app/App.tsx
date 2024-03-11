import { StatusBar } from "expo-status-bar";
import {
  StyleSheet,
  Alert,
  View,
  Text,
  TextInput,
  ScrollView,
  Modal,
  ToastAndroid,
} from "react-native";
import * as Clipboard from "expo-clipboard";
import * as SQLite from "expo-sqlite";
import { ThemedButton } from "react-native-really-awesome-button";
import AwesomeButton from "react-native-really-awesome-button";
import { Octicons } from "@expo/vector-icons";
import { FontAwesome } from "@expo/vector-icons";
import { Ionicons } from "@expo/vector-icons";
import React, { useEffect, useState } from "react";
import { webSocket, WS } from "./ws";

type Clip = {
  id: number | undefined;
  clip: string;
};

export default function App() {
  const [db, setDb] = useState(SQLite.openDatabase("1.db")); // SQLite database to save clipboard
  const [serverVal, setServerVal] = useState<string>("");
  const [val, setVal] = useState<Clip[]>([]); // Clips are saved here
  const [currentVal, setCurrentVal] = useState<string | undefined>(undefined); // Text input value
  const [setting, setSetting] = useState<boolean>(false);

  useEffect(() => {
    // Send data when `db` changes
    const ws = async () => {
      const websocket = await webSocket();
      websocket.onopen = () => {
        const lastValue: string = val[val.length - 1].clip;
        websocket.send(lastValue);
      };

      websocket.onerror = (error: Event) => {
        const webSocketError = error as WebSocketErrorEvent;
        Alert.alert("WebSocket Status", webSocketError.message, [
          {
            text: "OK",
          },
        ]);
      };
      console.log(websocket.url);
      websocket.onmessage = ({ data }) => {
        setServerVal(data);
      };
    };

    ws();
  }, [db, val]); // Include `val` in the dependencies array if `val` is also used inside the effect// Reset Database

  const resetDatabase = () => {
    db.transaction((tx) => {
      // Drop the clips table if it exists
      tx.executeSql("DROP TABLE IF EXISTS clips", [], () => {
        console.log("Table dropped successfully");
      });
    });

    // Recreate the clips table
    db.transaction((tx) => {
      tx.executeSql(
        "CREATE TABLE IF NOT EXISTS clips (id INTEGER PRIMARY KEY AUTOINCREMENT, clip TEXT)",
        [],
        () => {
          console.log("Table created successfully");
        },
      );
    });

    // Update the val state to reflect the empty database
    setVal([]);
  };

  useEffect(() => {
    db.transaction((tx) => {
      tx.executeSql(
        "CREATE TABLE IF NOT EXISTS clips (id INTEGER PRIMARY KEY AUTOINCREMENT, clip TEXT)",
      );
    });

    db.transaction((tx) => {
      tx.executeSql("SELECT * FROM clips", [], (txObj, resultSet) =>
        setVal(resultSet.rows._array),
      );
    });
  }, [db]);

  const fetchCopiedText = async () => {
    const text = await Clipboard.getStringAsync();
    setCurrentVal(text);
  };

  const addClip = () => {
    if (currentVal === undefined) {
      return ToastAndroid.show("Your input is empty", ToastAndroid.CENTER);
    }
    db.transaction((tx) => {
      tx.executeSql(
        "INSERT INTO clips (clip) values (?)",
        [currentVal],
        (txObj, resultSet) => {
          let existingClips = [...val];
          existingClips.push({ id: resultSet.insertId, clip: currentVal });
          setVal(existingClips);
          setCurrentVal(undefined);
        },
      );
    });
  };

  const deleteClip = (id: number) => {
    db.transaction((tx) => {
      tx.executeSql(
        "DELETE FROM clips WHERE id = ?",
        [id],
        (txObj, resultSet) => {
          if (resultSet.rowsAffected > 0) {
            let existingCLips = [...val].filter((clip) => clip.id !== id);
            setVal(existingCLips);
          }
        },
      );
    });
  };

  const showClips = () => {
    return val.map((clip, index) => {
      return (
        <View
          key={index}
          style={styles.row}
          className="px-1 border-2 w-[80%] flex flex-row-reverse justify-center rounded space-x-3"
        >
          <TextInput multiline className="w-full text-[16px]">
            {clip.clip}
          </TextInput>
          <AwesomeButton
            width={60}
            backgroundColor="white"
            onPress={() => clip.id !== undefined && deleteClip(clip.id)}
          >
            <Octicons name="trash" size={24} color="black" />
          </AwesomeButton>
        </View>
      );
    });
  };

  const showSeverClips = () => {
    return (
      <View
        style={styles.row}
        className="px-1 border-2 w-[79%] flex flex-row-reverse justify-center rounded space-x-3"
      >
        <TextInput multiline className="w-full text-[16px]">
          {serverVal}
        </TextInput>
        <AwesomeButton
          width={60}
          backgroundColor="white"
          onPress={() => Clipboard.setStringAsync(serverVal)}
        >
          <Ionicons name="copy" size={24} color="black" />
        </AwesomeButton>
      </View>
    );
  };

  const settingModal = () => {
    if (setting === true)
      return (
        <Modal>
          <View className="flex flex-row justify-end mx-2 my-7">
            <AwesomeButton
              backgroundColor="white"
              width={60}
              onPress={() => setSetting(false)}
            >
              <FontAwesome name="close" size={24} color="black" />
            </AwesomeButton>
          </View>
          <View className="flex items-center space-y-8">
            <View>
              <WS />
            </View>
            {
              <ThemedButton
                width={295}
                name="bruce"
                type="danger"
                onPress={resetDatabase}
              >
                Reset Clipboard
              </ThemedButton>
            }
          </View>
        </Modal>
      );
  };

  return (
    <>
      <ScrollView className="flex justfiy-center mt-16">
        <View className="flex flex-row justify-end mx-3 mb-4">
          <AwesomeButton
            width={60}
            backgroundColor="white"
            onPress={() => setSetting(true)}
          >
            <Octicons name="server" size={24} color="black" />
          </AwesomeButton>
        </View>
        <View style={styles.container}>
          <TextInput
            className="w-[90%] text-center text-[16px]"
            multiline
            value={currentVal}
            placeholder="ClipWarp"
            onChangeText={setCurrentVal}
          />
          <View className="flex flex-row my-4 w-[96%] justify-between">
            <ThemedButton
              width={160}
              name="bruce"
              type="primary"
              onPress={addClip}
            >
              Send
            </ThemedButton>
            <ThemedButton
              width={160}
              name="bruce"
              type="secondary"
              onPress={fetchCopiedText}
            >
              Paste
            </ThemedButton>
          </View>
          {showSeverClips()}
          <View className="border-b-4 border-gray-400 w-full my-2" />
          {showClips()}
          {settingModal()}
          <StatusBar style="auto" />
        </View>
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "stretch",
    justifyContent: "space-between",
    margin: 8,
  },
  contentContainer: {
    flex: 1,
    alignItems: "center",
  },
});
