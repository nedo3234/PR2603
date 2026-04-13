# Vmesno poročilo

## Problem

Cilj projekta je analizirati trg avtomobilov v Sloveniji in razumeti vedenje kupcev na podlagi registriranih vozil. Zanimalo nas je, kateri tipi vozil prevladujejo, kako se spreminjajo trendi glede pogona (bencin, dizel, elektrika) ter kakšna je starostna in znamčna struktura voznega parka.

Posebej smo se osredotočili na vprašanja, ali se slovenski trg približuje evropskim trendom elektrifikacije in trajnostne mobilnosti ter kako hitro se obnavlja vozni park. Na podlagi teh analiz želimo oceniti prihodnje trende in preference kupcev ter razumeti, kakšen razvoj lahko pričakujemo na slovenskem trgu avtomobilov.

## Podatki, ki smo jih obravnavali

Uporabili smo javno dostopne podatke iz evidence registriranih vozil v Sloveniji za leto 2023:  
[https://podatki.gov.si/dataset/evidenca-registriranih-vozil-presek-stanja](https://podatki.gov.si/dataset/evidenca-registriranih-vozil-presek-stanja)

Podatkovni set vsebuje različne informacije o vozilih, kot so datum prve registracije, lokacija registracije, znamka in model, vrsta goriva, emisije CO₂, masa vozila, moč motorja in prevoženi kilometri.

Ker podatki vsebujejo tudi veliko nerelevantnih atributov (npr. administrativne oznake), smo izvedli čiščenje podatkov v Excelu in Pythonu (knjižnica pandas). Odstranili smo manjkajoče in nelogične vrednosti ter poenotili zapise kategorij (npr. vrste goriva).

Za analizo smo uporabili:

-   Python (pandas za obdelavo podatkov)
-   matplotlib in seaborn za vizualizacijo
-   osnovne statistične metode (porazdelitve, korelacije, primerjave skupin)

Grafi in rezultati temeljijo na lastni izvorni kodi, ki je vključena v projekt.

## Ugotovitve do sedaj

Najprej smo analizirali trende glede vrste goriva. Opazili smo, da v zadnjih letih prevladujejo bencinska vozila, medtem ko delež dizelskih vozil postopoma upada.

**bencin_dizel_trend.png**

Ta trend lahko razložimo z več dejavniki. V Evropi se po letu 2015 zmanjšuje priljubljenost dizelskih vozil, predvsem zaradi okoljskih regulacij in afer povezanih z emisijami. Poleg tega so dizelski motorji manj primerni za kratke mestne vožnje, ki postajajo vedno pogostejše.

Opazili smo tudi izrazit porast električnih in hibridnih vozil.

**ev_rast.png**

Podrobnejša analiza pokaže, da se je rast začela okoli leta 2016. To sovpada z več dejavniki: državnimi subvencijami, padanjem cen baterij ter večjo dostopnostjo električnih vozil. Tudi na ravni Evropske unije se spodbuja zmanjševanje emisij, kar dodatno vpliva na odločitve kupcev.

Regionalna analiza kaže, da je rast električnih vozil najizrazitejša v večjih mestih, kot sta Ljubljana in Maribor.

**ev_regije.png**

To je pričakovano, saj imajo urbana območja bolj razvito infrastrukturo (polnilnice), višji dohodek prebivalcev ter večjo okoljsko ozaveščenost. Prav tako mestni promet bolj ustreza električnim vozilom zaradi krajših razdalj.

Pri analizi znamk električnih vozil smo ugotovili, da izstopa Toyota.

**ev_znamke.png**

To lahko pripišemo dejstvu, da Toyota že dolgo razvija hibridna vozila, ki so cenovno dostopnejša kot popolnoma električna vozila in zato predstavljajo vmesno stopnjo prehoda.

## Katera vozila pa največkrat vidimo na cestah

Analiza starosti vozil pokaže, da je največ vozil starih med 10 in 15 let.

**starost_porazdelitev.png**

To pomeni, da slovenski vozni park temelji predvsem na rabljenih vozilih. V primerjavi z zahodno Evropo je povprečna starost vozil v Sloveniji višja, kar kaže na počasnejšo obnovo voznega parka. Razlogi za to so lahko nižja kupna moč ter večja uporaba uvoženih rabljenih vozil.

Pri starejših vozilih (nad 20 let) število hitro upada, kar je posledica tehničnih omejitev, okvar ter strožjih okoljskih standardov.

Analizirali smo tudi najbolj popularne znamke vozil.

**znamke_popularnost.png**

Ugotovili smo, da je Volkswagen najbolj zastopana znamka, sledijo pa Renault in druge evropske znamke. Ta rezultat je pričakovan, saj imajo evropski proizvajalci dolgo tradicijo na tem trgu ter dobro razmerje med ceno in kakovostjo.

S pomočjo heatmap analize smo preverili razširjenost znamk po regijah.

**heatmap_znamke.png**

Rezultati potrjujejo, da Volkswagen prevladuje v večini regij, kar kaže na enotne preference kupcev po celotni državi.

## Kaj pa emisije

Analizirali smo povezavo med maso vozila in porabo ter maso in močjo motorja.

**masa_poraba.png**

**masa_moc.png**

Rezultati kažejo, da ni močne linearne korelacije. To pomeni, da sama masa vozila ni dovolj za napoved porabe ali moči, saj pomembno vlogo igrajo tudi tehnologija motorja, tip goriva in aerodinamične lastnosti.

Nato smo primerjali napovedane in dejanske emisije CO₂.

**co2_primerjava.png**

Opazili smo določena odstopanja, kar kaže na razliko med laboratorijskimi meritvami in dejanskimi pogoji vožnje. To je znan problem v avtomobilski industriji, kjer standardizirani testi ne odražajo vedno realne uporabe.

Pomembna ugotovitev je, da imajo vozila na fosilna goriva bistveno višje emisije kot električna in hibridna vozila. Električna vozila nimajo neposrednih emisij CO₂, medtem ko hibridi zmanjšujejo porabo predvsem v mestnih razmerah.

Na podlagi teh rezultatov lahko sklepamo, da se bo trend prehoda na okolju prijaznejša vozila nadaljeval. K temu prispevajo zakonodaja, subvencije, višje cene goriv ter večja okoljska ozaveščenost prebivalcev.

Dolgoročno lahko pričakujemo zmanjševanje deleža vozil na dizel, stabilizacijo bencinskih vozil ter hitro rast električnih vozil, še posebej v urbanih območjih.
