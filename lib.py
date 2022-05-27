import sqlite3,os,random,string

class korisnik:
    def __init__(self, nalog: list):        
        self.proces = ""
        self.index_trenutnog = 0
        self.kod_povrsina = ""
        self.konzola = ""
        self.trenutni_file = nalog[3]
        self.select_color = nalog[4] #boja kojom se boje selektovani fajlovi/folderi
        self.root_fold = nalog[3]

        fajlovi = [["white", x, f"root_fold/{x}", 1] for x in os.listdir(nalog[3])]
        fajlovi = [[nalog[4], "root", "root_fold", 0],*fajlovi]
        self.fajlovi = fajlovi


#region nalog funkcije
def obrisi_sve_iz_trenutni_ulogovani():
    konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
    kursor = konekcija.cursor() 
    kursor.execute('''
        DELETE FROM trenutni_ulogovani;
    ''')

    konekcija.commit()
    konekcija.close()

def sql_select_u_listu(query):
    konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
    kursor = konekcija.cursor()    
    kursor.execute(query)
    pom = []
    for x in kursor.fetchall():
        pom.append(list(x))

    konekcija.close()
    if pom == []:
        return False
    else:
        return pom

def da_li_je_vec_ulogovan(username,password):
    konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
    kursor = konekcija.cursor()    

    kursor.execute('''
        select id_korisnika
        from trenutni_ulogovani
        where ime = ? and pass = ?;
    ''', (username,password))
    pom = []
    for x in kursor.fetchall():
        pom.append(list(x))    
    konekcija.close()
    if pom == []:
        return False
    else:
        return True

def pokusaj_login(username, password):
    '''
    @todo #2 sql kod da vraca true ili false automatski
    '''
    konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
    kursor = konekcija.cursor() 
    kursor.execute('''
        select *
        from Korisnici
        where ime = ? and pass = ?;
    ''', (username,password))
    nalog = list(kursor.fetchall())
    konekcija.close()
    if nalog == []:
        return False
    else:
        return nalog[0]

def ulogovani_tabela(idkorisnika, ime, passw):
    konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
    kursor = konekcija.cursor() 
    kursor.execute('''
        INSERT INTO trenutni_ulogovani
        VALUES (?,?,?);
    ''', (idkorisnika, ime, passw))
    konekcija.commit()    
    konekcija.close()

def izloguj_korisnika(idkorisnika):
    konekcija = sqlite3.connect(r"E:\remote_dev_server_data\baza.mdf")
    kursor = konekcija.cursor() 
    kursor.execute("DELETE FROM trenutni_ulogovani where id_korisnika = ?;", (idkorisnika))
    konekcija.commit()    
    konekcija.close()

#endregion nalog funkcije

#region FILE SYSTEM FUNKCIJE
def napravi_fajl(path):
    open(path,mode="w").close()

def procitaj_file(file_path):
    file_string = ""
    f = open(file_path,"r+", encoding="UTF-8")
    for linija in f.readlines():
        file_string+=linija
    f.close()
    return file_string

def lista_u_string(lista, dodatak:str):
    pom = ""
    for x in lista:
        pom+=f"{x}{dodatak}"
    return pom    

def kreiraj_folder_listu(path):
    folderi_ime = [x for x in os.listdir(path)]
    folderi = [["white",x] for x in folderi_ime]
    return folderi, folderi_ime

def ukloni_boje_svih_datoteka(lista):
    for i, elem in enumerate(lista):
        if "." in elem[1]:            
            lista[i][0] = "white"
    return lista

def vrati_element_po_adresi(lista, adresa_elementa):
    for i, elem in enumerate(lista):        
        if elem[2] == adresa_elementa:            
            return i

#endregion FILE SYSTEM FUNKCIJE

def nasumicni_string(x: int):    
    return "".join(random.choice(string.ascii_letters) for i in range(x))