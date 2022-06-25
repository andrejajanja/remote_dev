const lok = new URL(window.location.href);

const url_code = lok.protocol+ "//" +lok.host+"/coding";
const url_filesistem = lok.protocol+ "//" +lok.host+ "/file_explorer";

//funkcije nasumicne
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

async function uzmi_elemente(){
    elementi = await posalji_req_json({"dinamicki_elememnti": "bilo_sta"}, "POST", url_filesistem) 
    napravi_dugmad(elementi)
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function ekstenzija_od_imena(ime){    
    i = ime.lastIndexOf(".")
    if (i==-1) {return "folder"}    
    return ime.substring(i+1)
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

//funkcije koje okidaju dugmici i precice
async function sacuvaj_fajl(){
    sacuvaj_dugme.disabled = true;
    odgovor = await posalji_req_json({kontrola: "sacuvaj", code: editor.getTextArea().value},"POST", url_code)

    if(odgovor["status"].length > 9){  
        alert(odgovor["status"]);                                  
    }
    else{                    
        sacuvaj_dugme.value = odgovor["status"];
    }
    await sleep(1000);
    sacuvaj_dugme.disabled = false;
    sacuvaj_dugme.value = "Sačuvaj"
    return;
}

async function napravi_fajl_folder(){
    let ime_fajla = prompt("Unesite ime fajla/foldera ovde:");    
    if(ime_fajla == null){
        return;
    }

    let odgovor = await posalji_req_json({akcija:"napravi", "ime": ime_fajla}, "POST",url_filesistem)

    if (odgovor["fajlovi"] == "postoji_vec") {
        alert("Fajl/folder sa datim imenom vec postoji");
    }else{
        napravi_dugmad(odgovor) 
    }
}

async function obrisi_fajl_folder(){
    if(adres_traka.innerHTML == "root_fold"){
        alert("Ne mozete obrisati glavni direktorijum")
    }
    else{
        let obris_file = prompt("Da li sigurno zelite da obirsete izabran file/folder? (izbrisite _ da bi potvrdili)", "_");
        if (obris_file == "") {
            let odgovor = await posalji_req_json({akcija:"obrisi"}, "POST",url_filesistem)
            napravi_dugmad(odgovor)
        }else{
            return;
        }
    }  
}

async function preuzmi_fajl(){
    let ime_fajla = await posalji_req_json({"trenutni_file": "___"},"POST",url_filesistem)
    if (ime_fajla["ime"] == "_f_o_l_d_e_r_") {
        alert("Ne mozete preuzeti folder za sada.")            
    } else {
        alert("Pocelo preuzimanje fajla")
        let odgovor = await fetch(url_filesistem, {
            method: "POST",
            body: new URLSearchParams({"preuzmi_trenutni": "prez"})
        })
        .then((response) => {return response.blob()});

        let url = window.URL.createObjectURL(odgovor);
        const anchor = document.createElement("a");
        document.body.appendChild(anchor);
        anchor.style = "display: none";    
        anchor.href = url;
        anchor.download = ime_fajla["ime"];
        
        anchor.click();
        document.body.removeChild(anchor);
        window.URL.revokeObjectURL(url);        
        alert("Preuzet fajl: " + ime_fajla["ime"])
    }
}

async function pokreni_proveravanje_konzole(odgovor){
    izvrsava = true                     
    inicijalni_odgovor="";
    pom_konzola = "";
    if(jeste_konzola){
        inicijalni_odgovor= konzola.value + odgovor["konzola"] + "\n"
        konzola.value = inicijalni_odgovor+ pom_konzola
        jeste_konzola=false
    }else{
        inicijalni_odgovor= konzola.value + "\n"
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
    return;
}

async function izvrsi_fajl(){
    izvrsi_dugme.dataset.funkcija = "Zaustavi";
    izvrsi_dugme.value = "Zaustavi";

    odgovor = await posalji_req_json({kontrola: "izvrsi", sta: "py"},"POST", url_code);
    if(odgovor["konzola"] == 0){
        konzola.value = "Neophodan je ime_fajla.py file da biste ga izvrsili";
        izvrsi_dugme.value = "Izvrši";
        izvrsi_dugme.dataset.funkcija = "Izvrsi"             
        return;
    }                

    await pokreni_proveravanje_konzole(odgovor);

    izvrsi_dugme.value = "Izvrši";
    izvrsi_dugme.dataset.funkcija = "Izvrsi"
    izvrsava = false
    konzo = konzola.value;
    var notifi = new Notification(title = "Zavšeno izvrsavanje komande/skripte!");  
    return;
}

async function terminal_pokretanje(){
    if (term.value == "Zaustavi") {
        izvrsi_dugme.disabled = false;
        izvrsava = false                    
        term.value = "Terminal";
        odgovor = await posalji_req_json({kontrola: "zaustavi"}, "POST", url_code)                                
        return;
    }

    let komm = konzola.value.substring(konzo.length);
    if(komm == ""){
        alert("Morate uneti terminalnu komandu da bi ste je izvršili");
        return;
    }        
    konzola.value += "\n";
    term.value = "Zaustavi";                      
    odgovor = await posalji_req_json({kontrola: "izvrsi", sta: komm}, "POST", url_code);                
    izvrsi_dugme.disabled = true; 
    await pokreni_proveravanje_konzole(odgovor);
    izvrsava = false
    izvrsi_dugme.disabled = false;        
    term.value = "Terminal";
    
    konzo = konzola.value;
    konzola.value = konzo
    return; 
}

async function zaustavi_izvrsavanje(){    
    odgovor = await posalji_req_json({kontrola: "zaustavi"}, "POST", url_code)                                 
    izvrsava = false                    
    izvrsi_dugme.value = "Izvrši";
    izvrsi_dugme.dataset.funkcija = "Izvrsi"    
    return;
}

const forma_za_kodiranje = document.querySelector("#forma_kodiranje");
const code_povrs = document.querySelector("#povrsina_kodiranje");
const konzola = document.getElementById("koznola_deo");
const sacuvaj_dugme = document.getElementById("sacu");
const izvrsi_dugme = document.getElementById("izvr");
const file_explorer_form = document.querySelector("#file_explorer");
const adres_traka = document.querySelector("#adresna_traka");
const forma_fajlovi = document.querySelector("#forma_pravljenje_fajlovi");
const kutija_za_dugmice = document.querySelector("#files_view");
const forma_zaglavlje = document.querySelector("#zaglavlje");
const file_loader = document.getElementById("file_loader");
const term = document.getElementById("terminal_izvr");

let jeste_konzola = true
let inicijalni_odgovor="";
let pom_konzola = "";
let izvrsava = false;
let notif = false;
let konzo = "";
let eks = "";


if(code_povrs.value == "0"){ code_povrs.value = "Fajl sa ovom ekstenzijom se trenutno\nne može prikazati u pretraživaču."; }

//davanje dozvole za notifikacije
if (Notification.permission !== "granted") {Notification.requestPermission().then(function (permission) {if (permission === "granted") {notif = true;}});}

uzmi_elemente()

eks = ekstenzija_od_imena(adres_traka.textContent)
if(eks == "py"){eks = "python";}
if(eks == "html"){eks == "xml";}

const editor = CodeMirror.fromTextArea(code_povrs, {
    lineNumbers: true,
    mode: eks,
    theme: 'dracula',
    autoCloseBrackets: true,
    autoCloseTags: true,
    styleActiveLine: true,
    // lineWrapping: true,
    scrollbarStyle: 'simple',
    lint: true,
    selfContain: true,
    highlightLines: true,
    // indentWithTabs: true,
    // gutters: ['CodeMirror-lint-markers'],
    extraKeys: { "ALT": "autocomplete" },
    foldGutter: true,
    gutters: ['CodeMirror-lint-markers', "CodeMirror-linenumbers", "CodeMirror-foldgutter",]
});

function focusCodeMirrorEditor() {
    editor.focus();
}

function clearCodeMirror() {
    editor.setValue('');
    editor.clearHistory();
}

function setNewLanguageModeOfEditor(newLanguage) {
    editor.setOption("mode", newLanguage)
}

const ucitaj_panel = document.getElementById("ucitavanje");
ucitaj_panel.style.display = "none";

//EVENT LISTENERS
forma_za_kodiranje.addEventListener("submit", async function(e){   
    e.preventDefault();   
    
    if (e.submitter.dataset.funkcija == "Zaustavi") {        
        zaustavi_izvrsavanje();
    }

    if(e.submitter.dataset.funkcija == "Izvrsi"){
        izvrsi_fajl();
    }            

    if(e.submitter.dataset.funkcija == "Sacuvaj"){                
        sacuvaj_fajl();
    }

    if(e.submitter.dataset.funkcija == "ocisti"){
        konzola.value=""
        jeste_konzola = true        
    }

    if(e.submitter.dataset.funkcija == "terminal"){ 
        terminal_pokretanje();
    }
})

forma_fajlovi.addEventListener("submit", async function(e){        
    e.preventDefault();

    if(e.submitter.dataset["vrednost"] == "napravi")
    {
        napravi_fajl_folder();
    }

    if(e.submitter.dataset["vrednost"] == "obrisi")
    {                               
        obrisi_fajl_folder();
    }

    if(e.submitter.dataset["vrednost"] == "preuzmi")
    {
        preuzmi_fajl();
    }

    if(e.submitter.dataset["vrednost"] == "posalji")
    {
        file_loader.click();
    }    
})

//funckcija koja "otvara" fajl
file_explorer_form.addEventListener('submit', async function(e){
    e.preventDefault();
    eks = ekstenzija_od_imena(e.submitter.dataset["put"])    

    if(eks == "folder"){
        let odgovor = await posalji_req_json({lokacija: e.submitter.dataset['put']}, "POST", url_filesistem);
        napravi_dugmad(odgovor)
        return;
    }
    let odgovor = await fetch(url_filesistem, {method: "POST",body: new URLSearchParams({lokacija: e.submitter.dataset['put']})
    })
    .then((response) => {return response.json()})                    
    editor.getDoc().setValue(odgovor["kodd"]);    
    if(code_povrs.value == "0"){
        code_povrs.value = "Fajl sa ovom ekstenzijom se trenutno\nne može prikazati u pretraživaču.";
    }
    
    if(eks == "py"){eks = "python";}
    if(eks == "html"){eks == "xml";}
    setNewLanguageModeOfEditor(eks);    
    napravi_dugmad(odgovor)
    return;     
})

forma_zaglavlje.addEventListener("submit", async function(e){
    e.preventDefault();                       
    if(e.submitter.dataset.funkcija == "odjava"){                                             
        odgovor = await posalji_req_json({izloguj: "pokreni"}, "POST", url_code)        
        window.location.href = lok.protocol+ "//" +lok.host;        
    }
})

file_loader.onchange = async function(e){   
    alert("Otpremanje fajlova otpočelo.")
    let slanje = new FormData();

    for (let i = 0; i < file_loader.files.length; i++) {        
        slanje.append("fajlovi", file_loader.files[i]);        
    }

    const podaci = await fetch(url_filesistem, {
        method: "PUT",
        body: slanje,        
    })
    .then((response) => response.json())
    .then((pod) => {return pod;});        
    while (file_loader.length > 0) {
        file_loader.pop();
    } 
    alert("Završeno otpremanje fajlova")    
}

konzola.onkeyup = function(){    
    if(konzola.value.indexOf(konzo) === -1){
        konzola.value = konzo
    }
};

//precice za koriscenje web stranice
window.addEventListener('keydown', async function (event) {    
    if (event.altKey && event.code === 'KeyS') {        
        sacuvaj_fajl();
    }
    if (event.altKey && event.code === 'KeyN'){        
        napravi_fajl_folder();
    }
    if (event.altKey && event.code === 'KeyO'){
        obrisi_fajl_folder();
    }
    if (event.altKey && event.code === 'KeyI'){
        izvrsi_fajl();
    }
    if (event.altKey && event.code === 'KeyZ'){
        zaustavi_izvrsavanje();
    }
    if (event.altKey && event.code === 'KeyP'){
        file_loader.click();
    }
    if (event.altKey && event.code === 'KeyD'){
        preuzmi_fajl();
    }  
    if (event.altKey && event.code === 'KeyT'){
        terminal_pokretanje();
    } 
    if(event.altKey && event.code === 'KeyB'){
        alert("PRECICE, ALT +:\n\n\tSacuvaj: S\n\tNovi fajl folder: N\n\tObrisi trenutni: O\n\tIzvrsi skriptu: i\n\tZaustavljanje skripte: Z\n\tSlanje file-a: P\n\tPreuzimanje trenutnog: D");
    }
});
//if (event.altKey && event.code === 'KeyS'){}  