import csv,hashlib,os,random,string


#region FUNKCIJE ZA RAD SA NALOZIMA i sesijama
def ucitaj_hash_user_pass(path_do_csv):
    hash_user,hash_pass =[],[]
    with open(path_do_csv, "r+") as file:
                citac = csv.reader(file)
                zaglavlje = next(citac)
                for red in citac:
                    hash_user.append(red[0]) 
                    hash_pass.append(red[1])
    return hash_user,hash_pass

def ucitaj_sve_sesijske_podatke(path_do_csv):
    podaci = []
    with open(path_do_csv, "r+") as file:
        citac = csv.reader(file)
        zaglavlje = next(citac)
        for red in citac:
            podaci.append(red)            
    return podaci
#endregion FUNKCIJE ZA RAD SA NALOZIMA i sesijama

#region korisne male funkcije
def encrypt(plaintext: str):
    return hashlib.md5(plaintext.encode()).hexdigest()

def nasumicni_string(x: int):    
    return "".join(random.choice(string.ascii_letters) for i in range(x))

#endregion korisne male funkcije