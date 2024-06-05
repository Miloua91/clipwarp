<div align="center">
<a href="https://clipwarp.vercel.app" >
   <img src="./desktop-app/assets/cw.ico" alt="Logo" width="100" height="100">
</a>

# ClipWarp

[![product-screenshot]](https://clipwarp.vercel.app)

</div>

## Elevator pitch

Ever get frustrated trying to share links or text between your desktop and phone? ClipWarp makes it super easy. Just install it on both devices, and you’ll have a simple way to manage links and text across platforms without any hassle.

<div align="center">

![example-screenshot]

An instance where you need to send a link to your device, screenshot from Expo documentation. If it's up to me than I will definitely use ClipWarp.

</div>


## Installation

### Linux (x64)

#### Tarball

1. Download [clipwarp-0.1.0.tar.gz](https://github.com/Miloua91/clipwarp/releases/download/v0.1.0/clipwarp-0.1.0.tar.gz)
2. Extract: ```tar xzvf clipwarp-0.1.0.tar.gz```
3. Create an assets directory: ```mkdir ~/.config/clipwarp/assets```
4. Run ```./clipwarp/ClipWarp```

#### Arch Linux

1. Download [PKGBUILD](https://github.com/Miloua91/clipwarp/releases/download/v0.1.0/PKGBUILD)
2. Install the app ```makepkg -si```
3. Launch the app ```clipwarp```

### Android

1. Download the [APK file](https://github.com/Miloua91/clipwarp/releases/download/v0.1.0/clipwarp-0.1.0.apk)
2. Install it on your device
3. Profit

## Get the source code

Clone the repo to your machine

``` git
git clone https://github.com/Miloua91/clipwarp.git
```

### Desktop App

Go to desktop-app directory

``` sh
cd clipwarp/desktop-app
```

Create a virtual environment

```
python -m venv env .
```

Activate the virtual environment

```
source env/bin/activate
```

Install the python packages

``` python
pip install -r requirements.txt
```

Lunch the app

``` python
python main.py
```

##### Build the desktop app

With PyInstaller build the app on desktop

```
pyinstaller main.spec
```

Launch the app

```
./dist/ClipWarp
```

### Mobile app

Go to mobile-app directory

``` sh
cd clipwarp/mobile-app
```

Install the packages with yarn

``` sh 
yarn install
```

Start the development server 

``` sh 
yarn expo start
```

##### Build the mobile app

With Expo and EAS build the APK, Install EAS CLI if you don't have it

``` 
npm install --global eas-cli
```

Build the app 

```
eas build -p android --profile preview
```

### Web app

Go to web-app directory

``` sh
cd clipwarp/web-app
```

Install the packages with npm 

``` sh 
npm install
```

Start the server 

``` sh 
npm run dev
```

##### Build the web app

Build this command

```
npm run build
```

[product-screenshot]: ./presentation.png
[example-screenshot]: ./example.png
