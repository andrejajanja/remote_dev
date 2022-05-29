from flask import Flask, jsonify, redirect,request, render_template,make_response
import os,shutil,hashlib,random,string,csv,sys
from waitress import serve
from paste.translogger import TransLogger  
from subprocess import Popen
from ua_parser import user_agent_parser
from infi.systray import SysTrayIcon
from lib import *

#region tray ikonica
def napravi_nalogg(systray):
    '''
    @todo #1
    '''
    Popen([lokacija_od_pythona,"napravi_nalog.py"])

def ugasi_program(systray):
    os._exit(1)

opcije = (("Napravi novi nalog", None, napravi_nalogg),)
trag = SysTrayIcon("static/images/ikonica.ico", "Remote_dev", opcije, on_quit=ugasi_program)
#endregion tray ikonica

#region serverske promenljive
app = Flask(__name__)
vreme_kolacic = 7200 #2h traju kolacici na sajtu
serverski_path = r"E:\remote_dev_server_data"
lokacija_od_pythona = f"{os.path.dirname(sys.executable)}\{os.path.basename(sys.executable)}"
ulogovani = {}
sesije = {}

obrisi_sve_iz_trenutni_ulogovani()
#endregion serverske promenljive
jeste_debug = False



#region stranice
@app.route('/', methods=['GET', 'POST'])
def login():
    #agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent'))
    #print(agent_korisnika)
    if request.method == "POST":
        komande = list(request.form.keys())
        uraditi = list(request.form.values())
        if "login" in komande:

            #provera da li je ulogovan na nekom drugom uredjaju            
            if da_li_je_vec_ulogovan(str(uraditi[1]),str(uraditi[2])):
                odgovor = make_response(jsonify({"autentifikacija":"uspesna"}))
                ulogovani[idkorisnika] += 1
                odgovor.set_cookie("kluc_sesija", idkorisnika,max_age=vreme_kolacic, httponly=True)
                return odgovor

            #pokusaj logina, ako krerencijali ne valjaju, vraca poruku
            nalog = pokusaj_login(str(uraditi[1]),str(uraditi[2]))
            if nalog == False:
                return jsonify({"autentifikacija":"neuspesna"})

            #stavlja kolacic i ucitava nalog ukoliko je login uspesan
            odgovor = make_response(jsonify({"autentifikacija":"uspesna"}))
            idkorisnika = nasumicni_string(10)
            ulogovani[idkorisnika] = 1
            sesije[idkorisnika] = korisnik(nalog)

            #ubacivanje u tabela sa uspesno ulogovanim
            ulogovani_tabela(idkorisnika,str(uraditi[1]),str(uraditi[2]))
            odgovor.set_cookie("kluc_sesija", idkorisnika,max_age=vreme_kolacic, httponly=True)
            return odgovor
            
    if request.method == "GET":
        if "kluc_sesija" in request.cookies.keys():            
            if request.cookies["kluc_sesija"] in ulogovani.keys():
                return redirect("/coding")
        return render_template("login.html")

@app.route('/coding', methods=['GET', 'POST'])
def kodiranje():        
    if request.method=="POST":
        komande = list(request.form.keys())
        uraditi = list(request.form.values())
        idkorisnika = request.cookies["kluc_sesija"]
        if "kontrola" in komande:            
            if "zaustavi" in uraditi:                         
                sesije[idkorisnika].proces.terminate()
                return jsonify({"rezultat": "uspesno"})   

            if "izvrsi" in uraditi:                                            
                if ".py" not in sesije[idkorisnika].trenutni_file:                    
                    return jsonify({"konzola": 0})
                sesije[idkorisnika].proces = Popen([lokacija_od_pythona, "-u", sesije[idkorisnika].trenutni_file], stdout=open(f'{serverski_path}/tekst_fajlovi/{idkorisnika}.txt', 'w+'), cwd=sesije[idkorisnika].root_fold)                
                return jsonify({"konzola": f'root_fold{sesije[idkorisnika].trenutni_file[len(sesije[idkorisnika].root_fold):]}>\n'})

            if "proveri_konzolu" in uraditi:
                sesije[idkorisnika].konzola = procitaj_file(f'{serverski_path}/tekst_fajlovi/{idkorisnika}.txt')                     
                if sesije[idkorisnika].proces.poll() == 0:
                    os.remove(f"{serverski_path}/tekst_fajlovi/{idkorisnika}.txt")                    
                    sesije[idkorisnika].proces = ""
                    return jsonify({"konzola": sesije[idkorisnika].konzola, "nastavi": False})
                else:                    
                    return jsonify({"konzola": sesije[idkorisnika].konzola, "nastavi": True})
                            
            if "sacuvaj" in uraditi and "." in sesije[idkorisnika].trenutni_file:                
                sesije[idkorisnika].kod_povrsina = request.form["code"]                            
                with open(sesije[idkorisnika].trenutni_file,"w+", encoding="UTF-8") as f:                    
                    f.write(sesije[idkorisnika].kod_povrsina)
                return jsonify({"status": 1})
            else:
                return jsonify({"status": 0})
                                    
        if "izloguj" in komande:
            '''
            @todo #3 ne radi logout, jebe ga ovaj .pop i izbacivanje iz baze, redirect ne sljaka
            '''

            #smanjuje se broj uredjaja na kojima je ulogovan korisnik
            ulogovani[request.cookies["kluc_sesija"]] -= 1
            print(ulogovani[request.cookies["kluc_sesija"]])
            #ukoliko je broj uredjaja 0, podaci o korisniku se brisu sa servera
            if ulogovani[request.cookies["kluc_sesija"]] == 0:                
                print("sodhaskjdhakshdkjashdkj")
                izloguj_korisnika(request.cookies["kljuc_sesija"])                
                ulogovani.pop(request.cookies["kluc_sesija"], None)             
                sesije.pop(idkorisnika, None)

            #uklanjanje kolacica i poruka o uspesnom logout-u
            odgovor = make_response(jsonify({"poruka": "uspesno"}))            
            odgovor.set_cookie("kluc_sesija", "",max_age=0, httponly=True)
            return odgovor               

        return odgovor
    elif request.method=="GET":        
               
        kljucevi =list(request.cookies.keys())        
        if "kluc_sesija" in kljucevi:                                           
            if request.cookies["kluc_sesija"] not in list(ulogovani.keys()):
                return redirect("/")
                
            #lokalne varijable
            nas,konzolica = "Remote_dev",""

            #obrada monitora za trenutni file (natpis kod konzole i title stranice u html-u)
            konzolica = sesije[request.cookies["kluc_sesija"]].trenutni_file[len(sesije[request.cookies["kluc_sesija"]].root_fold):]
            if not len(konzolica) == 0:
                konzolica = konzolica.split("/")[-1]
                nas = konzolica

            #desktop ili mobile html  
            agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent')) 
            if agent_korisnika["os"]["family"] in ["Windows","macos","Linux"]:
                ime_html_fajla = "coding_desktop"                
            elif agent_korisnika["os"]["family"] in ["Android","ios"]:
                ime_html_fajla = "coding_mobile"

            #pravljenje odgovora            
            return render_template("{}.html".format(ime_html_fajla), kdp = sesije[request.cookies["kluc_sesija"]].kod_povrsina, naslov =nas, konzolica = konzolica)
            
        return redirect("/")
            
@app.route('/file_explorer', methods=["GET","POST"])
def menadzer():    
    if request.method=="POST":
        komande = request.form.keys()
        uraditi = list(request.form.values())  
        idkorisnika = request.cookies["kluc_sesija"]
        if "akcija" in komande:
            if "obrisi" in uraditi:                    
                if "." in sesije[idkorisnika].trenutni_file.split("/")[-1]:
                    sesije[idkorisnika].kod_povrsina, sesije[idkorisnika].konzola = "",""
                    os.remove(sesije[idkorisnika].trenutni_file)
                    sesije[idkorisnika].fajlovi.pop(sesije[idkorisnika].index_trenutnog)                    
                else:
                    shutil.rmtree(sesije[idkorisnika].trenutni_file)
                    pom_index = sesije[idkorisnika].index_trenutnog+1
                    try:
                        while not sesije[idkorisnika].fajlovi[pom_index][3] == sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][3]:                        
                            pom_index+=1                   
                        sesije[idkorisnika].fajlovi = sesije[idkorisnika].fajlovi[0:sesije[idkorisnika].index_trenutnog] + sesije[idkorisnika].fajlovi[pom_index:]
                    except:
                        sesije[idkorisnika].fajlovi = sesije[idkorisnika].fajlovi[0:sesije[idkorisnika].index_trenutnog]  
                sesije[idkorisnika].trenutni_file = lista_u_string(sesije[idkorisnika].trenutni_file.split("/")[:-1],"/")[:-1]                
                sesije[idkorisnika].index_trenutnog = vrati_element_po_adresi(sesije[idkorisnika].fajlovi,"root_fold" + sesije[idkorisnika].trenutni_file[len(sesije[idkorisnika].root_fold):])                
                
            if 'napravi' in uraditi:                    
                if "." in sesije[idkorisnika].trenutni_file:
                    p = f'{lista_u_string(sesije[idkorisnika].trenutni_file.split("/")[:-1],"/")[:-1]}/{uraditi[1]}'
                    sesije[idkorisnika].fajlovi.insert(sesije[idkorisnika].index_trenutnog+1,["white",uraditi[1],"root_fold" + p[len(sesije[idkorisnika].root_fold):], sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][3]])
                else:
                    p = f'{sesije[idkorisnika].trenutni_file}/{uraditi[1]}'
                    sesije[idkorisnika].fajlovi.insert(sesije[idkorisnika].index_trenutnog+1,["white",uraditi[1],"root_fold" + p[len(sesije[idkorisnika].root_fold):], sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][3]+1])

                if "." in uraditi[1]:
                    napravi_fajl(p) 
                else:
                    os.mkdir(p)
            return jsonify({"fajlovi": sesije[idkorisnika].fajlovi,"trenutni_fajl": "root_fold" + sesije[idkorisnika].trenutni_file[len(sesije[idkorisnika].root_fold):]})
                
        if "lokacija" in komande:
            if request.form["lokacija"] == "root_fold":                
                sesije[idkorisnika].trenutni_file = sesije[idkorisnika].root_fold
                sesije[idkorisnika].kod_povrsina = ""
                sesije[idkorisnika].fajlovi = [["white", x, f'root_fold\{x}', 1] for x in os.listdir(sesije[idkorisnika].root_fold)]
                sesije[idkorisnika].fajlovi = [[sesije[idkorisnika].select_color, "root", "root_fold", 0],*sesije[idkorisnika].fajlovi]
                sesije[idkorisnika].index_trenutnog = 0
                return jsonify({"fajlovi": sesije[idkorisnika].fajlovi,"trenutni_fajl": "root_fold"})

            sesije[idkorisnika].trenutni_file = sesije[idkorisnika].root_fold+ request.form["lokacija"][9:]              
            ime_file = sesije[idkorisnika].trenutni_file.split("/")[-1] 
            stari_index = sesije[idkorisnika].index_trenutnog            
            sesije[idkorisnika].index_trenutnog = vrati_element_po_adresi(sesije[idkorisnika].fajlovi,f'root_fold{sesije[idkorisnika].trenutni_file[len(sesije[idkorisnika].root_fold):]}')
            b = sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][0] 

            if "." in ime_file: 
                if b == "white":
                    sesije[idkorisnika].konzola = ""
                    sesije[idkorisnika].kod_povrsina = procitaj_file(sesije[idkorisnika].trenutni_file)
                    sesije[idkorisnika].fajlovi = ukloni_boje_svih_datoteka(sesije[idkorisnika].fajlovi)
                    sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][0] = sesije[idkorisnika].select_color   
                    return jsonify({"fajlovi": sesije[idkorisnika].fajlovi,"trenutni_fajl": "root_fold" + sesije[idkorisnika].trenutni_file[len(sesije[idkorisnika].root_fold):], "prebaci": "da", "code": sesije[idkorisnika].kod_povrsina})
                else:
                    sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][0] = "white"
                    sesije[idkorisnika].kod_povrsina = ""   
            else:
                if b == "white":
                    sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][0] = sesije[idkorisnika].select_color
                    if "." in sesije[idkorisnika].fajlovi[stari_index][1]:
                        sesije[idkorisnika].fajlovi[stari_index][0] = "white"
                    for file in os.listdir(sesije[idkorisnika].trenutni_file):
                        sesije[idkorisnika].fajlovi.insert(sesije[idkorisnika].index_trenutnog+1,["white", file, f'root_fold{sesije[idkorisnika].trenutni_file[len(sesije[idkorisnika].root_fold):]}/{file}', sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][3]+1])                
                else:
                    sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][0] = "white"
                    sesije[idkorisnika].trenutni_file = lista_u_string(sesije[idkorisnika].trenutni_file.split("/")[:-1],"/")[:-1]
                    pom_index = sesije[idkorisnika].index_trenutnog+1
                    try:
                        while not sesije[idkorisnika].fajlovi[pom_index][3] == sesije[idkorisnika].fajlovi[sesije[idkorisnika].index_trenutnog][3]:                        
                            pom_index+=1                   
                        sesije[idkorisnika].fajlovi = sesije[idkorisnika].fajlovi[0:sesije[idkorisnika].index_trenutnog+1] + sesije[idkorisnika].fajlovi[pom_index:]
                    except:
                        sesije[idkorisnika].fajlovi = sesije[idkorisnika].fajlovi[0:sesije[idkorisnika].index_trenutnog+1]
            return jsonify({"fajlovi": sesije[idkorisnika].fajlovi,"trenutni_fajl": "root_fold" + sesije[idkorisnika].trenutni_file[len(sesije[idkorisnika].root_fold):],"code": sesije[idkorisnika].kod_povrsina})

        if "dinamicki_elememnti" in komande:
            return jsonify({"fajlovi": sesije[idkorisnika].fajlovi,"trenutni_fajl": "root_fold" + sesije[idkorisnika].trenutni_file[len(sesije[idkorisnika].root_fold):]})


    elif request.method=="GET":
        
        agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent'))
        if agent_korisnika["os"]["family"] in ["Windows","macos","Linux"]:
            return redirect("/coding")

        kljucevi =list(request.cookies.keys())                                
        if "kluc_sesija" in kljucevi:
            if request.cookies["kluc_sesija"] not in list(ulogovani.keys()):
                return redirect("/")

            return make_response(render_template("file_manager.html"))
        else:            
            return redirect("/")

#error 404 handling
@app.errorhandler(404)
def nenadjena_stranica(e):
    return render_template("404.html"),404

#endregion stranice
if __name__=="__main__":
    if jeste_debug:     
        app.run(port = 5000)
    else:
        trag.start()
        serve(TransLogger(app, setup_console_handler=False, logger_name="Remote_dev", format = ('[%(time)s] Metod: %(REQUEST_METHOD)s Status: %(status)s\tVelicina: %(bytes)s [bytes]\tTrazeno: %(REQUEST_URI)s')),host='0.0.0.0', port=5000, url_scheme = "https")
        trag.shutdown()