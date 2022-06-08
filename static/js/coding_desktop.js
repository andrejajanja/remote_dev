//funkcije
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

async function napravi_fajl_folder(){
    let ime_fajla = prompt("Unesite ime fajla/foldera ovde:");
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

async function izvrsi_fajl(){
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

    izvrsi_dugme.value = "Izvrši";
    izvrsi_dugme.dataset.funkcija = "Izvrsi"
    izvrsava = false
    return;
}

async function zaustavi_izvrsavanje(){
    izvrsava = false                    
    izvrsi_dugme.value = "Izvrši";
    izvrsi_dugme.dataset.funkcija = "Izvrsi"
    odgovor = await posalji_req_json({kontrola: "zaustavi"}, "POST", url_code)                                 
    return;
}

//programske promenljive
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
const file_loader = document.getElementById("file_loader");
const slika_kont = document.getElementById("slika_kontejner")

const eks_slika = ["jpg","png","jpeg","ico","bmp"]
const eks_txt = ["py","pyw","txt","html","css","js","md","xml","csv"]

let jeste_konzola = true
let inicijalni_odgovor="";
let pom_konzola = "";
let izvrsava = false;

uzmi_elemente()

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
    let eks = ekstencija_od_imena(e.submitter.dataset["put"])    

    if(eks == "folder"){
        let odgovor = await posalji_req_json({lokacija: e.submitter.dataset['put']}, "POST", url_filesistem);
        napravi_dugmad(odgovor)
        return;
    }
    
    if(eks_txt.includes(eks)){     
        let odgovor = await fetch(url_filesistem, {method: "POST",body: new URLSearchParams({lokacija: e.submitter.dataset['put']})
        })
        .then(response => {return response.text()})
        slika_kont.style.display = "none";
        code_povrs.style.display = "block";
        code_povrs.value = odgovor;
    }
    else if(eks_slika.includes(eks)){
        
        let odgovor = await fetch(url_filesistem, {method: "POST",body: new URLSearchParams({lokacija: e.submitter.dataset['put']})
        })
        .then(response =>{return response.text()})
        code_povrs.value = "";
        code_povrs.style.display = "none";
        slika_kont.style.display = "block";
        slika_kont.src = "data:image/png;charset=utf-8;base64," + odgovor;
    }
    else{
        slika_kont.style.display = "none";
        code_povrs.style.display = "block";
        code_povrs.value = "Fajl se ne moze interpretirati kao slika ili tekst";
    }

    uzmi_elemente();    
})

forma_zaglavlje.addEventListener("submit", async function(e){
    e.preventDefault();                       
    if(e.submitter.dataset.funkcija == "odjava"){                                             
        odgovor = await posalji_req_json({izloguj: "pokreni"}, "POST", url_code)
        window.location.href = "https://janja.xyz"
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
});
//if (event.altKey && event.code === 'KeyS'){}  