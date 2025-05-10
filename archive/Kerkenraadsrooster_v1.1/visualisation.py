# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 11:45:40 2024

@author: Levi
"""

import datetime

def create_grid(list_of_persons, begindatum, einddatum):
    """
    Deze functie maakt het uiterlijk van het rooster, zonder speciale dagen in te voegen. 
    De data van de zondagen worden ook in het rooster gezet, net als de namen van de ouderlingen
    en het o/a-ritme van ochtend- en avonddiensten.

    Parameters
    ----------
    list_of_persons : lijst van strings. 
        Geef een lijst met de namen van de kerkenraadsleden op volgorde van hun 
        functie in de kerkenraad. Als er een vacature is, gewoon "" invullen op 
        de juiste plek in de lijst.
    begindatum : string. 
        Vul de datum in van de zondag dat het rooster moet starten in de vorm "dd-mm-yyyy".
    einddatum : string.
        Vul de datum in van de zondag dat het rooster moet eindigen in de vorm "dd-mm-yyyy".

    Returns
    -------
    list of lists.

    """
    
    # Hier berekenen we het aantal zondagen dat het rooster duurt
    begindatum_datetime = datetime.datetime.strptime(begindatum, "%d-%m-%Y")
    einddatum_datetime = datetime.datetime.strptime(einddatum, "%d-%m-%Y")
    verschil_in_dagen = einddatum_datetime-begindatum_datetime
    aantal_zondagen = int((verschil_in_dagen.days)/7)+1
    print("Aantal zondagen = "+str(aantal_zondagen))
    
    aantal_personen = len(list_of_persons)
    
    # Hier berekenen we het aantal rijen en kolommen dat in het rooster moet komen.
    aantal_kolommen = 2*aantal_zondagen+2
    aantal_rijen = aantal_personen+2
    # We beginnen de bovenste rij met ongeveer de helft van het aantal kolommen, 
    # omdat er twee diensten per zondag zijn.
    rooster = [list(range(aantal_zondagen+2))]
    # Maakt het rooster
    for i in range(aantal_rijen):
        rooster.append(list(0 for j in range(aantal_kolommen)))
    
    # Vult wat speciale woorden voor het rooster in.
    rooster[0][0] = "Versie:"
    rooster[0][1] = begindatum
    rooster[0][-1] = "Voorkeuren:"
    
    # Bepaalt de data die in de kolommen komen te staan.
    for i in range(aantal_zondagen):
        nieuwe_datum = begindatum_datetime + datetime.timedelta(days=7*i)
        rooster[0][i+1] = nieuwe_datum.strftime("%d-%m-%Y")
    
    # Voegt de namen toe aan de eerste kolom.
    for i in range(aantal_personen):
        rooster[i+2][0] = list_of_persons[i]
    
    # Voegt o en a toe aan de tweede rij.
    for i in range(2*aantal_zondagen):
        if i % 2 == 0:
            rooster[1][i+1] = "o"
        else: rooster[1][i+1] = "a"
        
    print(rooster)
    return(rooster)




def adjust_grid_column(kolomnummer, datum, rooster, actie = "toevoegen", kant = "rechts", 
                       tijdstip = "o"):
    """
    Deze functie voegt de speciale dagen toe aan het rooster dat create_grid heeft gemaakt.

    Parameters
    ----------
    kolomnummer : integer.
        Vul het kolomnummer in van de kolom naast de nieuwe kolom die je in wil voegen.
    datum : string.
        Vul de datum in van de dag die je in wil voegen in de vorm "dd-mm-yyyy".
    rooster : list of lists.
        Vul de lijst van lijsten in die je met create_grid hebt gemaakt.
    kant : string.
        Vul "links" of "rechts" in. De nieuwe kolom verschijnt/verdwijnt aan die kant van 
        de kolom die je ingevuld hebt bij kolomnummer.
    actie : string.
        Vul "toevoegen" of "verwijderen" in.
    tijdstip : string.
        Vul "o" of "a" in.
    
    Returns
    -------
    list of lists.

    """
    aantal_personen = len(rooster)-3
    # print("aantal_personen = " + str(aantal_personen))
    
    if kant == "rechts":
        if actie == "toevoegen":
            rooster[0].insert(kolomnummer, datum)
            rooster[1].insert(kolomnummer*2-1, tijdstip)
            for i in range(aantal_personen):
                rooster[i+2].insert(kolomnummer*2-1, 5)
            print(rooster)
            return(rooster)

#------------------------ end function definitions -------------------------
