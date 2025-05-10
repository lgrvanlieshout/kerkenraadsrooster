# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 09:42:31 2022

@author: lgrle
"""

#--------------- importing stuff ------------------
import datetime
import time
import numpy as np
import itertools
import random
import copy



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
        return str([self.name,self.phone_number, self.email, self.role, self.preference])
    
    
    
    
#--------------------- Organisation class -----------------------
class Organisation:
    """
    Description: Represents an organisation.
    -----------
    Attributes : members, roles, size, size_per_role, preferences, desired_participants
    -----------
    members : list consisting of objects of the class 'member'
    roles : list consisting of the roles of members
    size : number of members
    size_per_role : list containing the number of members with the same role for each role
    preferences : list  containing the preference for each member
    desired : ordered list stating how many persons in a specific role must 
                be present in an event 
                (in dit geval hoeveel kerkenraadsleden er bij een dienst aanwezig 
                 moeten zijn, dus bijv [3,1,2].)
    """
    
    def __init__(self, members, desired):
        self.members = members
        
        # for each new role encountered in the 'member' information, add it to roles.
        roles = []
        for member in members:
            if member.role not in roles:
                roles.append(member.role)
        self.roles = roles
        self.size = len(members)
        
        # for each role count how many people there are with that role.
        size_per_role = []
        for role in roles:
            count = 0
            for member in members:
                if member.role == role:
                    count+=1
            size_per_role.append(count)
        self.size_per_role = size_per_role
        
        # create a list with all preferences
        preferences = []
        for member in members:
            preferences.append(member.preference)
        self.preferences = preferences
        self.desired = desired
        
        
    def __str__(self):
        namen = []
        for member in self.members:
            namen.append(member.name)
        return str(namen)





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


# ------------------- end class initialisations -----------------------


"""
chuisman = Member('C. Huisman', '06-25055447', 'huisman@ziggo.nl', 'ouderling', 
                  'om de week')
kdorresteijn = Member('K. Dorresteijn', '06-22555003', 'keesdorresteijn@outlook.com',
                       'ouderling', 'none')
gjverburg = Member('G.J. Verburg', '06-10059937', 'gjverburg@outlook.com', 'ouderling', 
                   'ochtend')
cverweij = Member('C. Verweij', '06-13882025', 'corverweij@kpnmail.nl', 'ouderling', 
                  'ochtend')
hbudding = Member('H. Budding', '0348-452158', 'henk.budding@hetnet.nl', 'ouderling',
                  'none')
pmolenaar = Member('P. Molenaar', '06-54640383', 'piet-regina@hotmail.nl', 'ouderling',
                   'om de week')
pvandenbroek = Member('P. van den Broek', '06-19456958', 'vdbroek@live.nl', 'ouderling',
                      'none')
ddejong = Member('D. de Jong', '06-51052856', 'info@bouwbedrijfdejonglopik.nl', 
                 'ouderling-kerkrentmeester', 'avond')
nschep = Member('M. Schep', '06-20392712', 'n.schep@outlook.com', 
                'ouderling-kerkrentmeester', 'ochtend')
abuitenhuis = Member('A. Buitenhuis', '06-11820506', 'aronbuitenhuis@gmail.com',
                     'ouderling-kerkrentmeester', 'ochtend')
mcooiman = Member('M. Cooiman', '0348-551602', 'fam-cooiman@hotmail.com', 'diaken',
                  'om de week')
fvanoort = Member('F. van Oort', '0348-554336', 'famfoort@kliksafe.nl', 'diaken', 
                  'none')
mvisser = Member('M. Visser', '06-23372557', 'martijnvisser76@hotmail.com', 'diaken',
                  'none')
gdevor = Member('G. de Vor', '06-36436022', 'gerritdevor@outlook.com', 'diaken',
                'ochtend')

members = [chuisman, kdorresteijn, gjverburg, cverweij, hbudding, pmolenaar, 
           pvandenbroek, ddejong, nschep, abuitenhuis, mcooiman, fvanoort, mvisser, gdevor]

matrix = np.reshape([[1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
                     [1,0,1,0,1,1,1,0,1,0,0,0,0,0,0,0],
                     [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],(14,16))

absence_matrix = np.reshape([[1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1],
                     [1,1,0,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,0,0,1,1,1,1,0,1,1,1,1,1,1,0],
                     [1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                     [1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,1,1,1,0,1,1,1,1,1,1,1,1],
                     [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
                     [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                     [1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,1,1,1,1,1],
                     [1,1,0,1,1,1,0,0,1,1,0,0,1,0,0,0,1,1,1,1,1,1,1,1,1,0,1,0,1,0,0,0,1,1,1,1],
                     [1,1,0,0,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1],
                     [1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1],
                     [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,1,1,1,1],
                     [1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1],
                     [0,1,1,1,1,0,1,0,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,0,1,0,1,0,1,1,0,1,1,1,0,1],
                     [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],(14,36))


day_info = np.array([0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1])
rooster = Rooster(matrix, day_info, members, [3,1,2])

#print(rooster.matrix)
#rooster.value()
"""
chuisman = Member('C. Huisman', '06-25055447', 'huisman@ziggo.nl', 'ouderling', 
                  'om de week 2')
kdorresteijn = Member('K. Dorresteijn', '06-22555003', 'keesdorresteijn@outlook.com',
                       'ouderling', 'none')
gjverburg = Member('G.J. Verburg', '06-10059937', 'gjverburg@outlook.com', 'ouderling', 
                   'ochtend')
pvandenbroek = Member('P. van den Broek', '06-19456958', 'vdbroek@live.nl', 'ouderling',
                      'none')
ddejong = Member('D. de Jong', '06-51052856', 'info@bouwbedrijfdejonglopik.nl', 
                 'ouderling-kerkrentmeester', 'avond')
nschep = Member('M. Schep', '06-20392712', 'n.schep@outlook.com', 
                'ouderling-kerkrentmeester', 'ochtend')
abuitenhuis = Member('A. Buitenhuis', '06-11820506', 'aronbuitenhuis@gmail.com',
                     'ouderling-kerkrentmeester', 'ochtend')
hdegroot = Member('H. de Groot', '06-12102581', 'de.groot.hans@hotmail.com', 'diaken',
                  'om de week')
kgoedhart = Member('K. Goedhart', '06-51082473', 'famgoedhart@ziggo.com', 'diaken',
                'ochtend')
mvisser = Member('M. Visser', '06-23372557', 'martijnvisser76@hotmail.com', 'diaken',
                  'none')
gdevor = Member('G. de Vor', '06-36436022', 'gerritdevor@outlook.com', 'diaken',
                'ochtend')

members = [chuisman, kdorresteijn, gjverburg, pvandenbroek, ddejong, nschep,
           abuitenhuis, hdegroot, kgoedhart, mvisser, gdevor]

absence_matrix = np.reshape([[1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1],
                             [1,0,1,1,1,1,0,1,2,2,1,1,1,1,1,1,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0],
                             [0,0,1,1,1,1,1,1,2,2,1,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,0,0,0,1,1],
                             [1,1,1,1,1,1,1,1,2,2,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                             [1,1,0,0,0,1,1,1,2,2,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1,1],
                             [1,1,0,0,1,1,1,1,2,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,0,1,1],
                             [1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
                             [1,1,1,1,1,1,1,1,2,2,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
                             [1,0,1,1,1,1,0,0,0,0,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
                             [0,1,1,1,0,1,1,1,2,2,0,1,1,0,1,0,0,1,1,1,1,1,0,1,1,0,1,0,1,1,0],
                             [1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],(11,31))
day_info = [0,1,0,1,0,1,0,1,0,1,2,0,1,0,1,2,0,1,0,1,0,1,0,1,0,1,0,1,2,0,1]


# ------------------ begin function definitions -----------------------


def time_it(f, list_of_args):
    start = time.perf_counter()
    f(*list_of_args)
    print(time.perf_counter()-start)


def gen_schedule_pref(day_info, preferences):
    """
    Generates a matrix where each member is only present at the preferred date
    and time.

    Parameters
    ----------
    day_info : List
        Row vector with a 0, 1 or 2 depending on the day/time slot. 0 for
        morning, 1 for evening and 2 for special day.
    preferences : Tuple
        list containing the preference for each member. The entry "None" is not
        allowed to be in this list.

    Returns
    -------
    schedule : np matrix
        Matrix with zeros and ones representing presence and absence according
        to the preferences.

    """
    
    # initialisations
    m, n = len(preferences), len(day_info)
    schedule = np.zeros((m, n), int)
    
    # adding ones to the matrix when someone wants to be present according to
    # his/her preference
    for i in range(m):
        if preferences[i] == "ochtend":
            for j in range(n):
                if day_info[j] == 0:
                    schedule[i][j] = 1
        elif preferences[i] == "avond":
            for j in range(n):
                if day_info[j] == 1:
                    schedule[i][j] = 1
        elif preferences[i] == "om de week 1":
            count0, count1 = 0, 0
            for j in range(n):
                if day_info[j] == 0:
                    if count0 == 0:
                        schedule[i][j] = 1
                    count0 = (count0 + 1) % 2
                elif day_info[j] == 1:
                    if count1 == 0:
                        schedule[i][j] = 1
                    count1 = (count1 + 1) % 2
        elif preferences[i] == "om de week 2":
            count0, count1 = 0, 0
            for j in range(n):
                if day_info[j] == 0:
                    if count0 == 1:
                        schedule[i][j] = 1
                    count0 = (count0 + 1) % 2
                elif day_info[j] == 1:
                    if count1 == 1:
                        schedule[i][j] = 1
                    count1 = (count1 + 1) % 2
    return schedule



def gen_init_schedule(day_info, members, distr, absence_mat, show_rate=0):
    """
    Generates the best initial schedule based on preferences and absence.

    Parameters
    ----------
    day_info : list
        Row vector with a 0, 1 or 2 depending on the day/time slot. 0 for morning, 
        1 for evening and 2 for special day.
    members : list
        list consisting of objects of the class 'member'.
    distr : list
        preferred role distribution. list containing how many persons in a 
                specific role must be present in an event 
                (in dit geval hoeveel kerkenraadsleden er bij een dienst aanwezig 
                 moeten zijn, dus bijv [3,1,2].)
    absence_mat : Numpy matrix
        Matrix giving the absence and presence. Zeros meaning absence and two's meaning presence.
    show_rate : int, optional
        number indicating the soft upper limit on the maximal number of 
                    times people have to show up. The default is 0.

    Returns
    -------
    Object of the class Rooster
        Returns the best initial schedule based on preferences and absence.

    """
    
    # initialisations
    preferences = []
    for member in members:
        preferences.append(member.preference)
    
    # preparing a list of options over which will be iterated
    pref_options = []
    for pref in preferences:
        if pref == "ochtend":
            pref_options.append(["ochtend"])
        elif pref == "avond":
            pref_options.append(["avond"])
        elif pref == "om de week 1":
            pref_options.append(["om de week 1"])
        elif pref == "om de week 2":
            pref_options.append(["om de week 2"])
        elif pref == "om de week":
            pref_options.append(["om de week 1", "om de week 2"])
        elif pref == "none":
            pref_options.append(["ochtend", "avond", "om de week 1", "om de week 2"])
    
    # all possible preference permutations
    pref_perms = list(itertools.product(*pref_options))
    
    # list indices of presence
    list_of_presence = []
    for i in range(len(members)):
        for j in range(len(day_info)):
            if absence_matrix[i][j] == 2:
                list_of_presence.append((i,j))
    
    # init list of schedules
    poss_schedules = []
    first_mat = np.multiply(absence_mat, gen_schedule_pref(day_info, pref_perms[0]))
    for i in list_of_presence:
        first_mat[i] = 1
    first_schedule = Rooster(first_mat, day_info, members, distr, 0)
    first_schedule.preferences = pref_perms[0]
    first_schedule.get_vect()
    poss_schedules.append(first_schedule)
    
    for prefs in pref_perms:
        mat = np.multiply(absence_mat, gen_schedule_pref(day_info, prefs))
        for i in list_of_presence:
            mat[i] = 1
        schedule = Rooster(mat, day_info, members, distr, 0)
        schedule.preferences = prefs
        schedule.get_vect()
        if schedule.value() < poss_schedules[-1].value():
            poss_schedules.append(schedule)
            #print(prefs)
        
    return poss_schedules[-1]


#a = gen_init_schedule(day_info, members, [3,1,2], absence_matrix, 0)
#time_it(gen_init_schedule, [day_info, members, [3,1,2], absence_matrix, 0])
#print(a, a.value())
    


def gen_perms(absence_matrix, perm_selection):
    
    # setup
    mat = absence_matrix
    m,n = absence_matrix.shape
    mat_str = np.reshape(mat, -1)
    k = len(mat_str)
    perms = []
    
    # construct a list that translates a number to matrix coordinates
    coordinate = []
    for i in range(k):
        coordinate.append(divmod(i, n))

    # storing the indices at which people have said being absent or present.
    fixed = []
    for i in range(k):
        if mat_str[i] == 0 or mat_str[i] == 2:
            fixed.append(i)
    #print("fixed = "+ str(fixed))
    
    # adding all single switches
    if 1 in perm_selection:
        for i in range(k):
            if i not in fixed:
                combo = [coordinate[i]]
                perms.append(combo)
                
    # adding all double switches
    if 2 in perm_selection:
        for combo in itertools.combinations(range(k), 2):
            if set(combo).isdisjoint(set(fixed)):
                combo = tuple([coordinate[combo[j]] for j in range(len(combo))])
                perms.append(combo)
    
    # adding all double switches in a single row or column
    if 2.1 in perm_selection:
        for i in range(m):
            for combo in itertools.combinations(range(n), 2):
                combo = tuple([combo[j] + n*i for j in range(len(combo))])
                if set(combo).isdisjoint(set(fixed)):
                    combo = tuple([coordinate[combo[j]] for j in range(len(combo))])
                    perms.append(combo)
        for i in range(n):
            for combo in itertools.combinations(range(m), 2):
                combo = tuple([combo[j]*n+i for j in range(len(combo))])
                if set(combo).isdisjoint(set(fixed)):
                    combo = tuple([coordinate[combo[j]] for j in range(len(combo))])
                    perms.append(combo)
    
    # adding all quadrupel switches 'occurring in a rectangle'
    if 4 in perm_selection:
        for i in range(m-1):
            for j in range(1,m-i):
                for combo in itertools.combinations(range(n),2):
                    combo = tuple([combo[l] + n*i for l in range(len(combo))])
                    combo = (combo[0], combo[1], combo[0]+n*j, combo[1]+n*j)
                    if set(combo).isdisjoint(set(fixed)):
                        combo = tuple([coordinate[combo[l]] for l in range(len(combo))])
                        perms.append(combo)
    
    print("number of permutations = " + str(len(perms)))
    return perms




def optimize_schedule(schedule, absence_matrix, perm_sets):
    
    # initialisations
    day_info = schedule.day_info
    members, distr, show_rate = schedule.members, schedule.distr, schedule.show_rate
    t_start = time.perf_counter()
    perms = gen_perms(absence_matrix, perm_sets)
    print("computing terms time = " + str(time.perf_counter()-t_start))
    schedule_iters = [(schedule, schedule.value())]
    schedules = [(schedule, schedule.value())]
    print(schedule_iters[-1][1])
    count = 0
    
    # start iterating, stop when results hardly get better
    while count == 0 or schedule_iters[-2][1]-schedule_iters[-1][1]>1:
        count+=1
        t_start = time.perf_counter()
        print(count)
        # start creating variations of schedules and calculate their value
        random.shuffle(perms)
        for perm in perms:
            mat = copy.deepcopy(schedule_iters[-1][0].matrix)
            for index in perm:
                mat[index[0]][index[1]] = 1 - mat[index[0]][index[1]]
            sched_perm = Rooster(mat, day_info, members, distr, show_rate)
            value = sched_perm.value()
            # only save the schedule if it is better than the previous ones
            if value < schedules[-1][1]:
                schedules.append((sched_perm, value))
                
        schedule_iters.append(schedules[-1])
        print("duration cycle = " + str(time.perf_counter()-t_start))
        print(schedule_iters[-1][1])
    
    print(str(schedule_iters[-1][0]))
    return schedule_iters[-1][0]



def get_schedule(absence_matrix, day_info, members, distr, show_rate=0):
    t_start = time.perf_counter()
    a = gen_init_schedule(day_info, members, distr, absence_matrix, show_rate)
    t_diff = time.perf_counter()-t_start
    print('duration generating initial schedule = '+str(t_diff))
    #idee: doe eerst alleen 1 tot het verschil <2 is, en dan ook nog 4.
    return optimize_schedule(a, absence_matrix, [1,2.1,4])

get_schedule(absence_matrix, day_info, members, [3,1,2], 0)

# ------------------------- OLD -----------------------------

def np_to_array(matrix):
    return np.reshape(matrix, -1)

def array_to_np(array_1, rows, columns):
    return np.reshape(array_1, (rows,columns))


def genereer_roosters(nprooster, npafwezigheidsrooster):
    """
    

    Parameters
    ----------
    nprooster : numpy 2-dimensional array containing only 0's and 1's.
        DESCRIPTION.
    npafwezigheidsrooster : numpy 2-dimensional array containing only 0's and -1's.
        DESCRIPTION.

    Returns
    -------
    alle_roosters : TYPE
        DESCRIPTION.

    """
    ak, aantal_diensten = np.shape(nprooster)
    afwezigheidsrooster = np.reshape(npafwezigheidsrooster,-1)
    rooster = np.reshape(nprooster, -1)
    
    n= ak*aantal_diensten+sum(afwezigheidsrooster)
    alle_roosters = []
    
    for k in range(2):
        for combination in itertools.combinations(range(n), k):
            for i in combination:
                rooster[i] = 1-rooster[i]
            for j in range(ak*aantal_diensten):
                if afwezigheidsrooster[j]==-1:
                    np.insert(rooster, j, 0)
            alle_roosters.append(np.reshape(rooster, (ak,aantal_diensten)))
            if len(alle_roosters)%1000==0:
                print(len(alle_roosters)//(1000))
    return alle_roosters


"""
def convergentie_rooster(nprooster, npafwezigheidsrooster, c_oud):
    lijst = []
    roosters = genereer_roosters(nprooster, npafwezigheidsrooster)
    for rooster in roosters:
        lijst.append(f(rooster, voorkeur, gakpd, kerkenraadsleden, c=c_oud, parameters = [1,1,0],
                   aantal_zondagen=14))
    temp = min(lijst)
    print("lijst = "+str(lijst))
    res = [i for i, j in enumerate(lijst) if j == temp]
    minimale_roosters = [lijst[i] for i in res]
    print(minimale_roosters[0])
    return minimale_roosters
    


    
voorkeur=["om de week", "geen", "geen","geen", "geen", "geen", "geen","geen", "geen", 
            "geen", "geen","geen", "geen", "geen"]
gewenste_aantal_kerkenraadsleden_per_dienst=[3,1,2]
gakpd = gewenste_aantal_kerkenraadsleden_per_dienst
kerkenraadsleden = [7,2,4]
aantal_zondagen=14
    
#f(np.ones((14, 4),int), voorkeur, gewenste_aantal_kerkenraadsleden_per_dienst=[3,1,2],
#  kerkenraadsleden = [7,3,4], aantal_zondagen=2)

npafwrooster = -1*np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                           [1,1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
                           [0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,1],
                           [0,0,0,0,0,0,0,0,1,1,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,1],
                           [1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1],
                           [1,0,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                           [1,0,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                           [0,0,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1],
                           [1,1,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
                           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                           [1,1,0,0,1,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
                           [0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0]])
nprooster = np.ones((13,28))+npafwrooster

bovengrenzen=[f(nprooster, voorkeur, gakpd, kerkenraadsleden,c=10000, parameters = [1,1,0],
               aantal_zondagen=14)]
iteratie = 0
bovengrenzen.append(bovengrenzen[0])

while (bovengrenzen[-1]<bovengrenzen[-2]) or iteratie == 0:
    nieuw_nprooster = convergentie_rooster(nprooster, npafwrooster, bovengrenzen[-1])
    print(nieuw_nprooster)
    bovengrenzen.append(f(nieuw_nprooster, voorkeur, gakpd, kerkenraadsleden, c=10000, 
                          parameters=[1,1,0], aantal_zondagen=17)) 
    iteratie+=1
    
print("rooster, f(rooster) = " + str(nieuw_nprooster, bovengrenzen[-1]))

"""



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


#---------------------------- begin main file ------------------------------

"""
rooster = create_grid(["Huisman","Dorrestein","Verburg","Verweij", "Budding"], 
                      "28-05-2002", "18-06-2002")
adjust_grid_column(2, "17-08-2016", rooster)

#print(np.__version__)
"""