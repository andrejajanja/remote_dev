import os,hashlib,random,string,csv

def napravi_fajl(path):
    open(path,mode="w").close()

def napravi_nalog(user, passw, boja):
    userh,passwh = encrypt(user),encrypt(passw)
    main_path = r"E:\remote_dev_server_data/"
    korsnik_path = r"E:\remote_dev_server_data\korisnicki_folderi/" + nasumicni_string(10)
    with open(main_path + "napravljeni_nalozi.txt", "a") as file:
        file.write(f"{user} {passw}\n")
    os.mkdir(korsnik_path)
    os.mkdir(korsnik_path+"/folder")
    napravi_fajl(korsnik_path+"/skripta.py")
    with open(main_path + "nalozi.csv", "a", newline="\n") as file:
        upisivac = csv.writer(file)
        upisivac.writerow([userh,passwh])

    with open(main_path + "seijsi_podaci.csv", "a", newline="\n") as file:
        upisivac = csv.writer(file)
        upisivac.writerow([korsnik_path, boja])

def encrypt(plaintext: str):
    return hashlib.md5(plaintext.encode()).hexdigest()

def nasumicni_string(x: int):    
    return "".join(random.choice(string.ascii_letters) for i in range(x))

#C:\Users\Andreja\Documents\Artificial_Inteligence\uho,"rgb(171, 248, 194)"

boja = "rgb(171, 248, 194)"
user = input("Unesite ime korisnika: ")
passw = input("Unesite prolaznu rec korisnika: ")
napravi_nalog(user,passw, boja)
#for x in range(1,10):
    #napravi_nalog(f"Korsnik{x}",f"000{x}", boja)
#for x in range(10):
    #napravi_nalog(f"korisnik{x}",f"000{x}", boja)
