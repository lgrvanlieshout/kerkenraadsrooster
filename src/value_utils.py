# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 12:05:22 2025

@author: Levi
"""

import numpy as np
from date_utils import services_to_list, is_special_date
from create_xlsx import services_dict, kerkenraad
from schedule import Rules


################################################
# ----------- Vectors for counting ----------- #
################################################

def role_vectors(rules: Rules, persons: dict):
    # Initialize roles
    roles = {}

    # Get a one-hot encoding per role of whether a person has that role
    for role in rules.role_distribution:
        roles[role] = []
        for person in persons.values():
            if person["ambt"] == role:
                roles[role].append(1)
            else:
                roles[role].append(0)

    return roles

def count_persons_vector(n_persons: int):
    return [1 for _ in range(n_persons)]

def morning_pref_vector(services):
    morning_vector = services
    for date, day in services.items():
        if is_special_date(date):
            morning_vector[date] = [0 for _ in day]  # Ignore special dates
        else:
            # Don't count mornings
            morning_vector[date] = [1 if service != 0 else 0 for service in day]

    return services_to_list(morning_vector)

def evening_pref_vector(services):
    evening_vector = services
    for date, day in services.items():
        if is_special_date(date):
            evening_vector[date] = [0 for _ in day]  # Ignore special dates
        else:
            # Don't count evenings
            evening_vector[date] = [1 if service != 1 else 0 for service in day]

    return services_to_list(evening_vector)

def even_week_vector(services):
    even_week_vector = services
    for date, day in services.items():
        week_number = int(date.strftime("%V"))

        if is_special_date(date):
            even_week_vector[date] = [0 for _ in day]  # Ignore special dates
        elif week_number % 2 == 0:
            even_week_vector[date] = [0 for _ in day]  # Don't count even weeks
        elif week_number % 2 == 1:
            even_week_vector[date] = [1 for _ in day]  # Count odd weeks

    return services_to_list(even_week_vector)

def odd_week_vector(services):
    odd_week_vector = services
    for date, day in services.items():
        week_number = int(date.strftime("%V"))

        if is_special_date(date):
            odd_week_vector[date] = [0 for _ in day]  # Ignore special dates
        elif week_number % 2 == 0:
            odd_week_vector[date] = [1 for _ in day]  # Count even weeks
        elif week_number % 2 == 1:
            odd_week_vector[date] = [0 for _ in day]  # Don't count odd weeks

    return services_to_list(odd_week_vector)

def n_present_vector(services):
    n_services = len(services_to_list(services))
    # Count how often someone is present
    return [1 for _ in range(n_services)]


################################################
# ------------ Counting functions ------------ #
################################################

def get_person_stats_counter(rules: Rules, persons: dict) -> np.ndarray:
    n_persons = len(persons)

    # Count how many people are present in a service
    counter_matrix = [count_persons_vector(n_persons)]

    # Count how many of each role are present in a service
    for role_vector in role_vectors(rules, persons).values():
        counter_matrix.append(role_vector)

    return np.array(counter_matrix)

def get_service_stats_counter(services: dict) -> np.ndarray:
    # Count how often everyone is present
    counter_matrix = [n_present_vector(services)]

    # Count how often a preference is denied
    counter_matrix.append(morning_pref_vector(services))
    counter_matrix.append(evening_pref_vector(services))
    counter_matrix.append(even_week_vector(services))
    counter_matrix.append(odd_week_vector(services))

    return np.array(counter_matrix).T

def get_ideal_person_stats(rules: Rules, n_services: int) -> np.ndarray:
    # Initialize ideal person stats with desired number of persons in a service
    ideal_person_stats = [rules.n_persons]

    # Add ideal role distribution
    for role, n_required in rules.role_distribution.items():
        ideal_person_stats.append(n_required)

    # Adjust shape for number of services
    ideal_person_stats = [ideal_person_stats for _ in range(n_services)]
    return np.array(ideal_person_stats).T

def get_ideal_service_stats(persons):
    ideal_service_stats = []
    preferences = ["ochtend", "avond", "om de week"]
    for preference in preferences:
        ideal_service_stats.append([])
        for person in persons.values():
            if person["voorkeur"] == preference:
                ideal_service_stats[-1].append(1)
            else:
                ideal_service_stats[-1].append(0)

    return np.array(ideal_service_stats)


################################################
# -------------- Score function -------------- #
################################################

def get_score(person_stats_counter: np.ndarray, ideal_person_stats: np.ndarray,
          service_stats_counter: np.ndarray, ideal_service_stats: np.ndarray,
          rules: dict, availability: np.ndarray):
    # Check for the difference with the ideal person stats
    person_stats = np.matmul(person_stats_counter, availability)
    print(f"person_stats: {person_stats}")
    difference = person_stats - ideal_person_stats

    # Calculate the resulting score
    score = np.inner(difference, difference)

    # Count how often everyone is present and how often preferences are denied
    service_stats = np.matmul(availability, service_stats_counter).T
    print(f"service_stats: {service_stats}")

    # Compute how much each person differs from the mean number of times present
    avg_presence = np.mean(service_stats[0])
    difference = service_stats[0] - avg_presence
    score += np.inner(difference, difference)

    # Add morning preference to score
    score += np.sum(ideal_service_stats[0] * service_stats[1])

    # Add evening preference to score
    score += np.sum(ideal_service_stats[1] * service_stats[2])


    return score


n_services = len(services_to_list(services_dict))
availability = np.ones((len(kerkenraad), n_services))

person_stats_counter = get_person_stats_counter(Rules(), kerkenraad)
#print(f"person_stats_counter: {person_stats_counter}")
service_stats_counter = get_service_stats_counter(services_dict)
#print(f"service_stats_counter: {service_stats_counter}")
ideal_person_stats = get_ideal_person_stats(Rules(), n_services)
#print(f"ideal_person_stats: {ideal_person_stats}")
ideal_service_stats = get_ideal_service_stats(kerkenraad)
print(f"ideal_service_stats: {ideal_service_stats}")



score = get_score(person_stats_counter, ideal_person_stats,
                  service_stats_counter, ideal_service_stats,
                  Rules(), availability)
