from flask import Flask, jsonify, redirect,request, render_template,make_response
import os,shutil,sys
from waitress import serve
from paste.translogger import TransLogger  
from subprocess import Popen
from ua_parser import user_agent_parser
from infi.systray import SysTrayIcon
from lib import *

#region tray ikonica
def ugasi_program(systray):
    os._exit(1)

trag = SysTrayIcon("static/images/ikonica.ico", "Remote_dev", on_quit=ugasi_program)
#endregion tray ikonica

#region serverske promenljive
app = Flask(__name__)
vreme_kolacic = 3600 #s traju kolacici na sajtu
serverski_path = r"E:\remote_dev_server_data"
lokacija_od_pythona = f"{os.path.dirname(sys.executable)}\{os.path.basename(sys.executable)}"
app.config['MAX_CONTENT_LENGTH'] = 100000000
#endregion serverske promenljive
jeste_debug = False
rt = r"C:\python_projekti\remote_dev"
#rt = r'C:\\Artificial_Inteligence\\uho'
nalog = ["",'Andreja', '92bffb0826ab25ce7877d6d1bd4a42f4', rt, 'rgb(171, 248, 194)']
kljuc_korisnika = ""

user = korisnik(nalog)

#region stranice
@app.route('/', methods=['GET', 'POST'])
def login():
    global kljuc_korisnika
    if request.method == "POST":
        komande = list(request.form.keys())
        sadrzaj_komande = list(request.form.values())        
        if "login" in komande:
            if str(sadrzaj_komande[1]) == nalog[1] and str(sadrzaj_komande[2]) == nalog[2]:
                odgovor = make_response(jsonify({"autentifikacija":"uspesna"}))
                if kljuc_korisnika == "":
                    kljuc_korisnika = nasumicni_string(10)
                odgovor.set_cookie("kluc_sesija", kljuc_korisnika,max_age=vreme_kolacic, httponly=True)
                return odgovor
            else:
                return jsonify({"autentifikacija":"neuspesna"})
            
    if request.method == "GET":
        if "kluc_sesija" in request.cookies.keys():            
            if request.cookies["kluc_sesija"] == kljuc_korisnika:
                return redirect("/coding")
        return render_template("login.html")

@app.route('/coding', methods=['GET', 'POST'])
def kodiranje(): 
    global kljuc_korisnika       
    if request.method=="POST":
        '''
        todo@ #6 dodati sigurnost da nasumicni post request (iz postmana npr) ne moze da ubaguje server
        '''
        komande = list(request.form.keys())
        sadrzaj_komande = list(request.form.values())
        kljuc_korisnika = request.cookies["kluc_sesija"]
        if "kontrola" in komande:
            if "zaustavi" in sadrzaj_komande:
                user.proces.terminate()
                return jsonify({"rezultat": "uspesno"})

            if "izvrsi" in sadrzaj_komande:                                            
                if ".py" not in user.trenutni_file:                    
                    return jsonify({"konzola": 0})
                user.proces = Popen([lokacija_od_pythona, "-u", user.trenutni_file], stdout=open(f'{serverski_path}/{kljuc_korisnika}.txt', 'w+'), cwd=user.root_fold)                
                return jsonify({"konzola": f'root_fold{user.trenutni_file[len(user.root_fold):]}>\n'})

            if "proveri_konzolu" in sadrzaj_komande:
                user.konzola = procitaj_file(f'{serverski_path}/{kljuc_korisnika}.txt')                     
                if user.proces.poll() == 0:
                    os.remove(f"{serverski_path}/{kljuc_korisnika}.txt")                    
                    user.proces = ""
                    return jsonify({"konzola": user.konzola, "nastavi": False})
                else:                    
                    return jsonify({"konzola": user.konzola, "nastavi": True})
                            
            if "sacuvaj" in sadrzaj_komande and "." in user.trenutni_file:                
                user.kod_povrsina = request.form["code"]                            
                with open(user.trenutni_file,"w+", encoding="UTF-8") as f:                    
                    f.write(user.kod_povrsina)
                return jsonify({"status": 1})
            else:
                return jsonify({"status": 0})
                                    
        if "izloguj" in komande:            
            odgovor = make_response(jsonify({"poruka": "uspesno"}))            
            odgovor.set_cookie("kluc_sesija", "",max_age=0, httponly=True)
            return odgovor               

        return odgovor

    elif request.method=="GET":        
               
        kljucevi =list(request.cookies.keys())        
        if "kluc_sesija" in kljucevi:  
            if request.cookies["kluc_sesija"] == kljuc_korisnika:                                
                #lokalne varijable
                nas,konzolica = "Remote_dev",""

                #obrada monitora za trenutni file (natpis kod konzole i title stranice u html-u)
                konzolica = user.trenutni_file[len(user.root_fold):]
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
                return render_template("{}.html".format(ime_html_fajla), kdp = user.kod_povrsina, naslov =nas, konzolica = konzolica)
            
        return redirect("/")
            
@app.route('/file_explorer', methods=["GET","POST", "PUT"])
def menadzer():
    global kljuc_korisnika
                               
    if "kluc_sesija" not in request.cookies.keys():
        return redirect("/")  
    if request.cookies["kluc_sesija"] != kljuc_korisnika:                
        return redirect("/")  

    if request.method=="PUT":

        if "." in user.trenutni_file:
            tren = user.trenutni_file[0:user.trenutni_file.index(r"/")]

        for f in request.files.getlist("fajlovi"):                           
            f.save(os.path.join(serverski_path, f.filename))
        return jsonify({"REZULTAT": "REZ"}), 200

    if request.method=="POST":
        komande = request.form.keys()
        sadrzaj_komande = list(request.form.values())          

        if "akcija" in komande:
            if "obrisi" in sadrzaj_komande:                    
                if "." in user.trenutni_file.split("/")[-1]:
                    user.kod_povrsina, user.konzola = "",""
                    os.remove(user.trenutni_file)
                    user.fajlovi.pop(user.index_trenutnog)                    
                else:
                    shutil.rmtree(user.trenutni_file)
                    pom_index = user.index_trenutnog+1
                    try:
                        while not user.fajlovi[pom_index][3] == user.fajlovi[user.index_trenutnog][3]:                        
                            pom_index+=1                   
                        user.fajlovi = user.fajlovi[0:user.index_trenutnog] + user.fajlovi[pom_index:]
                    except:
                        user.fajlovi = user.fajlovi[0:user.index_trenutnog]  
                user.trenutni_file = lista_u_string(user.trenutni_file.split("/")[:-1],"/")[:-1]                
                user.index_trenutnog = vrati_element_po_adresi(user.fajlovi,"root_fold" + user.trenutni_file[len(user.root_fold):])                
                
            if 'napravi' in sadrzaj_komande:                    
                if "." in user.trenutni_file:
                    p = f'{lista_u_string(user.trenutni_file.split("/")[:-1],"/")[:-1]}/{sadrzaj_komande[1]}'
                    user.fajlovi.insert(user.index_trenutnog+1,["white",sadrzaj_komande[1],"root_fold" + p[len(user.root_fold):], user.fajlovi[user.index_trenutnog][3]])
                else:
                    p = f'{user.trenutni_file}/{sadrzaj_komande[1]}'
                    user.fajlovi.insert(user.index_trenutnog+1,["white",sadrzaj_komande[1],"root_fold" + p[len(user.root_fold):], user.fajlovi[user.index_trenutnog][3]+1])

                if "." in sadrzaj_komande[1]:
                    napravi_fajl(p) 
                else:
                    os.mkdir(p)
            return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold" + user.trenutni_file[len(user.root_fold):]})
                
        if "lokacija" in komande:
            if request.form["lokacija"] == "root_fold":                
                user.trenutni_file = user.root_fold
                user.kod_povrsina = ""
                user.fajlovi = [["white", x, f'root_fold\{x}', 1] for x in os.listdir(user.root_fold)]
                user.fajlovi = [[user.select_color, "root", "root_fold", 0],*user.fajlovi]
                user.index_trenutnog = 0
                return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold"})

            user.trenutni_file = user.root_fold+ request.form["lokacija"][9:]              
            ime_file = user.trenutni_file.split("/")[-1] 
            stari_index = user.index_trenutnog            
            user.index_trenutnog = vrati_element_po_adresi(user.fajlovi,f'root_fold{user.trenutni_file[len(user.root_fold):]}')
            b = user.fajlovi[user.index_trenutnog][0] 

            if "." in ime_file: 
                if b == "white":
                    user.konzola = ""
                    user.kod_povrsina = procitaj_file(user.trenutni_file)
                    user.fajlovi = ukloni_boje_svih_datoteka(user.fajlovi)
                    user.fajlovi[user.index_trenutnog][0] = user.select_color   
                    return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold" + user.trenutni_file[len(user.root_fold):], "prebaci": "da", "code": user.kod_povrsina})
                else:
                    user.fajlovi[user.index_trenutnog][0] = "white"
                    user.kod_povrsina = ""   
            else:
                if b == "white":
                    user.fajlovi[user.index_trenutnog][0] = user.select_color
                    if "." in user.fajlovi[stari_index][1]:
                        user.fajlovi[stari_index][0] = "white"
                    for file in os.listdir(user.trenutni_file):
                        user.fajlovi.insert(user.index_trenutnog+1,["white", file, f'root_fold{user.trenutni_file[len(user.root_fold):]}/{file}', user.fajlovi[user.index_trenutnog][3]+1])                
                else:
                    user.fajlovi[user.index_trenutnog][0] = "white"
                    user.trenutni_file = lista_u_string(user.trenutni_file.split("/")[:-1],"/")[:-1]
                    pom_index = user.index_trenutnog+1
                    try:
                        while not user.fajlovi[pom_index][3] == user.fajlovi[user.index_trenutnog][3]:                        
                            pom_index+=1                   
                        user.fajlovi = user.fajlovi[0:user.index_trenutnog+1] + user.fajlovi[pom_index:]
                    except:
                        user.fajlovi = user.fajlovi[0:user.index_trenutnog+1]
            return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold" + user.trenutni_file[len(user.root_fold):],"code": user.kod_povrsina})

        if "dinamicki_elememnti" in komande:
            return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold" + user.trenutni_file[len(user.root_fold):]})

    elif request.method=="GET":        
        agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent'))

        if agent_korisnika["os"]["family"] in ["Windows","macos","Linux"]:
            return redirect("/coding")        
        return make_response(render_template("file_manager.html"))                 
        

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