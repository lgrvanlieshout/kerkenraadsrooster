# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 11:37:05 2024

@author: Levi
"""

import numpy as np
from classes import Member


"""
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

day_info = [["zondag 1", "morning", "evening"],
            ["2e Paasdag", "morning"],
            ["3e Paasdag", "evening"],
            ["zondag 2", "morning", "evening"],
            ["zondag 3", "morning", "evening"],
            ["zondag 4", "morning", "evening"],
            ["zondag 5", "morning", "evening"],
            ["zondag 6", "morning", "evening"],
            ["zondag 7", "morning", "evening"],
            ["zondag 8", "morning", "evening"]]

cast = [4, 1, 2]

congregation_day = "zondag"


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
#day_info = [0,1,0,1,0,1,0,1,0,1,2,0,1,0,1,2,0,1,0,1,0,1,0,1,0,1,0,1,2,0,1]