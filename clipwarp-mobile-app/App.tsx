import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Alert, View, Text, TextInput, ScrollView, Modal, ToastAndroid } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import * as SQLite from 'expo-sqlite';
import { ThemedButton } from 'react-native-really-awesome-button';
import AwesomeButton from "react-native-really-awesome-button";
import { Octicons } from '@expo/vector-icons';
import React, { useEffect, useState } from 'react';

type Clip = {
  id: number | undefined;
  clip: string;
};


export default function App() {
  const [db, setDb] = useState(SQLite.openDatabase('clip.db')); // SQLite database to save clipboard
  const [val, setVal] = useState<Clip[]>([]); // Clips are saved here
  const [currentVal, setCurrentVal] = useState<string | undefined>(undefined); // Text input value
  const [setting, setSetting] = useState<boolean>(false);
  


  useEffect(() => {
    const websocket = new WebSocket("ws://192.168.1.9:5678/");

    websocket.onerror = (error: Event) => {
     const webSocketError = error as WebSocketErrorEvent;
     Alert.alert('WebSocket Status', webSocketError.message, [
        {
          text: 'OK',
          onPress: () => console.log('Clicked'),
        },
        ]);

    };

    // Send data when `db` changes
    websocket.onopen = () => {
      websocket.send(JSON.stringify(val));
    };

    // Listen for messages
    websocket.onmessage = ({ data }) => {
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
    // Close the WebSocket connection when component unmounts
    return () => {
      websocket.close();
    };
  }, [db, val]); // Include `val` in the dependencies array if `val` is also used inside the effect// Reset Database

///* 
  const resetDatabase = () => {
  db.transaction(tx => {
    // Drop the clips table if it exists
    tx.executeSql('DROP TABLE IF EXISTS clips', [],
      () => {
        console.log('Table dropped successfully');
      },
    );
  });


  // Recreate the clips table
  db.transaction(tx => {
    tx.executeSql('CREATE TABLE IF NOT EXISTS clips (id INTEGER PRIMARY KEY AUTOINCREMENT, clip TEXT)',
      [],
      () => {
        console.log('Table created successfully');
      },
      );
  });

  // Update the val state to reflect the empty database
  setVal([]);
};
//*/


  useEffect(() => {
    db.transaction(tx => {
      tx.executeSql('CREATE TABLE IF NOT EXISTS clips (id INTEGER PRIMARY KEY AUTOINCREMENT, clip TEXT)')
    });

    db.transaction(tx => {
      tx.executeSql('SELECT * FROM clips', [],
        (txObj, resultSet) => setVal(resultSet.rows._array),
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
    db.transaction(tx => {
      tx.executeSql('INSERT INTO clips (clip) values (?)', [currentVal],
        (txObj, resultSet) => {
          let existingClips = [...val];
          existingClips.push({ id: resultSet.insertId, clip: currentVal});
          setVal(existingClips);
          setCurrentVal(undefined);
        },
      );
    });
  }

  const deleteClip = (id: number) => {
    db.transaction(tx => {
      tx.executeSql('DELETE FROM clips WHERE id = ?', [id],
        (txObj, resultSet) => {
          if (resultSet.rowsAffected > 0) {
            let existingCLips = [...val].filter(clip => clip.id !== id);
            setVal(existingCLips);
          }
        },
      );
    });
  };

  
  const showClips = () => {
    return val.map((clip, index) => {
      return (
        <View key={index} style={styles.row} className='px-1 border-2 w-[84%] flex flex-row-reverse justify-center rounded'>
          <TextInput multiline className='w-full mx-1 text-[16px]'>{clip.clip}</TextInput>
          <AwesomeButton width={50} backgroundColor='white' onPress={() => clip.id !== undefined && deleteClip(clip.id)}>
            <Octicons name="trash" size={24} color="black" />
          </AwesomeButton>
         </View>
      );
    });
  };

  const settingModal = () => {
    if (setting === true)
    return(
    <Modal>
      <Text className='h-48 flex m-auto justify-center items-center'>Hello</Text>
      <AwesomeButton  onPress={() => setSetting(false)}>Close</AwesomeButton>
    </Modal>
    );
  };


  return (
    <>
    <ScrollView className='flex justfiy-center mt-20'>
    <View style={styles.container}>
      <TextInput className='w-[90%] text-center text-[16px]' multiline value={currentVal} placeholder='ClipWarp' onChangeText={setCurrentVal} />
    <View className='flex flex-col gap-4 my-4 justify-center'>
        <ThemedButton name="bruce" type="primary" onPress={addClip}>Send</ThemedButton>
        <ThemedButton name="bruce" type="secondary" onPress={fetchCopiedText}>Paste</ThemedButton>
        {<ThemedButton name="bruce" type="danger" onPress={resetDatabase} >Reset</ThemedButton>} 
    </View>
      {showClips()}
      <AwesomeButton onPress={() => setSetting(true)}>Setting</AwesomeButton>
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
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'stretch',
    justifyContent: 'space-between',
    margin: 8
  },
    contentContainer: {
    flex: 1,
    alignItems: 'center',
  },
});
