import sqlite3


def obrisi_sve_iz_trenutni_ulogovani():
    konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
    kursor = konekcija.cursor() 
    kursor.execute('''
        DELETE FROM trenutni_ulogovani;
    ''')

    konekcija.commit()
    konekcija.close()



konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
kursor = konekcija.cursor() 
kursor.execute('''
    CREATE TABLE trenutni_ulogovani(
    id_korisnika char(10) PRIMARY KEY,
    ime varchar(255),
    pass varchar(255)
);
''')

konekcija.commit()
konekcija.close()
