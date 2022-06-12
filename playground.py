from subprocess import run, Popen
import os
from time import sleep
from lib import procitaj_file

kljuc_korisnika = "text_file"
serverski_path = os.getcwd()

with open(f'{serverski_path}/{kljuc_korisnika}.txt', 'w+') as f:
    proces = Popen("ipconfig /all", stdout=f,stderr=f, shell= True, text= True)


while(True):
    konzola = procitaj_file(f'{serverski_path}/{kljuc_korisnika}.txt')
    print(konzola)   
    if proces.poll() == 0:
        #os.remove(f"{serverski_path}/{kljuc_korisnika}.txt")                                            
        break         
    sleep(1)