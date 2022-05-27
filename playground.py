
import sqlite3

konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
kursor = konekcija.cursor()
kursor.execute(r'''
select pass from Korisnici;
'''
)

for red in kursor.fetchall():
    print(red)

konekcija.close()