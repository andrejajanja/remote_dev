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
                return jsonify({"fajlovi": sesije[idkorisnika]["fajlovi"],"trenutni_fajl": "root_fold" + sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):], "prebaci": "da"})
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
        return jsonify({"fajlovi": sesije[idkorisnika]["fajlovi"],"trenutni_fajl": "root_fold" + sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):]})

    if "dinamicki_elememnti" in komande:
        return jsonify({"fajlovi": sesije[idkorisnika]["fajlovi"],"trenutni_fajl": "root_fold" + sesije[idkorisnika]["trenutni_file"][len(sesije[idkorisnika]["root_fold"]):]})
