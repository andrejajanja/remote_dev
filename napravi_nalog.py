import sqlite3,hashlib,os,random,string

ime = input("Unesite korisnicko ime: ")
password = input("Unesite korisnicko ime: ")

passw = hashlib.md5(password.encode()).hexdigest()

#print(passw)
#exit()

fold = r'E:\remote_dev_server_data\korisnicki_folderi'

fold = os.path.join(fold, "".join(random.choice(string.ascii_letters) for i in range(15)))
os.mkdir(fold)
os.mkdir(os.path.join(fold, "datoteka"))
open(os.path.join(fold, "skripta.py"), mode = "w").close()

konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
kursor = konekcija.cursor()
kursor.execute(r'''
INSERT INTO Korisnici
VALUES (NULL, ?, ?, ?,"rgb(171, 248, 194)");
''', (ime, passw,fold)
)
konekcija.commit()
konekcija.close()