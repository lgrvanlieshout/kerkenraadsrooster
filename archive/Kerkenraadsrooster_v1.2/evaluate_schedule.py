# -*- coding: utf-8 -*-
"""
Function for determining the value of a schedule
"""

import numpy as np
from data import members, day_info, cast, congregation_day
from utils import gen_ideal_presences

def get_params(members, day_info, cast, congregation_day):
    # Create some useful variables
    roles = np.unique(np.array([member.role for member in members]))
    n_members = len(members)
    n_services = sum([(len(day)-1) for day in day_info])
    vectors = {}
    
    # Set up a list that contains all the vectors that will count how many 
    # members with the same role are present.
    role_vectors = []
    for role in roles:
        role_vector = np.zeros(n_members, int)
        for i, member in enumerate(members):
            if member.role == role:
                role_vector[i] = 1
        role_vectors.append(role_vector)
    # Add role vectors to self.vect
    vectors["role"] = role_vectors
    
    
    # Set up a list that contains all the vectors that will count how often 
    # a preference is not met. 
    pref_vects = {}
    
    # Get ideal presences. 
    ideal_presences = gen_ideal_presences(day_info, congregation_day)
    
    # Invert the ideal presence vectors and leave out the special days, so we 
    # get the vectors we are looking for.
    for key in ideal_presences:
        # Invert presence and absence in ideal presence
        vect = np.ones(n_services, int)-ideal_presences[key]
        
        # ------ Change to 0 on special services -------
        n_passed_services = 0
        for day in day_info:
            # Detect whether it is a special day
            if congregation_day not in day[0]:
                vect[n_passed_services : n_passed_services + len(day) - 1] = 0
            n_passed_services += len(day) - 1
        # Add vect to pref_vects
        pref_vects[key] = vect
    
    vectors["preference"] = pref_vects
    
    
    return members, roles, day_info, cast, congregation_day, vectors


def value(matrix, 
          members, 
          roles, 
          day_info, 
          cast, 
          congregation_day, 
          vectors, 
          parameters=[1,2,1,1,2]):
    """
    Dit is de objectieve functie die we willen minimaliseren. Hoe kleiner de uitkomst
    van deze functie, hoe beter het rooster is. This is the objective function we want to minimalize.
    The smaller the result of this function, the better the schedule is.

    Parameters
    ----------
    matrix : numpy array consisting of zeros and ones.
    vectors : dict of dicts
    parameters : list of parameters

    Returns
    -------
    Float.

    """
    
    
    
    
    
    #--------- MEASURING NUMBER OF PARTICIPANTS PER ROLE PRESENT ---------
    
    # set up a list whose elements will be added in the end to give the value of the roster
    summands = []
    
    role_vectors = vectors["role"]
    
    for i in range(len(roles)):
        # vector stating how much the present number of participants in a certain
        # role differs from the desired number of participants of that role (squared)
        difference = (role_vectors[i] @ matrix) - cast[i]
        summands.append(parameters[0]*np.squared(difference))
    
    print(summands)
    """
    #----------- MEASURING TOTAL PARTICIPANTS PER SERVICE/MEETING ----------
    
    difference = np.ones(m,int)@self.matrix-sum(self.distr)*np.ones(n,int)
    summands.append(parameters[1]*int(difference@difference.T))
    
    
    
    #----------- MEASURING HOW OFTEN PEOPLE HAVE TO SHOW UP (OBJECTIVELY) ----------
    
    # more or less measures how much more you had to show up than the show rate. Not sure
    # whether this is the right way to measure this.
    difference = matrix @ np.ones((n,1),int)-self.show_rate*np.ones((m,1),int)
    for i in range(m):
        if difference[i][0]<=-1:
            difference[i][0]=-0.2
    summands.append(parameters[2]*int((difference.T@difference)[0][0]))
    
    
    
    #----------- MEASURING HOW OFTEN PEOPLE HAVE TO SHOW UP (RELATIVELY) ----------
    
    presence = matrix @ np.ones((n,1),int)
    # turns the presence-vector in the right format
    presence = presence.T[0]
    mean = sum(presence)/n
    
    difference = matrix @ np.ones((n,1),int)-mean*np.ones((m,1),int)
    difference = difference.T[0]
    
    for i in range(m):
        difference[i] = abs(difference[i])
    summands.append(parameters[3]*sum(difference))
    
    
    
    #---------- MEASURING HOW WELL PREFERENCES ARE MET ----------
    
    preference_vectors = self.vect["preference_vectors"]
    
    # actually computing how often/good preferences are met
    value = 0
    # print((self.matrix@preference_vectors[0])[1])
    for i in range(m):
        if self.members[i].preference == "ochtend":
            value += (self.matrix@preference_vectors[0])[i]
        elif self.members[i].preference == "avond":
            value += (self.matrix@preference_vectors[1])[i]
        elif self.members[i].preference == "om de week 1":
            value += (self.matrix@preference_vectors[2])[i]
        elif self.members[i].preference == "om de week 2":
            value += (self.matrix@preference_vectors[3])[i]
    summands.append(parameters[4]*value)
    """
    return sum(summands)
    

get_params(members, day_info, cast, congregation_day)
n_services = sum([(len(day)-1) for day in day_info])
n_members = len(members)
matrix = np.ones((n_members, n_services), int)
value(matrix, get_params(members, day_info, cast, congregation_day))