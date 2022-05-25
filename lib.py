import csv,hashlib,os,random,string

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

#region FUNKCIJE ZA RAD SA NALOZIMA i sesijama

def ucitaj_sesiju(userpass: list):
    global hash_user, svi_sesijski_podaci
    ses = {}    
    pom = svi_sesijski_podaci[hash_user.index(userpass[0])]

    fajlovi = [["white", x, f"root_fold/{x}", 1] for x in os.listdir(pom[0])]
    fajlovi = [[pom[1], "root", "root_fold", 0],*fajlovi]
    ses["fajlovi"] = fajlovi
    ses["root_fold"] = pom[0]
    ses["select_color"] = pom[1]
    ses["konzola"] = ""
    ses["kod_povrsina"] = ""
    ses["trenutni_file"] = pom[0]
    ses["index_trenutnog"] = 0
    ses["proces"] = ""
    return ses

def ucitaj_hash_user_pass(path_do_csv):
    hash_user,hash_pass =[],[]
    with open(path_do_csv, "r+") as file:
                citac = csv.reader(file)
                zaglavlje = next(citac)
                for red in citac:
                    hash_user.append(red[0]) 
                    hash_pass.append(red[1])
    return hash_user,hash_pass

def ucitaj_sve_sesijske_podatke(path_do_csv):
    podaci = []
    with open(path_do_csv, "r+") as file:
        citac = csv.reader(file)
        zaglavlje = next(citac)
        for red in citac:
            podaci.append(red)            
    return podaci
#endregion FUNKCIJE ZA RAD SA NALOZIMA i sesijama

#region korisne male funkcije
def encrypt(plaintext: str):
    return hashlib.md5(plaintext.encode()).hexdigest()

def nasumicni_string(x: int):    
    return "".join(random.choice(string.ascii_letters) for i in range(x))

#endregion korisne male funkcije