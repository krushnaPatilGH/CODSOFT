# Python based GUI calculator with modern design

## Installation
### Requirements
```powershell
PS C:\Project> pip install -r requirements.txt
```
### Execute using python
```powershell
PS C:\Project> python main.py
```
### Export as an executable 
```powershell
PS C:\Project> pyinstaller --onefile --windowed -i calc_icon.ico -n calculator.exe main.py
```
Exported file can be found under dist/calculator.exe 