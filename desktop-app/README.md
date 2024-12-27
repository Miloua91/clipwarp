## Desktop app

<div align='center'>
   <img alt='ClipWarp' src='http://miloua.com/clipwarp.png'/>
</div>

Clone the repo to your machine

``` git
git clone https://github.com/Miloua91/clipwarp.git
```

Go to desktop-app directory

``` sh
cd clipwarp/desktop-app
```

Create a Python Virtual Environment:

   - Using [virtualenv](https://pypi.org/project/virtualenv/):

     _Note_: Check how to install virtualenv on your system here [link](https://learnpython.com/blog/how-to-use-virtualenv-python/).

     ```bash
     virtualenv env
     ```

   **OR**

   - Create a Python Virtual Environment:

     ```bash
     python -m venv env
     ```

Activate the Virtual Environment.

   - On Windows.

     ```bash
     env\Scripts\activate
     ```

   - On macOS and Linux.

     ```bash
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

Currently the project is being developed using Python 3.13

##### Build the desktop app

   - With [PyInstaller](https://pypi.org/project/pyinstaller/): build the app on desktop

     _Note_: Check how to use PyInstaller on your system here [link](https://pyinstaller.org/en/v4.1/usage.html).

     ```
     pyinstaller main.spec
     ```

   - Launch the app

     ```
     ./dist/ClipWarp
     ```
