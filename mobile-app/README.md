## Mobile app

Clone the repo to your machine

``` git
git clone https://github.com/Miloua91/clipwarp.git
```

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
