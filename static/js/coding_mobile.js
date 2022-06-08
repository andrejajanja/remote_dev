function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
async function posalji_req_json(data, tip)
{
    const podaci = await fetch(url_stranice, {
        method: tip,
        body: new URLSearchParams(data)
    })
    .then((response) => response.json())
    .then((pod) => {return pod;});
    return podaci;
}

const url_stranice = window.location.href;

const glavna_forma_form = document.querySelector("#glavna");
const code_povrs = document.querySelector("#povrsina_kodiranje");
const konzola = document.getElementById("koznola_deo");
const sacuvaj_dugme = document.getElementById("sacu");
const izvrsi_dugme = document.getElementById("izvr")

let jeste_konzola = true
let inicijalni_odgovor="";
let pom_konzola = "";
let izvrsava = false;
let konzo = "";
glavna_forma_form.addEventListener("submit", async function(e){
    e.preventDefault()                       
    if(e.submitter.dataset.funkcija == "odjava"){                                             
        odgovor = await posalji_req_json({izloguj: "pokreni"}, "POST")
        window.location.href = "https://janja.xyz/"
    }

    if(e.submitter.dataset.funkcija == "Izvrsi"){
        konzola.value = konzo
        if (izvrsi_dugme.value == "Zaustavi") {
            izvrsava = false                    
            izvrsi_dugme.value = "Izvrši";
            odgovor = await posalji_req_json({kontrola: "zaustavi"}, "POST")                                
            return;
        }

        izvrsi_dugme.value = "Zaustavi";
        izvrsava = true
        odgovor = await posalji_req_json({kontrola: "izvrsi"},"POST");
        
        if(odgovor["konzola"] == 0){
            konzola.value = "Neophodan je ime_fajla.py file da biste ga izvrsili";
            izvrsi_dugme.value = "Izvrši";                  
            return;
        }                
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
            pom_konzola = await posalji_req_json({kontrola: "proveri_konzolu"}, "POST")
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
        izvrsi_dugme.value = "Izvrsi";        
        izvrsava = false
        konzo = konzola.value;
        return;
    }        

    if(e.submitter.dataset.funkcija == "fajlovi"){                
        window.location.href = "https://janja.xyz/file_explorer"
    }

    if(e.submitter.dataset.funkcija == "Sacuvaj"){                
        sacuvaj_dugme.disabled = true;
        odgovor = await posalji_req_json({kontrola: "sacuvaj", code: code_povrs.value},"POST")

        if(odgovor["status"]){                    
            sacuvaj_dugme.value = "Uspesno"                                    
        }
        else{                    
            sacuvaj_dugme.value = "Greska"
        }
        await sleep(1000);
        sacuvaj_dugme.disabled = false;
        sacuvaj_dugme.value = "Sačuvaj"
        return;
    }

    if(e.submitter.dataset.funkcija == "ocisti"){
        konzola.value=""
        konzo = ""
        jeste_konzola = true
        return;
    }

    if(e.submitter.dataset.funkcija == "terminal"){
        let komanda = konzola.value.substring(konzo.length);
        konzo = konzola.value;
        console.log(komanda);
        //zavrsi slanje requesta i serversku funkcionalnost za izvrsavanje komande
        return;
    }
})
konzola.onkeyup = function(){
    if(konzola.value.indexOf(konzo) === -1){
        konzola.value = konzo
    }
};