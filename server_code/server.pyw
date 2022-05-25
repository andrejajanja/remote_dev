from flask import Flask, jsonify, redirect,request, render_template,make_response
import os,shutil,hashlib,random,string,csv,sys
from waitress import serve
from paste.translogger import TransLogger  
from subprocess import Popen
from ua_parser import user_agent_parser
from infi.systray import SysTrayIcon

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

#region serverske promenljive
app = Flask(__name__)
serverski_path = r"E:\remote_dev_server_data"
for x in os.listdir(f"{serverski_path}/tekst_fajlovi"):
    os.remove(f"{serverski_path}/tekst_fajlovi/{x}")
hash_user, hash_pass = ucitaj_hash_user_pass(f"{serverski_path}/nalozi.csv")
lokacija_od_pythona = f"{os.path.dirname(sys.executable)}\{os.path.basename(sys.executable)}"
svi_sesijski_podaci = ucitaj_sve_sesijske_podatke(f"{serverski_path}/seijsi_podaci.csv")
ulogovani = {}
sesije = {}
#endregion serverske promenljive

jeste_debug = False

def say_hello(systray):
    os._exit(1)

def ugasi_program(systray):
    os._exit(1)

opcije = (("Gasi ga i na dvoklik na tray ikonicu", None, say_hello),)
trag = SysTrayIcon("static/images/ikonica.ico", "Remote_dev", opcije, on_quit=ugasi_program)

#region stranice
@app.route('/', methods=['GET', 'POST'])
def login():
    #agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent'))
    #print(agent_korisnika)
    if request.method == "POST":
        komande = list(request.form.keys())
        uraditi = list(request.form.values())
        if "login" in komande:
            if (str(uraditi[1]) in hash_user) and (str(uraditi[2]) in hash_pass):                
                odgovor = make_response(jsonify({"autentifikacija":"uspesna"}))
                idkorisnika = nasumicni_string(10)
                sesije[idkorisnika] = ucitaj_sesiju([uraditi[1],uraditi[2]])                
                odgovor.set_cookie("nalog", f"{uraditi[1]} {uraditi[2]}",max_age=3600, httponly=True) #1h kolacic
                return odgovor
            return jsonify({"autentifikacija":"neuspesna"})
    if request.method == "GET":
        if "nalog" in request.cookies.keys():
            userpass = request.cookies["nalog"].split(" ")            
            try:
                userh = userpass[0]
                passh = userpass[1]
                if (userh not in hash_user) or (passh not in hash_pass):
                    raise Exception("nije nadjen hash")
            except:                
                return render_template("login.html")            
            return redirect("/coding")
        else:
            return render_template("login.html")

@app.route('/coding', methods=['GET', 'POST'])
def kodiranje():        
    if request.method=="POST":
        komande = list(request.form.keys())
        uraditi = list(request.form.values())
        idkorisnika = request.cookies["sesijskiID"]
        if "kontrola" in komande:            
            if "zaustavi" in uraditi:                                
                sesije[idkorisnika]["proces"].terminate()
                return jsonify({"rezultat": "uspesno"})   

            if "izvrsi" in uraditi:                                            
                if ".py" not in sesije[idkorisnika]["trenutni_file"]:                    
                    return jsonify({"konzola": 0})
                sesije[idkorisnika]["proces"] = Popen([lokacija_od_pythona, "-u", sesije[idkorisnika]["trenutni_file"]], stdout=open(f'{serverski_path}/tekst_fajlovi/{idkorisnika}.txt', 'w+'), cwd=sesije[idkorisnika]["root_fold"])                
                return jsonify({"konzola": f'root_fold{sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):]}>\n'})

            if "proveri_konzolu" in uraditi:
                sesije[idkorisnika]["konzola"] = procitaj_file(f'{serverski_path}/tekst_fajlovi/{idkorisnika}.txt')                     
                if sesije[idkorisnika]["proces"].poll() == 0:
                    os.remove(f"{serverski_path}/tekst_fajlovi/{idkorisnika}.txt")                    
                    sesije[idkorisnika]["proces"] = ""
                    return jsonify({"konzola": sesije[idkorisnika]["konzola"], "nastavi": False})
                else:                    
                    return jsonify({"konzola": sesije[idkorisnika]["konzola"], "nastavi": True})
                            
            if "sacuvaj" in uraditi and "." in sesije[idkorisnika]["trenutni_file"]:                
                sesije[idkorisnika]["kod_povrsina"] = request.form["code"]                            
                with open(sesije[idkorisnika]["trenutni_file"],"w+", encoding="UTF-8") as f:                    
                    f.write(sesije[idkorisnika]["kod_povrsina"])
                return jsonify({"status": 1})
            else:
                return jsonify({"status": 0})
                                    
        if "izloguj" in komande:
            ulogovani[request.cookies["nalog"]]["broj_uredjaja"] -= 1
            if ulogovani[request.cookies["nalog"]]["broj_uredjaja"] == 0:
                ulogovani.pop(request.cookies["nalog"], None)                
                sesije.pop(idkorisnika, None)
            odgovor = make_response(jsonify({"poruka": "uspesno"}))
            odgovor.set_cookie("sesijskiID", idkorisnika,max_age=0, httponly=True)
            odgovor.set_cookie("nalog", "",max_age=0, httponly=True)
            return odgovor               
        return odgovor
    elif request.method=="GET":        
        agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent'))        

        kljucevi =list(request.cookies.keys())        
        if "nalog" in kljucevi:            
            userpass = request.cookies["nalog"].split(" ")            
            try:
                userh = userpass[0]
                passh = userpass[1]
                if (userh not in hash_user) or (passh not in hash_pass):
                    raise Exception("nije nadjen hash")
            except:
                return redirect("/")
             
            #lokalne varijable
            nas,tren_file = "Remote_dev",""
            sesija_povrsina = [] #u ovu listu se smestaju vrednosti za, redom: coding povrsinu, idkorisnika cookie                                                    
            if request.cookies["nalog"] in list(ulogovani.keys()):                                                                
                if "sesijskiID" in kljucevi:                    
                    if not request.cookies["sesijskiID"] == ulogovani[request.cookies["nalog"]]["trenutni_id"]:
                        sesija_povrsina = [sesije[ulogovani[request.cookies["nalog"]]["trenutni_id"]]["kod_povrsina"],ulogovani[request.cookies["nalog"]]["trenutni_id"]]                                                              
                        ulogovani[request.cookies["nalog"]]["broj_uredjaja"] += 1
                        tren_file = sesije[ulogovani[request.cookies["nalog"]]["trenutni_id"]]["trenutni_file"][len(sesije[ulogovani[request.cookies["nalog"]]["trenutni_id"]]["root_fold"]):]
                    else:        
                        sesija_povrsina = [sesije[request.cookies["sesijskiID"]]["kod_povrsina"],""]
                        tren_file =  sesije[request.cookies["sesijskiID"]]["trenutni_file"][len(sesije[request.cookies["sesijskiID"]]["root_fold"]):]                               
                else:
                    sesija_povrsina = [sesije[ulogovani[request.cookies["nalog"]]["trenutni_id"]]["kod_povrsina"], ulogovani[request.cookies["nalog"]]["trenutni_id"]]                    
                    ulogovani[request.cookies["nalog"]]["broj_uredjaja"] += 1
                    tren_file = sesije[ulogovani[request.cookies["nalog"]]["trenutni_id"]]["trenutni_file"][len(sesije[ulogovani[request.cookies["nalog"]]["trenutni_id"]]["root_fold"]):]
            else:                
                idkorisnika = nasumicni_string(10)
                ulogovani[request.cookies["nalog"]] = {}
                ulogovani[request.cookies["nalog"]]["trenutni_id"] = idkorisnika
                ulogovani[request.cookies["nalog"]]["broj_uredjaja"] = 1                
                sesije[idkorisnika] = ucitaj_sesiju(request.cookies["nalog"].split(" "))
                sesija_povrsina = [sesije[idkorisnika]["kod_povrsina"],idkorisnika]
                tren_file = sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):]

            #obrada monitora za trenutni file
            if not len(tren_file) == 0:
                tren_file = tren_file.split("/")[-1]
                nas = tren_file

            #desktop ili mobile html  
            if agent_korisnika["os"]["family"] in ["Windows","macos","Linux"]:
                ime_html_fajla = "coding_desktop"                
            elif agent_korisnika["os"]["family"] in ["Android","ios"]:
                ime_html_fajla = "coding_mobile"

            #pravljenje odgovora
            odgovor =  make_response(render_template(ime_html_fajla + ".html", kdp = sesija_povrsina[0], naslov =nas, konzolica = tren_file))                        
            if not sesija_povrsina[1] == "":
                odgovor.set_cookie("sesijskiID", sesija_povrsina[1],httponly= True)
            return odgovor                        
        else:            
            return redirect("/")
            
@app.route('/file_explorer', methods=["GET","POST"])
def menadzer():    
    if request.method=="POST":
        komande = request.form.keys()
        uraditi = list(request.form.values())  
        idkorisnika = request.cookies["sesijskiID"]
        if "akcija" in komande:
            if "obrisi" in uraditi:                    
                if "." in sesije[idkorisnika]["trenutni_file"].split("/")[-1]:
                    sesije[idkorisnika]["kod_povrsina"], sesije[idkorisnika]["konzola"] = "",""
                    os.remove(sesije[idkorisnika]["trenutni_file"])
                    sesije[idkorisnika]["fajlovi"].pop(sesije[idkorisnika]["index_trenutnog"])                    
                else:
                    shutil.rmtree(sesije[idkorisnika]["trenutni_file"])
                    pom_index = sesije[idkorisnika]["index_trenutnog"]+1
                    try:
                        while not sesije[idkorisnika]["fajlovi"][pom_index][3] == sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][3]:                        
                            pom_index+=1                   
                        sesije[idkorisnika]["fajlovi"] = sesije[idkorisnika]["fajlovi"][0:sesije[idkorisnika]["index_trenutnog"]] + sesije[idkorisnika]["fajlovi"][pom_index:]
                    except:
                        sesije[idkorisnika]["fajlovi"] = sesije[idkorisnika]["fajlovi"][0:sesije[idkorisnika]["index_trenutnog"]]  
                sesije[idkorisnika]["trenutni_file"] = lista_u_string(sesije[idkorisnika]["trenutni_file"].split("/")[:-1],"/")[:-1]                
                sesije[idkorisnika]["index_trenutnog"] = vrati_element_po_adresi(sesije[idkorisnika]["fajlovi"],"root_fold" + sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):])                
                
            if 'napravi' in uraditi:                    
                if "." in sesije[idkorisnika]["trenutni_file"]:
                    p = f'{lista_u_string(sesije[idkorisnika]["trenutni_file"].split("/")[:-1],"/")[:-1]}/{uraditi[1]}'
                    sesije[idkorisnika]["fajlovi"].insert(sesije[idkorisnika]["index_trenutnog"]+1,["white",uraditi[1],"root_fold" + p[len(sesije[idkorisnika]["root_fold"]):], sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][3]])
                else:
                    p = f'{sesije[idkorisnika]["trenutni_file"]}/{uraditi[1]}'
                    sesije[idkorisnika]["fajlovi"].insert(sesije[idkorisnika]["index_trenutnog"]+1,["white",uraditi[1],"root_fold" + p[len(sesije[idkorisnika]["root_fold"]):], sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][3]+1])

                if "." in uraditi[1]:
                    napravi_fajl(p) 
                else:
                    os.mkdir(p)
            return jsonify({"fajlovi": sesije[idkorisnika]["fajlovi"],"trenutni_fajl": "root_fold" + sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):]})
                
        if "lokacija" in komande:
            if request.form["lokacija"] == "root_fold":                
                sesije[idkorisnika]["trenutni_file"] = sesije[idkorisnika]["root_fold"]
                sesije[idkorisnika]["kod_povrsina"] = ""
                sesije[idkorisnika]["fajlovi"] = [["white", x, f'root_fold\{x}', 1] for x in os.listdir(sesije[idkorisnika]["root_fold"])]
                sesije[idkorisnika]["fajlovi"] = [[sesije[idkorisnika]["select_color"], "root", "root_fold", 0],*sesije[idkorisnika]["fajlovi"]]
                sesije[idkorisnika]["index_trenutnog"] = 0
                return jsonify({"fajlovi": sesije[idkorisnika]["fajlovi"],"trenutni_fajl": "root_fold"})

            sesije[idkorisnika]["trenutni_file"] = sesije[idkorisnika]["root_fold"]+ request.form["lokacija"][9:]              
            ime_file = sesije[idkorisnika]["trenutni_file"].split("/")[-1] 
            stari_index = sesije[idkorisnika]["index_trenutnog"]            
            sesije[idkorisnika]["index_trenutnog"] = vrati_element_po_adresi(sesije[idkorisnika]["fajlovi"],f'root_fold{sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):]}')
            b = sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][0] 

            if "." in ime_file: 
                if b == "white":
                    sesije[idkorisnika]["konzola"] = ""
                    sesije[idkorisnika]["kod_povrsina"] = procitaj_file(sesije[idkorisnika]["trenutni_file"])
                    sesije[idkorisnika]["fajlovi"] = ukloni_boje_svih_datoteka(sesije[idkorisnika]["fajlovi"])
                    sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][0] = sesije[idkorisnika]["select_color"]   
                    return jsonify({"fajlovi": sesije[idkorisnika]["fajlovi"],"trenutni_fajl": "root_fold" + sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):], "prebaci": "da", "code": sesije[idkorisnika]["kod_povrsina"]})
                else:
                    sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][0] = "white"
                    sesije[idkorisnika]["kod_povrsina"] = ""   
            else:
                if b == "white":
                    sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][0] = sesije[idkorisnika]["select_color"]
                    if "." in sesije[idkorisnika]["fajlovi"][stari_index][1]:
                        sesije[idkorisnika]["fajlovi"][stari_index][0] = "white"
                    for file in os.listdir(sesije[idkorisnika]["trenutni_file"]):
                        sesije[idkorisnika]["fajlovi"].insert(sesije[idkorisnika]["index_trenutnog"]+1,["white", file, f'root_fold{sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):]}/{file}', sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][3]+1])                
                else:
                    sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][0] = "white"
                    sesije[idkorisnika]["trenutni_file"] = lista_u_string(sesije[idkorisnika]["trenutni_file"].split("/")[:-1],"/")[:-1]
                    pom_index = sesije[idkorisnika]["index_trenutnog"]+1
                    try:
                        while not sesije[idkorisnika]["fajlovi"][pom_index][3] == sesije[idkorisnika]["fajlovi"][sesije[idkorisnika]["index_trenutnog"]][3]:                        
                            pom_index+=1                   
                        sesije[idkorisnika]["fajlovi"] = sesije[idkorisnika]["fajlovi"][0:sesije[idkorisnika]["index_trenutnog"]+1] + sesije[idkorisnika]["fajlovi"][pom_index:]
                    except:
                        sesije[idkorisnika]["fajlovi"] = sesije[idkorisnika]["fajlovi"][0:sesije[idkorisnika]["index_trenutnog"]+1]
            return jsonify({"fajlovi": sesije[idkorisnika]["fajlovi"],"trenutni_fajl": "root_fold" + sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):],"code": sesije[idkorisnika]["kod_povrsina"]})

        if "dinamicki_elememnti" in komande:
            return jsonify({"fajlovi": sesije[idkorisnika]["fajlovi"],"trenutni_fajl": "root_fold" + sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):]})


    elif request.method=="GET":
        kljucevi =list(request.cookies.keys())
        agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent'))
        if agent_korisnika["os"]["family"] in ["Windows","macos","Linux"]:
            return redirect("/coding")
                                        
        if "nalog" in kljucevi:
            userpass = request.cookies["nalog"].split(" ")            
            try:
                userh = userpass[0]
                passh = userpass[1]
                if (userh not in hash_user) or (passh not in hash_pass):
                    raise Exception("nije nadjen hash")
            except:
                return redirect("/") 
            kolac = ""                 
            if request.cookies["nalog"] in list(ulogovani.keys()):                                                                
                if "sesijskiID" in kljucevi:                    
                    if not request.cookies["sesijskiID"] == ulogovani[request.cookies["nalog"]]["trenutni_id"]:
                        kolac = ulogovani[request.cookies["nalog"]]["trenutni_id"]
                        ulogovani[request.cookies["nalog"]]["broj_uredjaja"] += 1                                              
                else:
                    kolac = ulogovani[request.cookies["nalog"]]["trenutni_id"]
                    ulogovani[request.cookies["nalog"]]["broj_uredjaja"] += 1                    
            else:                
                idkorisnika = nasumicni_string(10)
                ulogovani[request.cookies["nalog"]] = {}
                ulogovani[request.cookies["nalog"]]["trenutni_id"] = idkorisnika
                ulogovani[request.cookies["nalog"]]["broj_uredjaja"] = 1                
                sesije[idkorisnika] = ucitaj_sesiju(request.cookies["nalog"].split(" "))
                kolac = idkorisnika
            odgovor = make_response(render_template("file_manager.html"))  
            if not kolac == "":
                odgovor.set_cookie("sesijskiID", kolac,httponly= True)                    
            return odgovor
        else:            
            return redirect("/")

#error 404 handling
@app.errorhandler(404)
def nenadjena_stranica(e):
    return render_template("404.html"),404

#endregion stranice
if __name__=="__main__":        
    #app.run(port = 5000)
    trag.start()
    serve(TransLogger(app, setup_console_handler=False, logger_name="Remote_dev", format = ('[%(time)s] Metod: %(REQUEST_METHOD)s Status: %(status)s\tVelicina: %(bytes)s [bytes]\tTrazeno: %(REQUEST_URI)s')),host='0.0.0.0', port=5000, url_scheme = "https")
    trag.shutdown()