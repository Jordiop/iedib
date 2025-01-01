Què he de fer?

En aquesta tasca anam a treballar amb HBase. Tenim una taula vehicles per gestionar un sistema de venda de vehicles de segona mà. La taula té 4 famílies de columnes: info_general, conservacio, propietari i ubicacio.

Aquesta taula mostra les dades que ha de contenir la taula vehicles:

clau 	info_general 	conservacio 	propietari 	ubicacio
	marca 	model 	matricula 	preu 	any 	km 	estat 	nif 	nom 	telefon 	mail 	ciutat 	illa 	longitud 	latitud
1 	Toyota 	Corolla 	1234ABC 	12000 	2015 	120000 	bo 	12345678A 	Joan Martínez 	623456789 	joan.martinez@email.com 	Palma 	Mallorca 	2.650160 	39.569600
2 	Ford 	Focus 	5678DEF 	15500 	2018 	55000 	molt bo 	87654321B 	Ana García 		ana.garcia@email.com 	Palma 	Mallorca 		
3 	Honda 	Civic 	9012GHI 	18000 	2020 	20000 	bo 	11223344C 	David López 	655123456 		Eivissa 	Eivissa 	1.452850 	38.916280
4 	Mercedes-Benz 	A-Class 	3456JKL 	30000 	2019 	40000 	bo 	22334455D 	Maria Sánchez 	672345678 		Manacor 	Mallorca 	3.703790 	40.416780
5 	BMW 	X5 	7890JKL 	25000 	2017 	70000 	bo 	33445566E 	Jordi Pérez 		jordi.perez@email.com 	Ciutadella 	Menorca 	0.376288 	39.469907
6 	Audi 	A4 	1122XYZ 	20000 	2016 	80000 	molt bo 	44556677F 	Laura Martín 	687654321 	laura.martin@email.com 	Maó 	Menorca 		


Has de seguir les següents passes:

- Crea la taula vehicles en HBase.
- Insereix mitjançant ordres put les tres primeres files de la taula.
- Fes un fitxer CSV amb les 3 darreres files i carrega'l a la taula.
- Mostra totes les dades de la fila 4 amb un get.
- Mostra les dades d'informació general de la taula amb un scan.
- Mostra totes les dades dels vehicles amb estat bo.
- Mostra les dades dels propietaris dels vehicles de Mallorca.
- Mostra la informació general dels vehicles que siguin posteriors al 2017 (inclòs) amb menys de 50000 km.
- Modifica la fila 2 i posa-li el telèfon 656123321
- Esborra totes les dades la fila 5.
- Crea una taula externa en Hive vinculada a la taula vehicles d'HBase.
- Fes una consulta en HiveQL que retorni les dades d'informació general dels vehicles de Palma.
- Fes una consulta en Impala que retorni totes les dades dels 3 vehicles més cars.
- Fes una consulta en HiveQL que agrupi els vehicles per estat i mostri la mitjana de km de cada estat.
- Fes una consulta en Impala que agrupi els vehicles per illa i mostri el nombre de vehicles de cada illa.


Fes un document de text on, per a cada un dels 15 apartats, aparegui l'ordre corresponent. En el cas de l'apartat 3, si fas servir l'eina gràfica per fer la importació, no cal.
Fes un document amb Word, Write o Docs on s'inclogui almenys una captura de pantalla que mostri l'execució de cada apartat. Exporta'l a PDF quan hagis acabat.
A continuació, fes un fitxer zip (o tar o tar.gz) que contengui els dos documents anteriors, a més del fitxer CSV que has carregat a l'apartat 3. El nom del fitxer ha de ser de la forma tasca_4_Nom_Llinatge.zip. Per exemple tasca_4_Toni_Navarrete.zip. No posis accents ni caràcters no anglesos (ç, ñ, etc.) i si tens espais en blanc, substitueix-los per guions baixos.
Finalment, envia el teu fitxer comprimit (amb el botó "Afegeix la tramesa").