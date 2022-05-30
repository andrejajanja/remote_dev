async function uzmi_elemente(){
    elementi = await posalji_req_json({"dinamicki_elememnti": "bilo_sta"}, "POST", url_filesistem) 
    napravi_dugmad(elementi)
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
async function posalji_req_json(data, tip, url_str)
{
    const podaci = await fetch(url_str, {
        method: tip,
        body: new URLSearchParams(data)
    })
    .then((response) => response.json())
    .then((pod) => {return pod;});
    return podaci;
}

async function ucitavanje_animacija_izvrsi_dugme(){
    let s = "="
    let i = 0
    while(izvrsi_dugme.disabled){
        if(i==7){i=0}
        izvrsi_dugme.value = "|"+s.repeat(i)+"|"
        i+=1
        await sleep(300)             
    }
    izvrsi_dugme.value = "Izvrši"
}

function napravi_dugmad(elems){
    while (kutija_za_dugmice.lastElementChild) {
        kutija_za_dugmice.removeChild(kutija_za_dugmice.lastElementChild);
    }
    elems["fajlovi"].forEach(dugme => {            
        var input = document.createElement("input");
        input.type = "submit";
        input.name = "lok";
        input.dataset['put'] = dugme[2];
        input.value = dugme[1];
        input.style.backgroundColor = dugme[0];
        input.style.marginLeft = dugme[3]*7 + "%";            
        input.className="file_folder";
        kutija_za_dugmice.appendChild(input);            
    });
    adres_traka.textContent = elems["trenutni_fajl"]
}

const url_code = "https://janja.xyz/coding";
const url_filesistem = "https://janja.xyz/file_explorer";

const forma_za_kodiranje = document.querySelector("#forma_kodiranje");
const code_povrs = document.querySelector("#povrsina_kodiranje");
const konzola =   document.getElementById("koznola_deo");
const sacuvaj_dugme = document.getElementById("sacu");
const izvrsi_dugme = document.getElementById("izvr");
const file_explorer_form = document.querySelector("#file_explorer");
const adres_traka = document.querySelector("#adresna_traka");
const forma_fajlovi = document.querySelector("#forma_pravljenje_fajlovi");
const ime_fajla = document.querySelector("#file_ime_input");
const kutija_za_dugmice = document.querySelector("#files_view");
const forma_zaglavlje = document.querySelector("#zaglavlje");
const naslov_konzola = document.querySelector("#naslov_konzola");

let jeste_konzola = true
let inicijalni_odgovor="";
let pom_konzola = "";
let izvrsava = false;

uzmi_elemente()

forma_za_kodiranje.addEventListener("submit", async function(e){   
    e.preventDefault();   
    
    if (e.submitter.dataset.funkcija == "Zaustavi") {
        izvrsava = false                    
        izvrsi_dugme.value = "Izvrši";
        izvrsi_dugme.dataset.funkcija = "Izvrsi"
        odgovor = await posalji_req_json({kontrola: "zaustavi"}, "POST", url_code)                                 
        return;
    }

    if(e.submitter.dataset.funkcija == "Izvrsi"){
        izvrsi_dugme.dataset.funkcija = "Zaustavi";
        izvrsi_dugme.value = "Zaustavi";
        izvrsava = true
        odgovor = await posalji_req_json({kontrola: "izvrsi"},"POST", url_code);
        if(odgovor["konzola"] == 0){
            konzola.value = "Neophodan je ime_fajla.py file da biste ga izvrsili";
            izvrsi_dugme.value = "Izvrši";
            izvrsi_dugme.dataset.funkcija = "Izvrsi"             
            return;
        }                
        inicijalni_odgovor="";
        pom_konzola = "";

        if(jeste_konzola){
            inicijalni_odgovor= konzola.value + odgovor["konzola"]
            konzola.value = inicijalni_odgovor+ pom_konzola
            jeste_konzola=false
        }else{
            inicijalni_odgovor= konzola.value
        }
                                        
        while (izvrsava) {
            pom_konzola = await posalji_req_json({kontrola: "proveri_konzolu"}, "POST", url_code)
            if(!pom_konzola["nastavi"]){
                konzola.value = inicijalni_odgovor+ pom_konzola["konzola"]
                break
            }
            konzola.value = inicijalni_odgovor+ pom_konzola["konzola"]
            await sleep(1000);
        }

        if (odgovor["konzola"]) {
            konzola.value += "\n" + odgovor["konzola"]    
        }
        
        if (izvrsava) {
                        
        }

        izvrsi_dugme.value = "Izvrši";
        izvrsi_dugme.dataset.funkcija = "Izvrsi"
        izvrsava = false
        return;
    }            

    if(e.submitter.dataset.funkcija == "Sacuvaj"){                
        sacuvaj_dugme.disabled = true;
        odgovor = await posalji_req_json({kontrola: "sacuvaj", code: code_povrs.value},"POST", url_code)

        if(odgovor["status"]){                    
            sacuvaj_dugme.value = "Uspesno"
            
        }
        else{                    
            sacuvaj_dugme.value = "Greska"
        }
        await sleep(2000);
        sacuvaj_dugme.disabled = false;
        sacuvaj_dugme.value = "Sačuvaj"
        return;
    }

    if(e.submitter.dataset.funkcija == "ocisti"){
        konzola.value=""
        jeste_konzola = true
        return;
    }
})

forma_fajlovi.addEventListener("submit", async function(e){        
    e.preventDefault();
    if(e.submitter.dataset["vrednost"] == "napravi")
    {
        if(ime_fajla.value=="")
        {
            alert("Ne mozete da napravite fajl/folder bez unetog imena");
        }
        else
        {
            var odgovor = await posalji_req_json({akcija:"napravi", "ime": ime_fajla.value}, "POST", url_filesistem)
            napravi_dugmad(odgovor)
            ime_fajla.value = ""
        }                
    }

    if(e.submitter.dataset["vrednost"] == "obrisi")
    {                       
        if(adres_traka.innerHTML == "root_fold"){
            alert("Ne mozete obrisati glavni direktorijum")
        }
        else{
            let person = prompt("Da li sigurno zelite da obirsete izabran file/folder? (izbrisite _ da bi potvrdili)", "da_");
            if (person == "da") {
                var odgovor = await posalji_req_json({akcija:"obrisi"}, "POST", url_filesistem)
                napravi_dugmad(odgovor)
            }else{
                return;
            }
        }
    }
})

file_explorer_form.addEventListener('submit', async function(e){
    e.preventDefault();
    var odgovor = await posalji_req_json({lokacija: e.submitter.dataset['put']}, "POST", url_filesistem)            
    if ("code" in odgovor) {
        code_povrs.value = odgovor["code"]    
    }
    else
    {
        code_povrs.value = ""
    }

    let fajl = odgovor["trenutni_fajl"].split("/").pop()

    if(fajl == "root_fold"){
        document.title = "Remote_dev"
        naslov_konzola.innerHTML = "Konzola:"
    }
    else
    {
        document.title = fajl
        naslov_konzola.innerHTML = "Konzola: " + fajl
    }

    napravi_dugmad(odgovor)
})

forma_zaglavlje.addEventListener("submit", async function(e){
    e.preventDefault();                       
    if(e.submitter.dataset.funkcija == "odjava"){                                             
        odgovor = await posalji_req_json({izloguj: "pokreni"}, "POST", url_code)
        window.location.href = "https://janja.xyz"
    }
})

window.addEventListener('keydown', async function (event) {
    if (event.shiftKey && event.code === 'KeyS') {
        sacuvaj_dugme.disabled = true;
        odgovor = await posalji_req_json({kontrola: "sacuvaj", code: code_povrs.value},"POST", url_code)

        if(odgovor["status"]){                    
            sacuvaj_dugme.value = "Uspesno"
            
        }
        else{                    
            sacuvaj_dugme.value = "Greska"
        }
        await sleep(2000);
        sacuvaj_dugme.disabled = false;
        sacuvaj_dugme.value = "Sačuvaj"
        return;
    }
});