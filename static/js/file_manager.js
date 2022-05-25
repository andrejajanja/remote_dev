async function posalji_req_json(data, tip){
    const podaci = await fetch(url_stranice, {
        method: tip,
        body: new URLSearchParams(data)
    })
    .then((response) => response.json())
    .then((pod) => {return pod;});
    return podaci;
}
const url_stranice = window.location.href;

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
    adres_traka.innerHTML = "Trenutni otvoreni file/folder:<br>"+elems["trenutni_fajl"]
}

async function uzmi_elemente(){
    elementi = await posalji_req_json({"dinamicki_elememnti": "bilo_sta"}, "POST") 
    napravi_dugmad(elementi)
}
uzmi_elemente()

const file_explorer_form = document.querySelector("#file_explorer");
const adres_traka = document.querySelector("#adresna_traka")
const glavna_forma_form = document.querySelector("#glavna_forma");
const ime_fajla = document.querySelector("#file_ime_input");
const kutija_za_dugmice = document.querySelector("#files_view")


glavna_forma_form.addEventListener("submit", async function(e){        
    e.preventDefault();

    if(e.submitter.dataset["vrednost"] == "napravi")
    {
        if(ime_fajla.value=="")
        {
            alert("Ne mozete da napravite fajl/folder bez unetog imena")
            
        }
        else
        {
            var odgovor = await posalji_req_json({akcija:"napravi", "ime": ime_fajla.value}, "POST")
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
                var odgovor = await posalji_req_json({akcija:"obrisi"}, "POST")
                napravi_dugmad(odgovor)
            }else{
                return;
            }
        }
        
    }

    if(e.submitter.dataset["vrednost"] == "nazad")
    {                                           
        window.location.href = "http://janja.xyz/coding";
    }
})

file_explorer_form.addEventListener('submit', async function(e){
    e.preventDefault();

    var odgovor = await posalji_req_json({lokacija: e.submitter.dataset['put']}, "POST")
    napravi_dugmad(odgovor)

    if(odgovor.hasOwnProperty("prebaci"))
    {
        window.location.href = "http://janja.xyz/coding";
    }

})