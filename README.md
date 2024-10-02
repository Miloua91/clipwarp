<div align="center">
<a href="https://clipwarp.vercel.app" >
   <img src="./desktop-app/assets/cw.ico" alt="Logo" width="100" height="100">
</a>

# ClipWarp

[![product-screenshot]](https://clipwarp.vercel.app)

</div>

## Elevator pitch

Ever get frustrated trying to share links or text between your desktop and phone? It's a common inconvenience we all face. You have a link on your desktop, therefore you'd think it would be easy to get it on your phone, but it's always more complicated than it should be.

That's where ClipWarp comes in. Install it on both devices, and you’ll have a simple way to manage links and text across platforms without the extra steps.

<div align="center">

![example-screenshot]

An instance where you need to send a link to your device, screenshot from Expo documentation. If it's up to me, then I will definitely use ClipWarp.

</div>

## Installation

### Windows 10/11

1. Download [clipwarp-0.1.0.exe](https://github.com/Miloua91/clipwarp/releases/download/v0.1.0/clipwarp-0.1.0.exe).
2. Install the app.
3. Launch it.

### Linux (x64)

#### Tarball

1. Download [clipwarp-0.1.0.tar.gz](https://github.com/Miloua91/clipwarp/releases/download/v0.1.0/clipwarp-0.1.0.tar.gz).
2. Extract it: 
   ```sh
   tar xzvf clipwarp-0.1.0.tar.gz
   ```
3. Create an assets directory: 
   ```sh
   mkdir ~/.config/clipwarp/assets
   ```
4. Run the app: 
   ```sh
   ./clipwarp/ClipWarp
   ```

#### Arch Linux

1. Download the [PKGBUILD](https://github.com/Miloua91/clipwarp/releases/download/v0.1.0/PKGBUILD).
2. Install the app: 
   ```sh
   makepkg -si
   ```
3. Launch the app: 
   ```sh
   clipwarp
   ```

### Android

1. Download the [APK file](https://github.com/Miloua91/clipwarp/releases/download/v0.1.0/clipwarp-1.0.0.apk).
2. Install it on your device.
3. Launch the app.

## Get the source code

Clone the repository:

```sh
git clone https://github.com/Miloua91/clipwarp.git
```

### Desktop App

1. Go to the `desktop-app` directory:
   ```sh
   cd clipwarp/desktop-app
   ```

2. Create a virtual environment:
   ```sh
   python -m venv env .
   ```

3. Activate the virtual environment:
   ```sh
   source env/bin/activate
   ```

4. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

5. Launch the app:
   ```sh
   python main.py
   ```

#### Build the Desktop App with PyInstaller

1. Build the app:
   ```sh
   pyinstaller main.spec
   ```

2. Launch the app:
   ```sh
   ./dist/ClipWarp
   ```

### Mobile App

1. Go to the `mobile-app` directory:
   ```sh
   cd clipwarp/mobile-app
   ```

2. Install the packages:
   ```sh
   yarn install
   ```

3. Start the development server:
   ```sh
   yarn expo start
   ```

#### Build the Mobile App

1. Install EAS CLI if you don't have it:
   ```sh
   npm install --global eas-cli
   ```

2. Build the app:
   ```sh
   eas build -p android --profile preview
   ```

### Web App

1. Go to the `web-app` directory:
   ```sh
   cd clipwarp/web-app
   ```

2. Install the packages:
   ```sh
   npm install
   ```

3. Start the server:
   ```sh
   npm run dev
   ```

#### Build the Web App

1. Build the app:
   ```sh
   npm run build
   ```

[product-screenshot]: ./presentation.png
[example-screenshot]: ./example.png
