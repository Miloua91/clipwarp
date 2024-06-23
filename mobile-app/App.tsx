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
  Share,
  RefreshControl,
} from "react-native";
import * as Clipboard from "expo-clipboard";
import * as SQLite from "expo-sqlite/legacy";
import { ThemedButton } from "react-native-really-awesome-button";
import {
  Entypo,
  FontAwesome6,
  Ionicons,
  FontAwesome,
} from "@expo/vector-icons";
import React, { useEffect, useState, useCallback } from "react";
import { webSocket, WS } from "./ws";
import { io } from "socket.io-client";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as SplashScreen from "expo-splash-screen";
SplashScreen.preventAutoHideAsync();

//TODO: Sync db between dektop and mobile
//TODO: Make the app function on IOS
//TODO: Add notification, open links with browserj
//TODO: Add pull to refresh clips
//TODO: Add time

type Clip = {
  id: number | undefined;
  clip: string;
};

interface ClipDb {
  id: number;
  clips_text: string;
  user_name: string;
}

const bgColor = "#252422";
const cardColor = "#403d39";

export default function App() {
  const [db, setDb] = useState(SQLite.openDatabase("clipwarp.db")); // SQLite database to save clipboard locally
  const [val, setVal] = useState<Clip[]>([]); // Clips are saved here
  const [currentVal, setCurrentVal] = useState<string | undefined>(undefined); // Text input value
  const [clipsDb, setClipsDb] = useState<ClipDb[]>([]);
  const [connection, setConnection] = useState(false);
  const [setting, setSetting] = useState<boolean>(false);
  const [wsAddress, setWsAddress] = useState<string>();
  const [wsPort, setWsPort] = useState<number>();
  const [seconds, setSeconds] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    async function getAddress() {
      const address = await AsyncStorage.getItem("address");
      const port = await AsyncStorage.getItem("port");
      setWsAddress(address ?? "192.168.1");
      setWsPort(Number(port) ?? 42069);
      await SplashScreen.hideAsync();
    }
    getAddress();
  }, [wsPort]);

  async function getClips() {
    const response = await fetch(
      `http://${wsAddress}:${(wsPort ?? 42069) + 1}/`,
    );
    const data = await response.json();
    setClipsDb(data);
  }

  useEffect(() => {
    getClips();
  }, [wsPort]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    getClips().then(() => setRefreshing(false));
  }, []);

  useEffect(() => {
    const socket = io(`http://${wsAddress}:${(wsPort ?? 42069) + 1}/`);

    socket.onAny((event) => {
      getClips();
    });
    socket.on("disconnect", () => {
      socket.connect;
    });

    return () => {
      socket.disconnect();
    };
  }, [getClips, wsPort]);

  useEffect(() => {
    if (!connection) {
      const timer = setInterval(() => {
        setSeconds((prevSeconds) => prevSeconds + 1);
      }, 1000);

      return () => clearInterval(timer);
    } else {
      setSeconds(0);
    }
  }, [connection]);

  useEffect(() => {
    // Send data when `db` changes
    const ws = async () => {
      const websocket = await webSocket();
      websocket.onopen = () => {
        val.forEach((vals) => {
          websocket.send(vals.clip);
          deleteDatabase();
          getClips();
        });
        setConnection(true);
      };

      websocket.onmessage = () => {
        getClips();
      };
    };

    ws();
  }, [db, val, seconds]);

  useEffect(() => {
    const ws = async () => {
      const websocket = await webSocket();

      websocket.onclose = () => {
        setConnection(false);
        Alert.alert("WebSocket Status", "Websocket connection closed", [
          {
            text: "OK",
          },
        ]);
      };
    };

    ws();
  }, [connection]);

  async function deleteClipsDb(clipId: number) {
    try {
      const response = await fetch(
        `http://${wsAddress}:${(wsPort ?? 42069) + 1}/delete/${clipId}`,
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
      const response = await fetch(
        `http://${wsAddress}:${(wsPort ?? 42069) + 1}/reset`,
        {
          method: "POST",
        },
      );
      if (!response.ok) {
        throw new Error("Failed to delete clips");
      }
      getClips();
    } catch (error) {
      console.error(error);
    }
  }

  const deleteDatabase = () => {
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

  function resetAlert() {
    Alert.alert(
      "Reset Database",
      "Resetting the Clips database is irreversible. Are you sure want to proceed?",
      [
        {
          text: "Yes",
          onPress: resetDatabase,
          style: "destructive",
        },
        {
          text: "No",
          style: "cancel",
        },
      ],
    );
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

  const shareClip = async (clip: string) => {
    try {
      await Share.share({
        message: clip,
      });
    } catch (error) {
      console.error("Error sharing:", error);
    }
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
            className="px-2 w-full text-gray-100 text-[16px] border-b border-stone-600 my-1 pb-4"
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
              onPress={() => clip.clip !== undefined && shareClip(clip.clip)}
              className="active:bg-stone-600 w-15 h-9 p-1 rounded"
            >
              <Entypo name="share" size={26} color="white" />
            </Pressable>
            <Pressable
              onPress={() => clip.id !== undefined && deleteClip(clip.id)}
              className="active:bg-red-500 w-15 h-9 p-1 rounded"
            >
              <FontAwesome6 name="delete-left" size={28} color="white" />
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
          <View className="px-2 w-full border-b border-stone-600 my-1 pb-4 flex flex-col">
            <TextInput multiline className="text-gray-100 text-[16px]">
              {clip.clips_text}
            </TextInput>
            <Text
              style={styles.text}
              className="w-full text-gray-100 text-[14px]"
            >
              {clip.user_name}
            </Text>
          </View>
          <View className="flex flex-row justify-between py-2 px-3">
            <Pressable
              onPress={() => Clipboard.setStringAsync(clip.clips_text)}
              className="active:bg-stone-600 w-[2rem] h-9 p-1 rounded"
            >
              <FontAwesome name="clipboard" size={26} color="white" />
            </Pressable>
            <Pressable
              onPress={() =>
                clip.clips_text !== undefined && shareClip(clip.clips_text)
              }
              className="active:bg-stone-600 w-15 h-9 p-1 rounded"
            >
              <Entypo name="share" size={26} color="white" />
            </Pressable>
            <Pressable
              onPress={() => clip.id !== undefined && deleteClipsDb(clip.id)}
              className="active:bg-red-500 w-15 h-9 p-1 rounded"
            >
              <FontAwesome6 name="delete-left" size={28} color="white" />
            </Pressable>
          </View>
        </View>
      );
    });
  };

  const handleSettingPress = () => {
    setSetting(true);
  };

  const settingModal = () => {
    if (setting === true)
      return (
        <Modal
          onRequestClose={() => {
            setSetting(false);
          }}
        >
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
            className="flex items-center space-y-8 h-full px-6"
          >
            <View className="w-full">
              <WS />
            </View>
            <View
              style={styles.card}
              className="border rounded-xl w-full h-20 p-2 flex flex-row justify-between items-center m-auto"
            >
              <Text className="text-lg text-white ">
                Reset clipboard database
              </Text>
              <ThemedButton
                width={75}
                name="bruce"
                type="danger"
                onPress={() => resetAlert()}
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
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        className={`flex justfiy-center `}
        style={styles.background}
      >
        <View className="flex flex-row justify-between items-center">
          <View
            className={`w-3 h-3 m-5 rounded-full ${connection ? "bg-green-500" : "bg-red-500"}`}
          />
          <Pressable
            className="h-12 w-12 p-2 mx-1 my-4 active:bg-stone-600 rounded-lg"
            onPress={handleSettingPress}
          >
            <Ionicons name="settings-sharp" size={32} color="white" />
          </Pressable>
        </View>
        <View style={styles.container}>
          <TextInput
            className="w-[97%] rounded-lg h-16 text-center text-[16px] text-white"
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
              onPressIn={fetchCopiedText}
            >
              Paste
            </ThemedButton>
            <ThemedButton
              width={160}
              name="bruce"
              type="secondary"
              onPressIn={addClip}
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
  text: {
    textAlign: "right",
  },
});
