# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 15:02:08 2024

@author: Levi
"""

import numpy as np

############ ---------------------------------------------------- ############
#                Functions for generating the initial schedule
############ ---------------------------------------------------- ############

def gen_ideal_presences(day_info, congregation_day = "sunday"):
    """
    Generate the ideal presence given some info on the dates and
     times services are held and do this for all preferences.

    Parameters
    ----------
    day_info : list[list["day i", "morning", "evening", ...]]
        List containing information about the dates, times and kinds of services.
    congregation_day : string, optional
        Day on which usually services are held. The default is "sunday".

    Returns
    -------
    ideal_presences : dict[list]
        Dictionary of lists that give the ideal presence given a preference.

    """    
    # Count the number of services
    n_services = 0
    for day in day_info:
        n_services += (len(day) - 1)
    
    # Initialise a dict for storing the ideal presences
    ideal_presences = {}
    
    
    # ---------- Construct presence for "morning" and "evening" ----------
    
    ideal_presence_morning = []
    ideal_presence_evening = []
    
    # For each day, check whether it's the usual day on which services are held
    for day in day_info:
        if congregation_day in day[0]:
            for service in day[1:]:
                ideal_presence_morning.append(1 if service == "morning" else 0)
                ideal_presence_evening.append(1 if service == "evening" else 0)
        else:
            # Mark absent for each service
            for _ in day[1:]:
                ideal_presence_morning.append(0)
                ideal_presence_evening.append(0)
    
    ideal_presences["morning"] = ideal_presence_morning
    ideal_presences["evening"] = ideal_presence_evening
    
    
    # ---------- Same for "every odd week" and "every even week" -----------
    
    ideal_presence_odd = []
    ideal_presence_even = []
    
    # For each day, check whether it's the usual day on which services are held
    for day in day_info:
        if congregation_day in day[0]:
            
            # Determine if week is even or odd
            parity = int(day[0][-1]) % 2
            
            # For each service this day, mark presence/absence based on odd/even week
            for _ in day[1: ]:
                ideal_presence_odd.append(parity)
                ideal_presence_even.append(1-parity)
        
        else:
            # Mark absent for each service
            for _ in day[1: ]:
                ideal_presence_odd.append(0)
                ideal_presence_even.append(0)
    
    ideal_presences["every odd week"] = ideal_presence_odd
    ideal_presences["every even week"] = ideal_presence_even

    # Return the resulting preferences
    return ideal_presences


def gen_schedule_pref(preferences, ideal_presences):
    """
    Generate a matrix where each member is only present at the preferred date
    and time.

    Parameters
    ----------
    preferences : List
        List containing the preference for each member. The entry "None" is not
        allowed to be in this list.
    ideal_presences : Dict
        Dict of lists containing the ideal presences given a preference.

    Returns
    -------
    schedule : np matrix
        Matrix with zeros and ones representing presence and absence according
        to the preferences.

    """
    # Initialise schedule
    schedule = []
    
    # adding ones to the matrix when someone wants to be present according to
    # his/her preference
    for preference in preferences:
        schedule.append(ideal_presences[preference])

    print(np.array(schedule))
    return np.array(schedule)



############ ---------------------------------------------------- ############
#                                  Test space
############ ---------------------------------------------------- ############

if __name__ == "__main__":
    
    day_info = [["zondag 1", "morning", "evening"],
                ["zondag 2", "morning", "evening"],
                ["special day", "flup"],
                ["zondag 3", "morning", "evening"],
                ["zondag 4", "morning", "evening"],
                ["zondag 5", "morning", "evening"],
                ["zondag 6", "morning", "evening"]]
    
    preferences = ["morning", "evening", "every odd week", "every even week"]
    
    ideal_presences = gen_ideal_presences(day_info, "zondag")
    gen_schedule_pref(preferences, ideal_presences)