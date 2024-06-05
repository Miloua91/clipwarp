## Desktop app

Clone the repo to your machine

``` git
git clone https://github.com/Miloua91/clipwarp.git
```

Go to desktop-app directory

``` sh
cd clipwarp/desktop-app
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
