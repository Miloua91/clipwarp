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
  Pressable,
} from "react-native";
import * as Clipboard from "expo-clipboard";
import * as SQLite from "expo-sqlite";
import { ThemedButton } from "react-native-really-awesome-button";
import AwesomeButton from "react-native-really-awesome-button";
import { Octicons, FontAwesome } from "@expo/vector-icons";
import React, { useEffect, useState } from "react";
import { webSocket, WS } from "./ws";
import { io } from "socket.io-client";

type Clip = {
  id: number | undefined;
  clip: string;
};

interface ClipDb {
  id: number;
  clips_text: string; // Add the 'clips_text' property
  // Add other properties as needed
}

export default function App() {
  const [db, setDb] = useState(SQLite.openDatabase("clipwarp.db")); // SQLite database to save clipboard
  const [val, setVal] = useState<Clip[]>([]); // Clips are saved here
  const [currentVal, setCurrentVal] = useState<string | undefined>(undefined); // Text input value
  const [clipsDb, setClipsDb] = useState<ClipDb[]>([]);
  const [connection, setConnection] = useState(false);
  const [setting, setSetting] = useState<boolean>(false);

  async function getClips() {
    const response = await fetch("http://192.168.1.13:5000/");
    const data = await response.json();
    setClipsDb(data);
  }

  useEffect(() => {
    getClips();
  }, []);

  useEffect(() => {
    const socket = io("ws://192.168.1.13:5000/");

    socket.onAny((event) => {
      getClips();
    });
    socket.on("disconnect", () => {
      socket.connect;
    });

    return () => {
      socket.disconnect();
    };
  }, [getClips]);

  useEffect(() => {
    // Send data when `db` changes
    const ws = async () => {
      const websocket = await webSocket();
      websocket.onopen = () => {
        val.forEach((vals) => {
          websocket.send(vals.clip);
          getClips();
          deleteClip(vals.id as number);
        });
        setConnection(true);
      };

      websocket.onmessage = () => {
        getClips();
      };
    };

    ws();
  }, [db, val]); // Include `val` in the dependencies array if `val` is also used inside the effect// Reset Database

  useEffect(() => {
    const ws = async () => {
      const websocket = await webSocket();

      websocket.onclose = () => {
        setConnection(false);
        Alert.alert("WebSocket Status", "Websocket closed", [
          {
            text: "OK",
          },
        ]);
      };
    };

    ws();
  }, []);

  async function deleteClipsDb(clipId: number) {
    try {
      const response = await fetch(
        `http://192.168.1.13:5000/delete/${clipId}`,
        {
          method: "DELETE",
        },
      );
      if (!response.ok) {
        throw new Error("Failed to delete clip");
      }
      getClips();
    } catch (error) {
      console.error(error);
    }
  }

  async function deleteAllClipsDb() {
    try {
      const response = await fetch(`http://192.168.1.13:5000/reset`, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Failed to delete clips");
      }
      getClips();
    } catch (error) {
      console.error(error);
    }
  }

  const resetDatabase = () => {
    deleteAllClipsDb();
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
    if (connection) {
      const ws = async () => {
        const websocket = await webSocket();
        websocket.onopen = () => {
          if (currentVal !== undefined) {
            websocket.send(currentVal);
            setCurrentVal(undefined);
            getClips();
          }
        };
      };
      ws();
    } else {
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
    }
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
    return val.reverse().map((clip, index) => {
      return (
        <View key={index} className="mb-2 bg-stone-800 w-[97%] py-2 rounded-xl">
          <TextInput
            multiline
            className="px-2 w-full text-gray-100 text-[16px] border-b border-stone-700 my-1 pb-2"
          >
            {clip.clip}
          </TextInput>
          <View className="flex flex-row justify-between py-2 px-3">
            <Pressable
              onPress={() => Clipboard.setStringAsync(clip.clip)}
              className="active:bg-stone-600 w-[2rem] h-9 p-1 rounded"
            >
              <FontAwesome name="clipboard" size={26} color="white" />
            </Pressable>
            <Pressable
              onPress={() => clip.id !== undefined && deleteClip(clip.id)}
              className="active:bg-stone-600 w-15 h-9 p-1 rounded"
            >
              <Text className="text-gray-100 text-lg">Delete</Text>
            </Pressable>
          </View>
        </View>
      );
    });
  };

  const showClipsBd = () => {
    return clipsDb.reverse().map((clip, index) => {
      return (
        <View key={index} className="mb-2 bg-stone-800 w-[97%] py-2 rounded-xl">
          <TextInput
            multiline
            className="px-2 w-full text-gray-100 text-[16px] border-b border-stone-700 my-1 pb-2"
          >
            {clip.clips_text}
          </TextInput>
          <View className="flex flex-row justify-between py-2 px-3">
            <Pressable
              onPress={() => Clipboard.setStringAsync(clip.clips_text)}
              className="active:bg-stone-600 w-[2rem] h-9 p-1 rounded"
            >
              <FontAwesome name="clipboard" size={26} color="white" />
            </Pressable>
            <Pressable
              onPress={() => clip.id !== undefined && deleteClipsDb(clip.id)}
              className="active:bg-stone-600 w-15 h-9 p-1 rounded"
            >
              <Text className="text-gray-100 text-lg">Delete</Text>
            </Pressable>
          </View>
        </View>
      );
    });
  };

  const handleSettingPress = () => {
    setTimeout(() => {
      setSetting(true);
    }, 50);
  };

  const settingModal = () => {
    if (setting === true)
      return (
        <Modal>
          <View className="flex flex-row justify-start mx-2 my-6">
            <Pressable
              onPress={() => setSetting(false)}
              className="active:bg-stone-100 w-10 h-10 px-3 py-[2px] rounded absolute"
            >
              <FontAwesome name="angle-left" size={32} color="black" />
            </Pressable>
            <Text className="m-auto text-xl font-semibold py-1">Settings</Text>
          </View>
          <View className="flex items-center space-y-8">
            <View className="w-96">
              <WS />
            </View>
            <View className="border rounded-xl w-[86%] h-20 p-2 flex flex-row justify-between items-center m-auto">
              <Text className="text-lg text-stone-800">
                Reset clipboard database
              </Text>
              <ThemedButton
                width={75}
                name="bruce"
                type="danger"
                onPress={resetDatabase}
              >
                Reset
              </ThemedButton>
            </View>
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
            onPress={handleSettingPress}
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
          <View className="border-b border-stone-500 w-[97%] my-2" />
          {connection ? showClipsBd() : showClips()}
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
