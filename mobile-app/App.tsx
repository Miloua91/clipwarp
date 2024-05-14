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
  SafeAreaView,
  StatusBar,
} from "react-native";
import * as Clipboard from "expo-clipboard";
import * as SQLite from "expo-sqlite";
import { ThemedButton } from "react-native-really-awesome-button";
import { Ionicons, FontAwesome } from "@expo/vector-icons";
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

const bgColor = "#252422";
const cardColor = "#403d39";

export default function App() {
  const db = await SQLite.openDatabaseAsync("clipwarp.db"); // SQLite database to save clipboard
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

  const resetDatabase = async () => {
    deleteAllClipsDb();
   await db.withTransactionAsync(async () => {
      await db.execAsync("DROP TABLE IF EXISTS clips");
      ;
    });

    // Recreate the clips table
    db.withTransactionAsync(async () => {
      await db.execAsync(
        "CREATE TABLE IF NOT EXISTS clips (id INTEGER PRIMARY KEY AUTOINCREMENT, clip TEXT)")
    });

    // Update the val state to reflect the empty database
    setVal([]);
  };

  useEffect(() => {
   await db.withTransactionAsync(async () => {
      db.execAsync(
        "CREATE TABLE IF NOT EXISTS clips (id INTEGER PRIMARY KEY AUTOINCREMENT, clip TEXT)")});

    db.withTransactionAsync(async () => {
    const resultSet = await  db.execAsync("SELECT * FROM clips")
    setVal(resultSet.rows._array);
    })
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
      db.withTransactionAsync(async () => {
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
    db.withTransactionAsync((tx) => {
      tx.(
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
    const reversedVal = [...val].reverse();
    return reversedVal.map((clip, index) => {
      return (
        <View
          key={index}
          className={`mb-2 w-[97%] py-2 rounded-xl`}
          style={styles.card}
        >
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
    const reversedClipsDb = [...clipsDb].reverse();
    return reversedClipsDb.map((clip, index) => {
      return (
        <View
          key={index}
          className={`mb-2 w-[97%] py-2 rounded-xl`}
          style={styles.card}
        >
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
          <View
            className="flex flex-row justify-start px-2 py-2"
            style={styles.background}
          >
            <Pressable
              onPress={() => setSetting(false)}
              className="active:bg-stone-600 w-10 h-10 px-3 py-[2px] rounded absolute"
            >
              <FontAwesome name="angle-left" size={32} color="white" />
            </Pressable>
            <Text className="m-auto text-xl font-semibold pb-10 text-white">
              Settings
            </Text>
          </View>
          <View
            style={styles.background}
            className="flex items-center space-y-8 h-full"
          >
            <View className="w-96">
              <WS />
            </View>
            <View
              style={styles.card}
              className="border rounded-xl w-[86%] h-20 p-2 flex flex-row justify-between items-center m-auto"
            >
              <Text className="text-lg text-white">
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
      <SafeAreaView>
        <StatusBar backgroundColor={`${bgColor}`} />
      </SafeAreaView>
      <ScrollView className={`flex justfiy-center `} style={styles.background}>
        <View className="flex flex-row justify-end">
          <Pressable
            className="h-12 w-12 p-2 mx-1 my-4 active:bg-stone-600 rounded-lg"
            onPress={handleSettingPress}
          >
            <Ionicons name="settings-sharp" size={32} color="white" />
          </Pressable>
        </View>
        <View style={styles.container}>
          <TextInput
            className="w-[97%] rounded-lg h-16 text-center text-[16px]  text-white"
            multiline
            value={currentVal}
            placeholder="ClipWarp"
            onChangeText={setCurrentVal}
            style={styles.card}
          />
          <View className="flex flex-row my-4 w-[96%] justify-between">
            <ThemedButton
              width={160}
              name="bruce"
              backgroundColor="#403d39"
              type="primary"
              onPress={fetchCopiedText}
            >
              Paste
            </ThemedButton>
            <ThemedButton
              width={160}
              name="bruce"
              type="secondary"
              onPress={addClip}
            >
              Send
            </ThemedButton>
          </View>
          <View className="border-b border-stone-500 w-[97%] my-2" />
          {connection ? showClipsBd() : showClips()}
          {settingModal()}
        </View>
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: `${bgColor}`,
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
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
  card: {
    backgroundColor: `${cardColor}`,
  },
  background: {
    backgroundColor: `${bgColor}`,
  },
});
