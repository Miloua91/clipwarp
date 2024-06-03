# ClipWarp

## Elevator pitch

Ever get frustrated trying to share links or text between your desktop and phone? ClipWarp makes it super easy. Just install it on both devices, and you’ll have a simple way to manage links and text across platforms without any hassle.

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

1. Download the APK file
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
