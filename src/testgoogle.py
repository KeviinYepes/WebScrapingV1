from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

file1 = drive.CreateFile({"tittle":"kevin.txt"}) #Create the file in GoogleDrive
file1.setContentString("Prueba drive") #Set content of 
file1.Upload()