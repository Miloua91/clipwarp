import { I18n } from "i18n-js";
import { getLocales } from "expo-localization";

export const deviceLanguage = getLocales()?.[0]?.languageCode ?? "en";
const supportedLanguages = [
  "en",
  "fr",
  "ar",
  "es",
  "pr",
  "it",
  "ru",
  "zh",
  "jp",
  "de",
];

export const i18n = new I18n({
  en: {
    Send: "Send",
    Paste: "Paste",
    serverIP: "Enter server's IP",
    serverPort: "Enter server's port",
    deviceName: "Enter device's name",
    changeTheme: "Change app's theme",
    resetDb: "Reset clipboard database",
    settings: "Settings",
    wsStatus: "WebSocket Status",
    wsMessage: "Websocket connection closed",
    msgDeviceName: "Please enter a device name",
    copyClip: "Copy Clip",
    openLink: "Open Link",
    resetDatabase: "Reset Database",
    resetMessage:
      "Resetting the Clips database is irreversible. Are you sure want to proceed?",
    deleteItem: "Delete Clip",
    deleteItemMessage: "Do you want to delete this clip?",
    deleteItems: "Delete Clips",
    deleteItemsMessage: "Do you want to delete these clips?",
    notif: "Notification token",
  },
  fr: {
    Send: "Envoyer",
    Paste: "Coller",
    serverIP: "Entrez l'adresse IP du serveur",
    serverPort: "Entrez le port du serveur",
    deviceName: "Entrez le nom de l'appareil",
    changeTheme: "Changer le thème de l'application",
    resetDb: "Réinitialiser la base de données du presse-papiers",
    settings: "Paramètres",
    wsStatus: "Statut WebSocket",
    wsMessage: "Connexion WebSocket fermée",
    msgDeviceName: "Veuillez entrer un nom d'appareil",
    copyClip: "Copier le clip",
    openLink: "Ouvrir le lien",
    resetDatabase: "Réinitialiser la base de données",
    resetMessage:
      "La réinitialisation de la base de données Clips est irréversible. Êtes-vous sûr de vouloir continuer ?",
    deleteItem: "Supprimer le clip",
    deleteItemMessage: "Voulez-vous supprimer ce clip?",
    deleteItems: "Supprimer les clips",
    deleteItemsMessage: "Voulez-vous supprimer ces clips?",
    notif: "Jeton de notification",
  },
  ar: {
    Send: "إرسال",
    Paste: "لصق",
    serverIP: "أدخل عنوان IP الخاص بالخادم",
    serverPort: "أدخل منفذ الخادم",
    deviceName: "أدخل اسم الجهاز",
    changeTheme: "تغيير مظهر التطبيق",
    resetDb: "إعادة تعيين قاعدة بيانات الحافظة",
    settings: "الإعدادات",
    wsStatus: "حالة WebSocket",
    wsMessage: "تم إغلاق اتصال WebSocket",
    msgDeviceName: "يرجى إدخال اسم الجهاز",
    copyClip: "نسخ المقطع",
    openLink: "فتح الرابط",
    resetDatabase: "إعادة تعيين قاعدة البيانات",
    resetMessage:
      "إعادة تعيين قاعدة بيانات Clips غير قابلة للاسترجاع. هل أنت متأكد من أنك تريد المتابعة؟",
    deleteItem: "حذف المقطع",
    deleteItemMessage: "هل تريد حذف هذا المقطع؟",
    deleteItems: "حذف المقاطع",
    deleteItemsMessage: "هل تريد حذف هذه المقاطع؟",
    notif: "رمز الإشعار",
  },
  es: {
    Send: "Enviar",
    Paste: "Pegar",
    serverIP: "Ingrese la IP del servidor",
    serverPort: "Ingrese el puerto del servidor",
    deviceName: "Ingrese el nombre del dispositivo",
    changeTheme: "Cambiar el tema de la aplicación",
    resetDb: "Restablecer la base de datos del portapapeles",
    settings: "Configuraciones",
    wsStatus: "Estado de WebSocket",
    wsMessage: "Conexión WebSocket cerrada",
    msgDeviceName: "Por favor, ingrese un nombre de dispositivo",
    copyClip: "Copiar clip",
    openLink: "Abrir enlace",
    resetDatabase: "Restablecer la base de datos",
    resetMessage:
      "Restablecer la base de datos de Clips es irreversible. ¿Está seguro de que desea continuar?",
    deleteItem: "Eliminar clip",
    deleteItemMessage: "¿Quieres eliminar este clip?",
    deleteItems: "Eliminar clips",
    deleteItemsMessage: "¿Quieres eliminar estos clips?",
    notif: "Token de notificación",
  },
  pr: {
    Send: "Enviar",
    Paste: "Colar",
    serverIP: "Digite o IP do servidor",
    serverPort: "Digite a porta do servidor",
    deviceName: "Digite o nome do dispositivo",
    changeTheme: "Mudar o tema do aplicativo",
    resetDb: "Redefinir banco de dados da área de transferência",
    settings: "Configurações",
    wsStatus: "Status do WebSocket",
    wsMessage: "Conexão WebSocket fechada",
    msgDeviceName: "Por favor, insira um nome de dispositivo",
    copyClip: "Copiar clipe",
    openLink: "Abrir link",
    resetDatabase: "Redefinir banco de dados",
    resetMessage:
      "Redefinir o banco de dados do Clips é irreversível. Tem certeza de que deseja continuar?",
    deleteItem: "Excluir clipe",
    deleteItemMessage: "Você quer excluir este clipe?",
    deleteItems: "Excluir clipes",
    deleteItemsMessage: "Você quer excluir esses clipes?",
    notif: "Token de notificação",
  },
  it: {
    Send: "Invia",
    Paste: "Incolla",
    serverIP: "Inserisci l'IP del server",
    serverPort: "Inserisci la porta del server",
    deviceName: "Inserisci il nome del dispositivo",
    changeTheme: "Cambia il tema dell'applicazione",
    resetDb: "Reimposta il database degli appunti",
    settings: "Impostazioni",
    wsStatus: "Stato WebSocket",
    wsMessage: "Connessione WebSocket chiusa",
    msgDeviceName: "Per favore, inserisci un nome del dispositivo",
    copyClip: "Copia il clip",
    openLink: "Apri il link",
    resetDatabase: "Reimposta database",
    resetMessage:
      "Reimpostare il database dei Clips è irreversibile. Sei sicuro di voler procedere?",
    deleteItem: "Elimina clip",
    deleteItemMessage: "Vuoi eliminare questo clip?",
    deleteItems: "Elimina clip",
    deleteItemsMessage: "Vuoi eliminare questi clip?",
    notif: "Token di notifica",
  },
  ru: {
    Send: "Отправить",
    Paste: "Вставить",
    serverIP: "Введите IP-адрес сервера",
    serverPort: "Введите порт сервера",
    deviceName: "Введите имя устройства",
    resetDb: "Сбросить базу данных буфера обмена",
    changeTheme: "Изменить тему приложения",
    settings: "Настройки",
    wsStatus: "Статус WebSocket",
    wsMessage: "Соединение WebSocket закрыто",
    msgDeviceName: "Пожалуйста, введите имя устройства",
    copyClip: "Копировать клип",
    openLink: "Открыть ссылку",
    resetDatabase: "Сбросить базу данных",
    resetMessage:
      "Сброс базы данных Clips необратим. Вы уверены, что хотите продолжить?",
    deleteItem: "Удалить клип",
    deleteItemMessage: "Вы хотите удалить этот клип?",
    deleteItems: "Удалить клипы",
    deleteItemsMessage: "Вы хотите удалить эти клипы?",
    notif: "Токен уведомления",
  },
  zh: {
    Send: "发送",
    Paste: "粘贴",
    serverIP: "输入服务器的IP",
    serverPort: "输入服务器的端口",
    deviceName: "输入设备名称",
    changeTheme: "更改应用主题",
    resetDb: "重置剪贴板数据库",
    settings: "设置",
    wsStatus: "WebSocket状态",
    wsMessage: "WebSocket连接已关闭",
    msgDeviceName: "请输入设备名称",
    copyClip: "复制剪辑",
    openLink: "打开链接",
    resetDatabase: "重置数据库",
    resetMessage: "重置Clips数据库是不可逆的。你确定要继续吗？",
    deleteItem: "删除剪辑",
    deleteItemMessage: "你确定要删除这个剪辑吗？",
    deleteItems: "删除剪辑",
    deleteItemsMessage: "你确定要删除这些剪辑吗？",
    notif: "通知令牌",
  },
  jp: {
    Send: "送信",
    Paste: "貼り付け",
    serverIP: "サーバーのIPを入力",
    serverPort: "サーバーのポートを入力",
    deviceName: "デバイス名を入力",
    changeTheme: "アプリのテーマを変更",
    resetDb: "クリップボードデータベースをリセット",
    settings: "設定",
    wsStatus: "WebSocketステータス",
    wsMessage: "WebSocket接続が閉じました",
    msgDeviceName: "デバイス名を入力してください",
    copyClip: "クリップをコピー",
    openLink: "リンクを開く",
    resetDatabase: "データベースをリセット",
    resetMessage:
      "Clipsデータベースのリセットは取り消しできません。本当に続行しますか？",
    deleteItem: "クリップを削除",
    deleteItemMessage: "このクリップを削除しますか？",
    deleteItems: "クリップを削除",
    deleteItemsMessage: "これらのクリップを削除しますか？",
    notif: "通知トークン",
  },
  de: {
    Send: "Senden",
    Paste: "Einfügen",
    serverIP: "Geben Sie die IP-Adresse des Servers ein",
    serverPort: "Geben Sie den Port des Servers ein",
    deviceName: "Geben Sie den Namen des Geräts ein",
    changeTheme: "App-Thema ändern",
    resetDb: "Zwischenspeicher-Datenbank zurücksetzen",
    settings: "Einstellungen",
    wsStatus: "WebSocket-Status",
    wsMessage: "WebSocket-Verbindung geschlossen",
    msgDeviceName: "Bitte geben Sie einen Gerätenamen ein",
    copyClip: "Clip kopieren",
    openLink: "Link öffnen",
    resetDatabase: "Datenbank zurücksetzen",
    resetMessage:
      "Das Zurücksetzen der Clips-Datenbank ist irreversibel. Sind Sie sicher, dass Sie fortfahren möchten?",
    deleteItem: "Clip löschen",
    deleteItemMessage: "Möchten Sie diesen Clip löschen?",
    deleteItems: "Clips löschen",
    deleteItemsMessage: "Möchten Sie diese Clips löschen?",
    notif: "Benachrichtigungstoken",
  },
});

i18n.defaultLocale = deviceLanguage;

i18n.locale = supportedLanguages.includes(deviceLanguage)
  ? deviceLanguage
  : "en";
