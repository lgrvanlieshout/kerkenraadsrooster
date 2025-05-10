# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 11:38:19 2024

@author: Levi
"""

import numpy as np

#------------------ Member class --------------------
class Member:
    """
    Description : Represents a member of an organisation.
    -----------
    Attributes : name, phone_number, e-mail, role, preference
    -----------
    name : string
    phone_number : string
    email : string
    role : string
    preference : 'none', 'ochtend', 'avond', 'om de week' 
    """
    
    def __init__(self, name, phone_number, email, role, preference):
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.role = role
        self.preference = preference
    
    def __str__(self):
        return str([self.name, self.phone_number, self.email, self.role, self.preference])

"""
class Schedule:
    def __init__(self, members, day_info, cast, congregation_day):
        self.members = members
        self.roles = np.unique(np.array([member.role for member in members]))
        self.day_info = day_info
        self.cast = cast
        self.congregation_day = congregation_day

    def __str__(self):
        member_names = [member.name for member in self.members]
        return str([member_names, self.roles, self.day_info, self.cast, self.congregation_day])
"""

#------------------- rooster class -------------------
class Rooster:
    """
    Description : Represents a schedule for presence/absence.
    -----------
    Attributes : matrix, value, day_info, members, preferences, distr, 
                 show_rate, vect
    -----------
    matrix : numpy matrix with a number of rows equal to the number of members for 
            which the roster is made.
    value : how good a roster is.
    day_info : row vector with a 0, 1 or 2 depending on the day/time slot. 0 for morning, 
                1 for evening and 2 for special day.
    members : list consisting of objects of the class 'member'
    preferences : list containing the preference for each member
    distr : preferred role distribution. list containing how many persons in a 
            specific role must be present in an event 
            (in dit geval hoeveel kerkenraadsleden er bij een dienst aanwezig 
             moeten zijn, dus bijv [3,1,2].)
    show_rate : number indicating the soft upper limit on the maximal number of 
                times people have to show up. 
    vect : list of vectors needed for value computation
    
    """
    
    def __init__(self, matrix, day_info, members, distr, show_rate=0, vect={}):
        self.matrix = matrix
        #self. value = f(matrix)
        self.day_info = day_info
        self.members = members
        
        # create a list with all preferences
        preferences = []
        for member in members:
            preferences.append(member.preference)
        self.preferences = preferences
        self.distr = distr
        self.vect = vect
        if show_rate == 0:
            self.show_rate = int(len(day_info)/2)
        else: self.show_rate = show_rate
    
    
    def __str__(self):
        return str(self.matrix)
    
    def get_vect(self):
        # Check if all things are as supposed
        m, n = np.shape(self.matrix)
        
        # For each new role encountered in the 'member' information, add it to roles.
        roles = []
        for member in self.members:
            if member.role not in roles:
                roles.append(member.role)
        
        # Set up a list that contains all the vectors that will count how many 
        # members with the same role are present.
        role_vectors = []
        for role in roles:
            role_vector = np.zeros(m, int)
            for i in range(len(self.members)):
                if self.members[i].role == role:
                    role_vector[i] = 1
            role_vectors.append(role_vector)
        # Add role vectors to self.vect
        self.vect["role_vectors"] = role_vectors
        
        
        # Set up a list that contains all the vectors that will count how often 
        # a preference is not met. 
        preference_vectors = []
        
        # Vectors for morning and evening
        for i in range(2):
            vec = np.ones(n, int)
            for j in range(n):
                if self.day_info[j] == i:
                    vec[j] = 0
            preference_vectors.append(vec)
            
        # Vectors for every other week
        vec0 = np.zeros(n, int)
        count0, count1 = 0, 0
        for i in range(n):
            if self.day_info[i] == 0:
                if count0 == 0:
                    vec0[i] = 1
                count0 = (count0 + 1) % 2
            elif self.day_info[i] == 1:
                if count1 == 0:
                    vec0[i] = 1
                count1 = (count1 + 1) % 2
        preference_vectors.append(vec0)

        vec1 = np.zeros(n, int)
        count0, count1 = 0, 0
        for i in range(n):
            if self.day_info[i] == 0:
                if count0 == 1:
                    vec1[i] = 1
                count0 = (count0 + 1) % 2
            elif self.day_info[i] == 1:
                if count1 == 1:
                    vec1[i] = 1
                count1 = (count1 + 1) % 2
        preference_vectors.append(vec1)
        
        self.vect["preference_vectors"] = preference_vectors
        return self.vect
    
    def value(self, parameters=[1,2,1,1,2]):
        """
        Dit is de objectieve functie die we willen minimaliseren. Hoe kleiner de uitkomst
        van deze functie, hoe beter het rooster is. This is the objective function we want to minimalize.
        The smaller the result of this function, the better the schedule is.

        Parameters
        ----------
        self : Rooster object
        parameters : list of parameters

        Returns
        -------
        Float.

        """        
        
        # check if all things are as supposed
        m,n = np.shape(self.matrix)
        if m != len(self.members) or n != len(self.day_info):
            print("The size of the matrix doesn't match the number of members or the number of days.")
            return False
        
        
        #--------- MEASURING NUMBER OF PARTICIPANTS PER ROLE PRESENT ---------
        
        # for each new role encountered in the 'member' information, add it to roles.
        roles = []
        for member in self.members:
            if member.role not in roles:
                roles.append(member.role)
        
        # set up a list whose elements will be added in the end to give the value of the roster
        summands = []
        
        role_vectors = self.vect["role_vectors"]
        
        for i in range(len(roles)):
            # vector stating how far the present number of participants in a certain
            # role differs from the desired number of participants of that role (squared)
            difference = role_vectors[i]@self.matrix-self.distr[i]
            summands.append(parameters[0]*int(difference@difference.T))
        
        
        
        #----------- MEASURING TOTAL PARTICIPANTS PER SERVICE/MEETING ----------
        
        difference = np.ones(m,int)@self.matrix-sum(self.distr)*np.ones(n,int)
        summands.append(parameters[1]*int(difference@difference.T))
        
        
        
        #----------- MEASURING HOW OFTEN PEOPLE HAVE TO SHOW UP (OBJECTIVELY) ----------
        
        # more or less measures how much more you had to show up than the show rate. Not sure
        # whether this is the right way to measure this.
        difference = self.matrix @ np.ones((n,1),int)-self.show_rate*np.ones((m,1),int)
        for i in range(m):
            if difference[i][0]<=-1:
                difference[i][0]=-0.2
        summands.append(parameters[2]*int((difference.T@difference)[0][0]))
        
        
        
        #----------- MEASURING HOW OFTEN PEOPLE HAVE TO SHOW UP (RELATIVELY) ----------
        
        presence = self.matrix @ np.ones((n,1),int)
        # turns the presence-vector in the right format
        presence = presence.T[0]
        mean = sum(presence)/n
        
        difference = self.matrix @ np.ones((n,1),int)-mean*np.ones((m,1),int)
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
        
        return sum(summands)