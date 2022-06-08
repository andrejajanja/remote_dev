import os,random,string,cv2,base64

class korisnik:
    def __init__(self, nalog: list[str]):        
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

        self.formatiranje = ""

#region FILE SYSTEM FUNKCIJE
#endregion FILE SYSTEM FUNKCIJE

def napravi_fajl(path):
    open(path,mode="w").close()

def procitaj_file_tf_format(file_path: str):
    txt = ""
    with open(file_path,"r+", encoding="UTF-8") as f:
        duz_prethodno = 0
        
        for i,l in enumerate(f.readlines()):                
            if i == 0:                    
                txt += l
                duz_prethodno = len(l)
                continue

            if l.find("accuracy:") != -1 and l.find("loss") != -1:
                txt = f"{txt[:-duz_prethodno]}{l}" 
                duz_prethodno = len(l)
                continue
            txt+= l
            duz_prethodno = len(l)
    return txt

def procitaj_file(file_path: str):
    eks = file_path[file_path.rindex(".")+1:]    
    eks_slika = ["jpg","png","jpeg","ico","bmp"]
    eks_txt = ["py","pyw","txt","html","css","js","md","xml","csv"]

    file = ""
    if eks in eks_txt:
        with open(file_path,"r+", encoding="UTF-8") as f:
            for linija in f.readlines():
                file+=linija
        return file
        
    if eks in eks_slika:
        file = cv2.imread(file_path, cv2.IMREAD_COLOR)       
        return base64.b64encode(file)
    return 0
   
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

def nasumicni_string(x: int):    
    return "".join(random.choice(string.ascii_letters) for i in range(x))

