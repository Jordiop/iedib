### Practica 7
#### Part A - Models extensos de llenguatge

Sobre un xatbot basat en LLM de la vostra elecció (ChatGPT, Gemini, Claude, DeepSeek) escriviu un llibre d'un mínim de dotze pàgines seguint el següent esquema.

1) Escriviu un prompt inicial prou llarg, explicant el text que voleu produir, el títol de la vostra obra, l'audiència, l'estil, la longitud de cada capítol i demanau una proposta d'índex de dotze capítols. El text pot ser de qualsevol estil que volgueu: ficció, d'assaig, tècnic...

Es farà servir Claude, amb la característica dels projectes. Què son els projectes? Els projectes són una manera de treballar amb Claude que permet crear documents llargs i estructurats. Podeu crear un projecte i demanar-li a Claude que generi un llibre sencer, amb capítols i seccions podria ser una bona opció per a la nostra pràctica. 

Així doncs, el primer pas és crear un projecte. Un cop creat el projecte, li donarem un contexte. Aquest contexte serà el nostro primer prompt. El prompt ha de ser llarg i detallat, explicant el text que volem produir, el títol de la nostra obra, l'audiència, l'estil, la longitud de cada capítol i demanant una proposta d'índex de dotze capítols.

A nivell tènic, faré us del darrer model de Claude, el Claude 3.7 Sibbet. Té certes limitacions en la longitud de text que pot generar, així que és millor dividir el llibre en capítols i demanar-li a Claude que generi un capítol a la vegada.

```
# PROMPT INICIAL: CREACIÓ D'UN LLIBRE DE FANTASIA

Vull crear un llibre de fantasia titulat "Les Cròniques d'Anthea: El Despertar dels Antics". L'obra està dirigida a joves adults i adults aficionats al gènere de la fantasia èpica, especialment aquells que gaudeixen d'universos màgics ben desenvolupats, amb sistemes de màgia originals i una mitologia profunda.

## SOBRE L'OBRA

### Títol
"Les Cròniques d'Anthea: El Despertar dels Antics"

### Audiència
Joves adults i adults aficionats a la fantasia èpica (16+ anys). Lectors que aprecien mons complexos, personatges amb profunditat psicològica i trames que combinen aventura, política i dilemes morals.

### Estil
Narrativa en tercera persona amb focalització variable que segueix diferents personatges. L'estil serà immersiu i descriptiu, amb diàlegs naturals i moments de reflexió. Combinaré escenes d'acció intensa amb passatges més introspectius i de construcció de món.

Vull un equilibri entre:
- Descripcions vívides però no excessives
- Diàlegs que reflecteixin la personalitat i origen de cada personatge
- Un to que fluctuï entre el meravellós, el misteriós i, en alguns moments, el fosc
- Ús ocasional de metàfores relacionades amb la natura i els elements màgics del món
- Moments d'humor subtil per alleujar la tensió

### Longitud dels capítols
Cada capítol ha de tenir una longitud d'aproximadament 2.000-2.500 paraules, amb una estructura que mantingui l'interès del lector. Els capítols han de tenir un bon ganxo inicial i un final que convidi a continuar llegint.

### Premissa del món
Anthea és un continent dividit en cinc regnes, cadascun vinculat a un element primordial i amb una forma única de màgia. Durant mil·lennis, un pacte ancestral ha mantingut l'equilibri entre aquests poders, però ara antigues entitats anomenades "Els Antics" comencen a despertar del seu somni etern, amenaçant amb trencar aquest equilibri. La història segueix diversos personatges els destins dels quals s'entrecreuen mentre intenten entendre i enfrontar-se a aquesta amenaça creixent.

### Personatges principals
1. **Elian Ventris** - Un jove cartògraf i explorador del Regne de Ventia (aire) amb l'habilitat secreta de veure corrents màgics.
2. **Nyara Emberfell** - Una guerrera i maga del foc del Regne d'Ignis, exiliada per raons polítiques.
3. **Thorn Deeproot** - Un druida ancià del Regne de Terrus, que porta segles estudiant els textos prohibits sobre Els Antics.
4. **Lyrella Tidecaller** - Una princesa del Regne d'Aquaria amb visions profètiques que ningú creu.
5. **Kairos Shadoweave** - Un enigmàtic assassí vinculat al Regne de Penumbra, l'últim descendent d'una línia de guardians.

### Aspectes importants a incloure
- Un sistema de màgia original basat en els cinc elements primordials
- Criatures fantàstiques úniques per a aquest món
- Dilemes morals complexos on no hi ha respostes òbvies
- Exploració de temes com el poder, el sacrifici, la identitat i la responsabilitat
- Mitologia rica que es va revelant progressivament
- Mapes i descripcions geogràfiques detallades

### Necessitats específiques
Necessito un índex detallat amb títols per a dotze capítols que formin una narrativa coherent i atractiva, acompanyat d'un breu resum de cadascun. Aquesta estructura ha de permetre crear una obra coherent que estableixi el món, presenti els personatges principals, desenvolupi els conflictes centrals i culmini amb un final que resolgui algunes trames però deixi portes obertes per a possibles continuacions.

Per favor, proposa un índex amb títols evocadors i una breu sinopsi per a cada capítol que em permeti començar a desenvolupar aquesta història.

Índex

Vents de Canvi
Flames de l'Exili
Arrels Profundes
----
Visions Aquàtiques
Ombres Ancestrals
La Confluència
El Mapa Fragmentat
Runes Prohibides
El Consell dels Cinc
El Santuari Perdut
El Ritual Trencat
Despertar
```

2) Amb prompts successius breus anau extraient els capítols consecutius de la vostra obra. Podeu inserir correccions si el resultat que obteniu no s'ajusta a la vostra idea.

El llibre resultant és un llibre de fantasia titulat "Les Cròniques d'Anthea: El Despertar". He creat un índex amb dotze capítols i he generat els tres primers capítols. Els capítols són:
- **Capítol 1: Vents de Canvi** - Presenta el món d'Anthea i els personatges principals, centrant-se en Elian Ventris, un jove cartògraf que descobreix un mapa antic que revela la ubicació d'un dels Antics.
- **Capítol 2: Flames de l'Exili** - Introduïm Nyara Emberfell, una guerrera del foc que busca venjança contra els que la van exiliar. La seva història es creua amb la d'Elian quan descobreixen un enemic comú.
- **Capítol 3: Arrels Profundes** - Thorn Deeproot, un druida del Regne de Terrus, descobreix que els Antics han començat a despertar. La seva recerca de coneixement el porta a unir-se amb Elian i Nyara.
No crearé més capítols, ja que el llibre és massa llarg. En el moment de fer la pràctica, hi ha una limitació en les converses.

3) Obteniu la URL de la conversa i afegiu-la al quadern de Colab que lliurareu en aquesta tasca.

Capitol 1: 
- Site: [Capitol 1 web](https://claude.site/artifacts/a8e6de69-c8d1-4c54-b2c7-4eab35d7a173)
- Conversation: [Capitol 1 conversa](https://claude.ai/share/c9680f64-5f14-4303-ac28-bed2c468bd53)

Capitol 2:
- Site: [Capitol 2 web](https://claude.site/artifacts/cd5e3a08-472f-4405-ad37-e0536ab55315)
- Conversation: [Capitol 2 conversa](https://claude.ai/share/c9680f64-5f14-4303-ac28-bed2c468bd53)

Capitol 3:
- Site: [Capitol 3 web](https://claude.site/artifacts/23e34483-1382-4bb2-a838-ef3adf06c000)
- Conversation: [Capitol 3 conversa](https://claude.ai/share/c9680f64-5f14-4303-ac28-bed2c468bd53)

4) Valorau el resultat obtingut. Fins a quin punt serveix com a producte final? Necessita molta més feina? El resultat és més bo o més dolent del que esperàveu?

El resultat obtingut és un bon punt de partida per a una obra de fantasia. Els capítols generats presenten un món interessant i personatges amb potencial per a un desenvolupament més profund. La narrativa és coherent i manté l'interès del lector, però hi ha aspectes que podrien millorar-se: 
- **Profunditat dels Personatges**: Encara que els personatges són interessants, podrien desenvolupar-se més les seves motivacions i conflictes interns.
- **Detalls del Món**: La descripció del món d'Anthea és atractiva, però es podria aprofundir més en la seva història i cultura.
- **Diàlegs**: Els diàlegs són naturals, però podrien ser més distintius per a cada personatge, reflectint millor les seves personalitats i orígens.
- **Ritme**: El ritme de la narrativa és adequat, però alguns passatges podrien ser més dinàmics o intensos per mantenir l'interès del lector.