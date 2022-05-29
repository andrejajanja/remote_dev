import sqlite3

konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
kursor = konekcija.cursor() 
kursor.execute('''
    select *
    from Korisnici;
''')

for nalog in kursor.fetchall():
    print(nalog)

konekcija.close()
