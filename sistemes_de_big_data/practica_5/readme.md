Apartat 1. Gràfics amb Matplotlib, Seaborn, Plotly i Dash

En el catàleg de dades obertes del Govern d'Espanya podem trobar una gran quantitat de conjunts de dades elaborats per l'Institut Nacional d'Estadística. En concret, nosaltres farem feina amb el dataset de naixements per edat de la mare i ordre de naixement. Podeu emprar el fitxer CSV separat ; (que també trobareu al repositori del curs).

Ens interessa agrupar les edats de la mare en els següents cinc grups:

    Fins a 19 anys
    De 20 a 29 anys
    De 30 a 39 anys 
    De 40 a 49 anys
    50 anys o més

I també volem agrupar l'ordre de naixement de la mare (primer fill, segon fill, etc.) en els següents tres grups:

    Primer fill
    Segon fill
    Tercer fill o posterior


Fes un quadern de Colab on es generin els gràfics següents:

    Gràfic circular amb Matplotlib que mostri el percentatge de naixements a tot Espanya en 2023 segons el grup d'edat de la mare. Cada grup d'edat ha de tenir un color diferent. Fes servir una paleta de Seaborn per als colors.
    Gràfic de barres verticals agrupades amb Seaborn (sense mostrar la barra d'errors), que mostri en l'eix X les comunitats autònomes mediterrànies (Illes Balears, Catalunya, Comunitat Valenciana, Regió de Múrcia i Andalusia) i en l'eix Y el nombre de naixements en l'any 2023, amb els valors agrupats per grup d'edat. Per a una comunitat autònoma, podeu fer una barra per a cada grup d'edat, o bé una única barra amb colors diferents per a cada grup d'edat. En qualsevol cas, cada grup d'edat ha de tenir un mateix color en tot el gràfic i s'ha de mostrar en una llegenda.
    Gràfic de barres verticals agrupades amb Plotly (sense mostrar la barra d'errors), que mostri en l'eix X l'any (de 2009 a 2023) i en l'eix Y el nombre de naixements, agrupats per ordre de naixement (agrupats com hem dit abans, en primer, segon i tercer o posterior). Per a un any, podeu fer una barra per a cada ordre de naixement, o bé una única barra amb colors diferents per a cada ordre. En qualsevol cas, cada ordre de naixement ha de tenir un mateix color en tot el gràfic i s'ha de mostrar en una llegenda. 
    Gràfic de línies i punts amb Seaborn que mostri l'evolució en el nombre de naixements a Espanya en el període 2009-2023. S'han de mostrar 3 línies, una per cada ordre de naixement (agrupats com hem dit abans). Cada una de les tres línies ha de tenir un color diferent i s'ha de mostrar en una llegenda.
    Gràfic de línies i punts amb Plotly que mostri l'evolució en el nombre de naixements a les Illes Balears en el període 2009-2023. S'han de mostrar 5 línies, una per cada grup d'edat de la mare. Cada una de les cinc línies ha de tenir un color diferent i s'ha de mostrar en una llegenda.
    Diagrama de caixes (boxplot) amb Seaborn que mostri el nombre de naixements a les Illes Balears al llarg del període 2009-2023, per a cada un dels grups d'edat. Cada grup d'edat ha de tenir un color diferent i s'ha de mostrar en una llegenda.
    Diagrama de caixes (boxplot) amb Plotly que mostri el nombre total de naixements del període 2009-2023, per a cada comunitat autònoma mediterrània. Cada comunitat autònoma ha de tenir un color diferent i s'ha de mostrar en una llegenda.
    Interfície amb Dash que permeti seleccionar una comunitat o ciutat autònoma, i mostri un diagrama de barres verticals agrupades que mostri en l'eix X el grup d'edat, en l'eix Y el nombre de naixements, amb els valors agrupats per ordre de naixement (primer fill, segon fill, etc.). Cada ordre de naixement ha de tenir un color diferent i s'ha de mostrar en una llegenda.


Tots els gràfics han de tenir un títol. I quan tenguin eixos, també s'hi ha d'incloure una etiqueta per a cada eix.



Apartat 2. Sèries temporals amb Datashader

En aquest apartat farem feina amb el dataset de les dades de qualitat de l'aire per hores de Castella i Lleó. En concret, ens centrarem en l'estació Renault1 de la província Valladolid.

En la columna Fecha apareix la data i l'hora de cada mesura. 

Volem representar gràficament aquesta sèrie temporal emprant Datashader. Heu d'obtenir les següents tres imatges

    Sèrie temporal de la variable monòxid de nitrogen (NO (ug/m3)) 
    Sèrie temporal de la variable diòxid de nitrogen (NO2 (ug/m3)) 
    Ambdues sèries en una única imatge, cada una d'un color diferent



Apartat 3. Visualització espacial amb Datashader

L'Ajuntament de Barcelona publica un dataset dels arbres dels carrers de la ciutat (arbrat viari) al seu catàleg de dades obertes. Són quasi 150.000 arbres.

Volem obtenir una imatge amb Datashader que mostri la ubicació de tots els arbres del municipi. Per fer-ho, heu d'emprar les columnes x_etrs89 i y_etrs89, que ja estan en un sistema de coordenades projectat. Fes servir una paleta de colors que permeti identificar clarament les zones amb més densitat d'arbres. 


