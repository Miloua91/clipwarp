import {
  FlatList,
  StyleSheet,
  Alert,
  View,
  Text,
  TextInput,
  ScrollView,
  ToastAndroid,
  Pressable,
  SafeAreaView,
  StatusBar,
  Share,
  RefreshControl,
  AppState,
  BackHandler,
} from "react-native";
import * as Clipboard from "expo-clipboard";
import * as SQLite from "expo-sqlite/legacy";
import { ThemedButton } from "react-native-really-awesome-button";
import {
  Entypo,
  FontAwesome6,
  Ionicons,
  FontAwesome,
  MaterialIcons,
} from "@expo/vector-icons";
import React, {
  useEffect,
  useState,
  useCallback,
  useRef,
  useMemo,
} from "react";
import { webSocket, WS } from "./ws";
import { io } from "socket.io-client";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as SplashScreen from "expo-splash-screen";
import * as Notifications from "expo-notifications";
//import { useShareIntent } from "expo-share-intent";
import { i18n } from "./i18n";
import { getLocales } from "expo-localization";
import * as Linking from "expo-linking";
import { Skeleton } from "./skeleton";
import * as NavigationBar from "expo-navigation-bar";
import {
  BottomSheetModal,
  BottomSheetView,
  BottomSheetModalProvider,
  BottomSheetBackdrop,
  BottomSheetBackdropProps,
} from "@gorhom/bottom-sheet";
import { GestureHandlerRootView } from "react-native-gesture-handler";

SplashScreen.preventAutoHideAsync();

//TODO: Select multiple text items
//TODO: Add animation
//TODO: Sync db between dektop and mobile
//TODO: Add note to links
//TODO: Make the app function on IOS
//PERF: Add pull to refresh clips
//PERF: Add time
//PERF: Add notification
//PERF: open links with browser in notification
//PERF: Add button to open link from app
//PERF: add icon to notification, and make it appear only when app is in background
//PERF: Added share intent to the app
//PERF: Add Skelton

type Clip = {
  id: number | undefined;
  clip: string;
};

interface ClipDb {
  id: number;
  clips_text: string;
  user_name: string;
  date: string;
}

const bgColor = "#252422";
const cardColor = "#403d39";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

const deviceLanguage = getLocales()?.[0]?.languageCode;

NavigationBar.setBackgroundColorAsync("#000");

export default function App() {
  /*
  const { hasShareIntent, shareIntent, resetShareIntent } = useShareIntent({
    debug: true,
    resetOnBackground: true,
  });
  */

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
  const appState = useRef(AppState.currentState);
  const responseListener = useRef<Notifications.Subscription>();
  const [appStateVisible, setAppStateVisible] = useState(appState.current);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    async function getAddress() {
      const address = await AsyncStorage.getItem("address");
      const port = await AsyncStorage.getItem("port");
      setWsAddress(address ?? "192.168.1");
      setWsPort(Number(port) ?? 42069);
      await SplashScreen.hideAsync();
    }
    getAddress();

    const subscription = AppState.addEventListener("change", (nextAppState) => {
      appState.current = nextAppState;
      setAppStateVisible(appState.current);
    });

    responseListener.current =
      Notifications.addNotificationResponseReceivedListener(
        async (response) => {
          const notificationId = response.notification.request.identifier;
          const clip = response?.notification?.request?.content.body;
          const userAction = response.actionIdentifier;

          if (!clip) return null;

          if (userAction === "copy") {
            Clipboard.setStringAsync(clip);
            BackHandler.exitApp();
          } else if (canOpenLink(clip)) {
            Linking.openURL(clip);
          }
          await Notifications.dismissNotificationAsync(notificationId);
        },
      );

    return () => {
      subscription.remove();
      responseListener.current &&
        Notifications.removeNotificationSubscription(responseListener.current);
    };
  }, [connection, appStateVisible, seconds]);

  useEffect(() => {
    if (wsAddress && wsPort) {
      getClips();
    }
  }, [wsAddress, wsPort]);

  const getClips = async () => {
    try {
      const response = await fetch(
        `http://${wsAddress}:${(wsPort ?? 42069) + 1}/`,
      );
      const data = await response.json();
      setClipsDb(data);
      return data;
    } catch (error) {
      console.log("Failed to fetch clips:", error);
    }
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    getClips().then(() => setRefreshing(false));
  }, [wsAddress, wsPort, val, connection]);

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
    if (!connection || appStateVisible === "background") {
      const timer = setInterval(() => {
        setSeconds((prevSeconds) => {
          // Increment the seconds, and reset to 0 if it exceeds 9
          return prevSeconds < 9 ? prevSeconds + 1 : 0;
        });
      }, 1000);
      return () => clearInterval(timer);
    } else if (connection) {
      getClips();
    }
  }, [connection, appStateVisible, seconds]);

  useEffect(() => {
    // Send data when `db` changes
    const ws = async () => {
      const websocket = await webSocket();
      websocket.onopen = async () => {
        setLoading(true);
        /*
  if (hasShareIntent) {
    if (shareIntent.text === undefined || shareIntent.text === null) {
      return ToastAndroid.show(
        "Your input is empty",
        ToastAndroid.CENTER,
      );
    }
    if (shareIntent.text !== undefined && shareIntent.text !== null) {
      resetShareIntent();
      websocket.send(shareIntent.text);
      await getClips(); // Await getClips if called here
    }
  }
  */

        try {
          // Send each clip
          for (const vals of val) {
            websocket.send(vals.clip);
          }
          deleteDatabase();
          await getClips();
        } catch (error) {
          console.error("Error:", error);
        } finally {
          setLoading(false);
        }

        setConnection(true);
      };
    };

    ws();
  }, [seconds]);

  useEffect(() => {
    // Send data when `db` changes
    const ws = async () => {
      const websocket = await webSocket();
      websocket.onmessage = async () => {
        const newClips = await getClips();
        const lastClip = newClips?.at(-1)?.clips_text;
        const username = newClips?.at(-1)?.user_name;
        if (canOpenLink(lastClip)) {
          Notifications.setNotificationCategoryAsync("action", [
            {
              identifier: "copy",
              buttonTitle: i18n.t("copyClip"),
              options: { isDestructive: true },
            },
            {
              identifier: "open",
              buttonTitle: i18n.t("openLink"),
              options: { isDestructive: true },
            },
          ]);
        } else {
          Notifications.setNotificationCategoryAsync("action", [
            {
              identifier: "copy",
              buttonTitle: i18n.t("copyClip"),
              options: { isDestructive: true },
            },
          ]);
        }

        if (lastClip && username && appStateVisible === "background") {
          await Notifications.scheduleNotificationAsync({
            content: {
              title: username,
              body: lastClip,
              categoryIdentifier: "action",
            },
            trigger: null,
          });
        }
      };
    };

    ws();
    /*
    if (!connection && hasShareIntent) {
      db.transaction((tx) => {
        if (shareIntent.text !== undefined && shareIntent.text !== null) {
          tx.executeSql(
            "INSERT INTO clips (clip) values (?)",
            [shareIntent.text],
            (txObj, resultSet) => {
              let existingClips = [...val];
              resetShareIntent();
              existingClips.push({
                id: resultSet.insertId,
                clip: shareIntent.text ?? "",
              });
              setVal(existingClips);
            },
          );
        }
      });
    }
    */
  }, [seconds, appStateVisible]);

  useEffect(() => {
    const ws = async () => {
      const websocket = await webSocket();

      websocket.onclose = () => {
        setConnection(false);
        /*
        Alert.alert(i18n.t("wsStatus"), i18n.t("wsMessage"), [
          {
            text: "OK",
          },
        ]);
        */
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
      await getClips();
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
      await getClips();
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
    Alert.alert(i18n.t("resetDatabase"), i18n.t("resetMessage"), [
      {
        text: "Yes",
        onPress: resetDatabase,
        style: "destructive",
      },
      {
        text: "No",
        style: "cancel",
      },
    ]);
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
    console.log(currentVal);
    if (currentVal === undefined || !currentVal?.trim()) {
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

  const openLink = async (clip: string) => {
    try {
      Linking.openURL(clip);
    } catch (error) {
      console.error("Can't open link:", error);
    }
  };

  function canOpenLink(url: string): boolean {
    try {
      const parsedUrl = new URL(url);
      return ["http:", "https:"].includes(parsedUrl.protocol);
    } catch (error) {
      return false;
    }
  }

  const reversedVal = [...val].reverse();
  const showClips = ({ item: clip }: { item: Clip }) => {
    return (
      <View
        key={clip.id}
        className={`mb-2 min-w-full py-2 rounded-xl`}
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
            disabled={canOpenLink(clip.clip) ? false : true}
            onPress={() => clip.clip !== undefined && openLink(clip.clip)}
            className="active:bg-stone-600 w-15 h-9 px-1 py-[2px] rounded"
          >
            <MaterialIcons
              name="open-in-browser"
              size={32}
              color={canOpenLink(clip.clip) ? "white" : "gray"}
            />
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
  };

  const reversedClipsDb = [...clipsDb].reverse();
  const showClipsBd = ({ item: clip }: { item: ClipDb }) => {
    return (
      <View
        key={clip.id}
        className={`mb-2 py-2 rounded-xl min-w-full`}
        style={styles.card}
      >
        <View className="px-2 w-full border-b border-stone-600 my-1 pb-4 flex flex-col">
          <TextInput multiline className="text-gray-100 text-[16px]">
            {clip.clips_text}
          </TextInput>
          <Text style={styles.text} className="text-gray-100 text-[14px]">
            {clip.date} | {clip.user_name}
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
            disabled={canOpenLink(clip.clips_text) ? false : true}
            onPress={() =>
              clip.clips_text !== undefined && openLink(clip.clips_text)
            }
            className="active:bg-stone-600 w-15 h-9 px-1 py-[2px] rounded"
          >
            <MaterialIcons
              name="open-in-browser"
              size={32}
              color={canOpenLink(clip.clips_text) ? "white" : "gray"}
            />
          </Pressable>
          <Pressable
            onPress={() => clip.id !== undefined && deleteClipsDb(clip.id)}
            className={`active:bg-red-500 w-15 h-9 p-1 rounded ${deviceLanguage === "ar" ? "rotate-180" : ""}`}
          >
            <FontAwesome6 name="delete-left" size={28} color="white" />
          </Pressable>
        </View>
      </View>
    );
  };

  const bottomSheetModalRef = useRef<BottomSheetModal>(null);

  const snapPoints = useMemo(() => ["73%"], []);

  const handleSettingPress = () => {
    if (setting) {
      bottomSheetModalRef.current?.close();
    } else {
      bottomSheetModalRef.current?.present();
    }
    setSetting(!setting);
  };

  const handleCloseModalPress = useCallback(() => {
    bottomSheetModalRef.current?.close();
    setSetting(false);
  }, []);

  const renderBackdrop = useCallback(
    (props: BottomSheetBackdropProps) => (
      <BottomSheetBackdrop
        {...props}
        disappearsOnIndex={-1}
        appearsOnIndex={0}
        onPress={handleCloseModalPress}
      />
    ),
    [],
  );

  const settingModal = () => {
    return (
      <BottomSheetModalProvider>
        <View>
          <BottomSheetModal
            ref={bottomSheetModalRef}
            snapPoints={snapPoints}
            enablePanDownToClose={true}
            backgroundStyle={{
              backgroundColor: bgColor,
            }}
            handleStyle={{
              backgroundColor: bgColor,
              borderRadius: 10,
            }}
            handleIndicatorStyle={{ backgroundColor: "white" }}
            onDismiss={() => setSetting(false)}
            backdropComponent={renderBackdrop}
          >
            <BottomSheetView style={styles.contentContainer}>
              <View
                className="flex flex-row justify-start px-2 py-[2px] w-full"
                style={styles.background}
              >
                <Pressable
                  onPress={handleCloseModalPress}
                  className="active:bg-stone-600 w-10 h-10 px-[10px] py-[4px] rounded absolute mx-2"
                >
                  <FontAwesome name={"angle-down"} size={32} color="white" />
                </Pressable>
                <Text className="m-auto text-xl font-semibold pb-6 text-white">
                  {i18n.t("settings")}
                </Text>
              </View>
              <View
                style={styles.background}
                className="w-full flex items-center space-y-8 h-full px-6"
              >
                <View className="w-full">
                  <WS />
                </View>
                <View
                  style={styles.card}
                  className={`border rounded-xl h-20 w-full p-2 flex flex-row justify-between items-center m-auto`}
                >
                  <Text className="text-lg text-white  w-[70%]">
                    {i18n.t("resetDb")}
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
            </BottomSheetView>
          </BottomSheetModal>
        </View>
      </BottomSheetModalProvider>
    );
  };

  return (
    <>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <SafeAreaView>
          <StatusBar backgroundColor={`${bgColor}`} />
        </SafeAreaView>
        <View className="h-full w-full">
          <View
            className="flex flex-row justify-between items-center h-12"
            style={styles.background}
          >
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
          <View style={styles.container} className="pt-4">
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
                {i18n.t("Paste")}
              </ThemedButton>
              <ThemedButton
                width={160}
                name="bruce"
                type="secondary"
                onPressIn={addClip}
              >
                {i18n.t("Send")}
              </ThemedButton>
            </View>
            <View className="border-b border-stone-500 w-[97%] my-2" />
          </View>
          <View style={[styles.contentContainer, styles.background]}>
            {loading ? (
              <>
                <Skeleton />
                <Skeleton />
                <Skeleton />
              </>
            ) : connection ? (
              <FlatList
                refreshControl={
                  <RefreshControl
                    refreshing={refreshing}
                    onRefresh={onRefresh}
                  />
                }
                data={reversedClipsDb}
                renderItem={showClipsBd}
                keyExtractor={(clip) => clip.id.toString()}
                style={styles.background}
                contentContainerStyle={{
                  alignItems: "center",
                }}
                className="w-[97%]"
              />
            ) : (
              <FlatList
                data={reversedVal}
                renderItem={showClips}
                keyExtractor={(clip) =>
                  clip.id ? clip.id.toString() : Math.random().toString()
                }
                style={styles.background}
                contentContainerStyle={{
                  alignItems: "center",
                }}
                className="w-[97%]"
              />
            )}
          </View>
        </View>
        {settingModal()}
      </GestureHandlerRootView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
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
