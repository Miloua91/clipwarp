import { I18n } from "i18n-js";
import { getLocales } from "expo-localization";

export const deviceLanguage = getLocales()?.[0]?.languageCode ?? "en";

export const i18n = new I18n({
  it: {
    Send: "Send",
    Paste: "Paste",
    serverIP: "Enter server's IP",
    serverPort: "Enter server's port",
    deviceName: "Enter device's name",
    resetDb: "Reset clipboard database",
    settings: "Settings",
    wsStatus: "WebSocket Status",
    wsMessage: "Websocket connection closed",
    msgDeviceName: "Please enter a device name",
  },
  fr: {
    Send: "Envoyer",
    Paste: "Coller",
    serverIP: "Entrez l'adresse IP du serveur",
    serverPort: "Entrez le port du serveur",
    deviceName: "Entrez le nom de l'appareil",
    resetDb: "Réinitialiser la base de \n données du presse-papiers",
    settings: "Paramètres",
    wsStatus: "Statut WebSocket",
    wsMessage: "Connexion WebSocket fermée",
    msgDeviceName: "Veuillez entrer un nom d'appareil",
  },
  ar: {
    Send: "إرسال",
    Paste: "لصق",
    serverIP: "أدخل عنوان IP الخاص بالخادم",
    serverPort: "أدخل منفذ الخادم",
    deviceName: "أدخل اسم الجهاز",
    resetDb: "إعادة تعيين قاعدة بيانات الحافظة",
    settings: "الإعدادات",
    wsStatus: "حالة WebSocket",
    wsMessage: "تم إغلاق اتصال WebSocket",
    msgDeviceName: "يرجى إدخال اسم الجهاز",
  },
  es: {
    Send: "Enviar",
    Paste: "Pegar",
    serverIP: "Ingrese la IP del servidor",
    serverPort: "Ingrese el puerto del servidor",
    deviceName: "Ingrese el nombre del \n dispositivo",
    resetDb: "Restablecer la base de \n datos del portapapeles",
    settings: "Configuraciones",
    wsStatus: "Estado de WebSocket",
    wsMessage: "Conexión WebSocket cerrada",
    msgDeviceName: "Por favor, ingrese un nombre de dispositivo",
  },
  pr: {
    Send: "Enviar",
    Paste: "Colar",
    serverIP: "Digite o IP do servidor",
    serverPort: "Digite a porta do servidor",
    deviceName: "Digite o nome do dispositivo",
    resetDb: "Redefinir banco de dados da \n área de transferência",
    settings: "Configurações",
    wsStatus: "Status do WebSocket",
    wsMessage: "Conexão WebSocket fechada",
    msgDeviceName: "Por favor, insira um nome de dispositivo",
  },
  en: {
    Send: "Invia",
    Paste: "Incolla",
    serverIP: "Inserisci l'IP del server",
    serverPort: "Inserisci la porta del server",
    deviceName: "Inserisci il nome del dispositivo",
    resetDb: "Reimposta il database degli appunti",
    settings: "Impostazioni",
    wsStatus: "Stato WebSocket",
    wsMessage: "Connessione WebSocket chiusa",
    msgDeviceName: "Per favore, inserisci un nome del dispositivo",
  },
});

i18n.defaultLocale = deviceLanguage;

i18n.locale = deviceLanguage;
