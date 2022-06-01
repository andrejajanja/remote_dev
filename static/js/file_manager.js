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
const file_loader = document.getElementById("file_loader")

glavna_forma_form.addEventListener("submit", async function(e){        
    e.preventDefault();
    if(e.submitter.dataset["vrednost"] == "napravi")
    {
        let ime_fajla = prompt("Unesite ime fajla/foldera ovde:");
        var odgovor = await posalji_req_json({akcija:"napravi", "ime": ime_fajla}, "POST")
        napravi_dugmad(odgovor)                 
    }
    if(e.submitter.dataset["vrednost"] == "obrisi")
    {                               
        if(adres_traka.innerHTML.slice(34) == "root_fold"){
            alert("Ne mozete obrisati glavni direktorijum")
        }
        else{
            let obris_file = prompt("Da li sigurno zelite da obirsete izabran file/folder? (izbrisite _ da bi potvrdili)", "_");
            if (obris_file == "") {
                var odgovor = await posalji_req_json({akcija:"obrisi"}, "POST")
                napravi_dugmad(odgovor)
            }else{
                return;
            }
        }
        
    }

    if(e.submitter.dataset["vrednost"] == "preuzmi")
    {

    }

    if(e.submitter.dataset["vrednost"] == "posalji")
    {
        file_loader.click();        
    }

    if(e.submitter.dataset["vrednost"] == "nazad")
    {                                           
        window.location.href = "https://janja.xyz/coding";
    }
})

file_explorer_form.addEventListener('submit', async function(e){
    e.preventDefault();

    var odgovor = await posalji_req_json({lokacija: e.submitter.dataset['put']}, "POST")
    napravi_dugmad(odgovor)

    if(odgovor.hasOwnProperty("prebaci"))
    {
        window.location.href = "https://janja.xyz/coding";
    }

})

file_loader.onchange = async function(e){   
    alert("Otpremanje fajlova otpočelo.")
    let slanje = new FormData();

    for (let i = 0; i < file_loader.files.length; i++) {        
        slanje.append("fajlovi", file_loader.files[i]);        
    }

    const podaci = await fetch(url_stranice, {
        method: "PUT",
        body: slanje,        
    })
    .then(response => {
        if (!response.ok) {
          throw Error(response.status+' '+response.statusText)
        }
      
        if (!response.body) {
          throw Error('ReadableStream not yet supported in this browser.')
        }
      
        // to access headers, server must send CORS header "Access-Control-Expose-Headers: content-encoding, content-length x-file-size"
        // server must send custom x-file-size header if gzip or other content-encoding is used
        const contentEncoding = response.headers.get('content-encoding');
        const contentLength = response.headers.get(contentEncoding ? 'x-file-size' : 'content-length');
        if (contentLength === null) {
          throw Error('Response size header unavailable');
        }
      
        const total = parseInt(contentLength, 10);
        let loaded = 0;
      
        return new Response(
          new ReadableStream({
            start(controller) {
              const reader = response.body.getReader();
      
              read();
              function read() {
                reader.read().then(({done, value}) => {
                  if (done) {
                    controller.close();
                    return; 
                  }
                  loaded += value.byteLength;
                  console.log(Math.round(loaded/total*100)+'%');
                  controller.enqueue(value);
                  read();
                }).catch(error => {
                  console.error(error);
                  controller.error(error)                  
                })
              }
            }
          })
        );
      })
      .then(response => response.blob())
      .then(data => {
        console.log('download completed');
        // document.getElementById('img').src = URL.createObjectURL(data);
      })
      .catch(error => {
        console.error(error);
      });       

    while (file_loader.length > 0) {
        file_loader.pop();
    } 

    alert("Završeno otpremanje fajlova")    
}