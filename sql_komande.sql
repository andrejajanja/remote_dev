CREATE TABLE Korisnici(
    id_korisnika int PRIMARY KEY,
    ime varchar(255),
    pass varchar(255),
    lokacija_foldera varchar(511),
    boja varchar(30)
);

CREATE TABLE trenutni_ulogovani(
    id_korisnika char(10) PRIMARY KEY,
    ime varchar(255),
    pass varchar(255)
);

INSERT INTO Korisnici
VALUES (NULL, "Andreja", "d69bca6a08af4fda3f595e68a922f18b", "C:\Artificial_Inteligence\uho","rgb(171, 248, 194)");