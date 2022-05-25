function enkriptuj(plaintext)
{
    if(plaintext != null && plaintext != undefined) {                
        return md5(plaintext);
    }
    else
    {
        return 0
    }            
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

glavna_forma_form.addEventListener("submit", async function(e){  
    e.preventDefault();
    if(e.submitter.dataset.funkcija == "Login")
    {                         
        let hash_user = enkriptuj(glavna_forma_form.ime_korisnika.value)  
        let hash_pass = enkriptuj(glavna_forma_form.prolazana_rec.value)                  
        let data = {login: "probaj" ,username: hash_user, password:hash_pass};
        const respo = await posalji_req_json(data, "POST");
        if(respo.autentifikacija == "neuspesna")
        {
            document.getElementById("poruka").innerHTML= "Pogresno korisničko ime ili prolazna reč";
        }
        else
        {
            window.location.href = "https://janja.xyz/coding";
        }                
    }
})