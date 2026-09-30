Set shell = CreateObject("WScript.Shell")

shell.CurrentDirectory = "C:\SIS_APOIO\casa-apoio"

python = "C:\SIS_APOIO\casa-apoio\venv\Scripts\python.exe"
manage = "C:\SIS_APOIO\casa-apoio\manage.py"

shell.Run """" & python & """ """ & manage & """ runserver 127.0.0.1:8000", 0, False

WScript.Sleep 3000

shell.Run "http://casadeapoio.local:8000/", 1, False