# CAMOnion

CAMOnion is a small CAD/CAM platform for simple feature based G-code generation.
Tool, Features, Operations, Machines and Post Formats stored in an SQL database. 

Any sql database is supported, the first time running it will prompt for a URL.  
The format for the URL is [found here](https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls).
(Example sqlite url "sqlite:///C:/REPO/CAMOnion/camo.db") To build new empty sqlite database configure the file build_db.py
with desired location and run it. 
The database will need to be populated before any code can parts can be programmed.

## Environment and Installation

Be sure python 3.8 is installed an set in PATH

```bash
git clone --recurse-submodules https://github.com/JonRob812/CAMOnion
cd CAMOnion
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
mkdir CAMOnion\resources\
mkdir CAMOnion\ui
cp BreezeStyleSheets\breeze_resources.py CAMOnion\resources\breeze_resources.py
make resource
make ui
```

remove line 30 and line 66 from CAMOnion/app.py (that is for quickbase integration)

Building DB file (SQLITE)

```bash
python build_db.py
```

## Usage

```bash
venv\Scripts\activate.bat
python main.py
```

## EXE and Installer
Configure Makefile for file locations, Install Inno Setup and add to path. Configure CAMOnion.spec file. To make exe
run 
```bash
make exe
```
or to make installer run (need Inno Setup)
```bash\
make installer
``` 

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)