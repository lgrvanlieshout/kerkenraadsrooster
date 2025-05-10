# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 09:42:31 2022

@author: Levi van Lieshout
"""

#--------------- importing stuff ------------------
import time
import numpy as np
import itertools
import random
import copy

#from classes import Rooster
#from data import members, absence_matrix


# ------------------ begin function definitions -----------------------


def time_it(f, *args):
    start = time.perf_counter()
    f(*args)
    print(time.perf_counter()-start)


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

#get_schedule(absence_matrix, day_info, members, [3,1,2], 0)