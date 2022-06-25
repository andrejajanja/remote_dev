from flask import Flask, jsonify, redirect,request, render_template,make_response, send_file
import os,shutil,sys
from waitress import serve
from paste.translogger import TransLogger  
from subprocess import Popen, STARTUPINFO, STARTF_USESHOWWINDOW
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
vreme_kolacic = 3600#s traju kolacici na sajtu
serverski_path = os.getcwd()
lokacija_od_pythona = f"{os.path.dirname(sys.executable)}\{os.path.basename(sys.executable)}"
app.config['MAX_CONTENT_LENGTH'] = 100000000 #100MB mu je max upload size, mora da se namesti limit i na nginx-u
#endregion serverske promenljive
jeste_debug = True
#rt = r"C:\python_projekti\remote_dev"
rt = r'C:\\Artificial_Inteligence\\uho'
nalog = ["",'Andreja', '92bffb0826ab25ce7877d6d1bd4a42f4', rt, 'rgb(171, 248, 194)']
kljuc_korisnika = ""
user = korisnik(nalog)
file_pointer = ""

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
    global kljuc_korisnika,file_pointer 

    #autentifikacija
    if "kluc_sesija" not in request.cookies.keys():
        return redirect("/")  
    if request.cookies["kluc_sesija"] != kljuc_korisnika:                
        return redirect("/") 

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
                file_pointer.close()                
                os.remove(f"{serverski_path}/{kljuc_korisnika}.txt")
                return jsonify({"rezultat": "uspesno"})

            if "izvrsi" in sadrzaj_komande:                                                                                           
                file_pointer = open(f'{serverski_path}/{kljuc_korisnika}.txt', 'w+') #otvaranje stream-a na trenutni konzolni fajl

                if sadrzaj_komande[1] == "py":
                    #grana u kojoj se izvrsava python skripta

                    if ".py" not in user.trenutni_file: #da li je uopste otvoren python file   
                        return jsonify({"konzola": 0})

                    if ("tensorflow" and "model.fit(") in procitaj_file(user.trenutni_file): #da li treba da se koristi formater za TF
                        user.formatiranje = "tf"  
                        
                    user.proces = Popen([lokacija_od_pythona, "-u", user.trenutni_file], stdout=file_pointer, cwd=user.root_fold, stderr = file_pointer)
                else:
                    #grana u kojoj se izvrsava terminalna skripta                    
                    strt = STARTUPINFO()
                    strt.dwFlags |= STARTF_USESHOWWINDOW  
                    try:                  
                        user.proces = Popen(sadrzaj_komande[1], stdout=file_pointer,stderr=file_pointer, text= True, startupinfo=strt)
                    except:
                        file_pointer.close()
                        os.remove(f"{serverski_path}/{kljuc_korisnika}.txt")
                        return jsonify({"konzola": 0})
                    
                return jsonify({"konzola": f'root_fold{user.trenutni_file[len(user.root_fold):]}>'})

            if "proveri_konzolu" in sadrzaj_komande:                
                if user.formatiranje == "":
                    user.konzola = procitaj_file(f'{serverski_path}/{kljuc_korisnika}.txt')
                else:
                    user.konzola = procitaj_file_tf_format(f'{serverski_path}/{kljuc_korisnika}.txt')
                
                if user.proces.poll() == 0:
                    file_pointer.close()
                    os.remove(f"{serverski_path}/{kljuc_korisnika}.txt")                    
                    
                    user.formatiranje = ""                         
                    user.proces = ""
                    return jsonify({"konzola": user.konzola, "nastavi": False})
                else:                    
                    return jsonify({"konzola": user.konzola, "nastavi": True})                                
                            
            if "sacuvaj" in sadrzaj_komande:            
                if "." in user.trenutni_file:                            
                    try:
                        user.kod_povrsina = request.form["code"]                            
                        with open(user.trenutni_file,"w+") as f:                    
                            f.write(user.kod_povrsina)
                        return jsonify({"status": "Uspešno"})
                    except:            
                        return jsonify({"status": "Neuspešno"})
                else:
                    return jsonify({"status": "Nije otvoren fajl koji bi se mogao sačivati"})
            
            
                                    
        if "izloguj" in komande:            
            odgovor = make_response(jsonify({"poruka": "uspesno"}))            
            odgovor.set_cookie("kluc_sesija", "",max_age=0, httponly=True)
            return odgovor        

    elif request.method=="GET":        
        nas,konzolica = "Remote_dev",""

        #obrada monitora za trenutni file (natpis kod konzole i title stranice u html-u)
        konzolica = user.trenutni_file[len(user.root_fold):]
        if not len(konzolica) == 0:
            konzolica = konzolica.split("/")[-1]            

        #provera da li je desktop ili mobile platforma - daje html shodno tome
        agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent')) 
        if agent_korisnika["os"]["family"] in ["Windows","macos","Linux"]:
            return render_template("coding_desktop.html",kdp = user.kod_povrsina, naslov =nas, konzolica = konzolica)
        elif agent_korisnika["os"]["family"] in ["Android","ios"]:            
            return render_template("coding_mobile.html",kdp = user.kod_povrsina, naslov =nas, konzolica = konzolica)

        #pravljenje odgovora                            
            
@app.route('/file_explorer', methods=["GET","POST", "PUT"])
def menadzer():
    global kljuc_korisnika
    
    #autentifikacija
    if "kluc_sesija" not in request.cookies.keys():
        return redirect("/")  
    if request.cookies["kluc_sesija"] != kljuc_korisnika:                
        return redirect("/")  

    #put request za file upload
    if request.method=="PUT":
        if "." in user.trenutni_file:
            try:
                tren = user.root_fold + user.trenutni_file[len(user.root_fold):user.trenutni_file.rindex("/")]
            except:
                tren = user.root_fold + user.trenutni_file[len(user.root_fold):user.trenutni_file.rindex("\\")]
        else:
            tren = user.root_fold + user.trenutni_file[len(user.root_fold):]
        
        for f in request.files.getlist("fajlovi"):            
            f.save(os.path.join(tren, f.filename))
        return jsonify({"REZULTAT": "REZ"}), 200

    #post request za funkcije file_explorer-a
    if request.method=="POST":
        komande = request.form.keys()
        sadrzaj_komande = list(request.form.values())        

        #napravi/obrisi fajlove
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

                try:
                    if "." in sadrzaj_komande[1]:
                        napravi_fajl(p) 
                    else:
                        os.mkdir(p)
                except FileExistsError:
                    return jsonify({"fajlovi": "postoji_vec"})

            return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold" + user.trenutni_file[len(user.root_fold):]})

        #otvaranje/zatvaranje fajlova, menjanje boja     
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

            #ukoliko je u pitanju fajl
            if "." in ime_file: 
                if b == "white":                                  
                    user.kod_povrsina = procitaj_file(user.trenutni_file)                                            
                    user.fajlovi = ukloni_boje_svih_datoteka(user.fajlovi)
                    user.fajlovi[user.index_trenutnog][0] = user.select_color                                      
                    return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold" + user.trenutni_file[len(user.root_fold):], "prebaci": "da", "kodd": user.kod_povrsina})
                else:
                    user.fajlovi[user.index_trenutnog][0] = "white"
                    user.kod_povrsina = ""   
            
            #ukoliko je u pitanju folder
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
            return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold" + user.trenutni_file[len(user.root_fold):]})

        #odgovor kada klijent trazi stanje otvorenih fajlova/foldera
        if "dinamicki_elememnti" in komande:
            return jsonify({"fajlovi": user.fajlovi,"trenutni_fajl": "root_fold" + user.trenutni_file[len(user.root_fold):]})

        #odgovor koji vraca ime fajla koji se preuzima
        if "trenutni_file" in komande:                  
            try:
                ime = user.trenutni_file[user.trenutni_file.rindex("/")+1:]
            except:                
                ime = user.trenutni_file[user.trenutni_file.rindex("\\")+1:]
            if not "." in ime: #ukoliko je zahtev za preuzimanje foldera, obavestava js da kaze korisniku da to nije dodato
                ime = "_f_o_l_d_e_r_"
            return jsonify({"ime": ime}),200

        #hendlovanje preuzimanja
        if "preuzmi_trenutni" in komande:                            
                try:                
                    return send_file(user.root_fold + user.trenutni_file[len(user.root_fold):], as_attachment=True),200
                except Exception as e:
                    return jsonify({"greska": "greska"}),420

    if request.method=="GET":        
        agent_korisnika = user_agent_parser.Parse(request.headers.get('User-Agent'))
        #provera da li je desktop ili mobile platforma
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

        serve(TransLogger(app, 
            setup_console_handler=False,
            logger_name="Remote_dev", 
            format = ('[%(time)s] Metod: %(REQUEST_METHOD)s Status: %(status)s\tVelicina: %(bytes)s [bytes]\tTrazeno: %(REQUEST_URI)s')),
            host='0.0.0.0',
            port=5000, 
            url_scheme = "https",
                     
        )

        trag.shutdown()