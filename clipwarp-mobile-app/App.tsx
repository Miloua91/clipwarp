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
import { Octicons,FontAwesome,Ionicons } from "@expo/vector-icons";
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
        if (currentVal !== undefined) {
        websocket.send(currentVal);
      }
      };

      websocket.onmessage = ({ data }) => {
        setServerVal(data);
      db.transaction(tx => {
          tx.executeSql('INSERT INTO clips (clip) values (?)', [data],
            (txObj, resultSet) => {
              let existingClips = [...val];
              existingClips.push({ id: resultSet.insertId, clip: data});
              setVal(existingClips);
              setCurrentVal(undefined);
            },
          );
        });
      };

      };

    

    ws();
  }, [db, val]); // Include `val` in the dependencies array if `val` is also used inside the effect// Reset Database

  useEffect(() => {
    const ws = async () => {
      const websocket = await webSocket();
       websocket.onclose = () => {
        Alert.alert("WebSocket Status", "Websocket closed", [
          {
            text: "OK",
          },
        ]);
      };
    };

    ws();
  }, []);

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
          className="mb-2 bg-stone-800 w-[97%] py-2 rounded-xl"
        >
          <TextInput multiline className="px-2 w-full text-gray-100 text-[16px] border-b border-stone-700 my-1 pb-2">
            {clip.clip}
          </TextInput>
          <View className="flex flex-row justify-between py-2 px-3">
        <Pressable onPress={() => Clipboard.setStringAsync(clip.clip)} className="active:bg-stone-600 w-[2rem] h-9 p-1 rounded">
          <FontAwesome name="clipboard" size={26} color="white" />
            </Pressable>
          <Pressable
            onPress={() => clip.id !== undefined && deleteClip(clip.id)} className="active:bg-stone-600 w-15 h-9 p-1 rounded"
          >
              <Text className="text-gray-100 text-lg">Delete</Text>
          </Pressable>
          </View>
        </View>
      );
    });
  };

  const showSeverClips = () => {
    return (
      <View
        className="px-3 bg-stone-800 w-[97%] flex flex-row justify-center rounded-xl"
      >
      <TextInput multiline className="px-4 py-2 w-full text-gray-100 text-[16px] right-3">
          {serverVal}
        </TextInput>
        <Pressable
          className="absolute flex flex-row justify-end active:bg-stone-600 h-8 p-1 right-1 top-[6px] rounded"
          onPress={() => Clipboard.setStringAsync(serverVal)}
        >
          <Ionicons name="copy" size={24} color="white" />
        </Pressable>
      </View>
    );
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
          {showSeverClips()}
          <View className="border-b border-stone-500 w-[97%] my-2" />
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
