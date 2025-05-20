# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 19:14:07 2024

@author: Levi
"""

from datetime import datetime, timedelta
import itertools

def services_to_list(services) -> list:
    """
    Converts the dictionary containing the services for each date to a
    list of services, essentially comprehensing all the values from the
    dictionary into a single list.

    Args:
        services (Services): dictionary containing the services per date.
    """
    return list(itertools.chain.from_iterable(services.values()))

def date_biddag(year: int) -> datetime:
    """
    Returns the date of biddag (first Wednesday of November) for a given year.

    Args:
        year (int): The year for which to find the date of biddag.

    Returns:
        date (datetime): The date of biddag for the given year.

    """
    # Start with the first day of March
    date = datetime(year, 3, 1)

    # Find the first Wednesday on or after the first of March
    while date.weekday() != 2:  # 2 represents Wednesday
        date += timedelta(days=1)

    # The second Wednesday is one week later
    date += timedelta(weeks=1)

    # Return the date of the second Wednesday of March
    return date

def date_dankdag(year: int) -> datetime:
    """
    Returns the date of dankdag (first Wednesday of November) for a given year.

    Args:
        year (int): The year for which to find the date of dankdag.

    Returns:
        date (datetime): The date of dankdag for the given year.

    """
    # Start with the first day of November
    date = datetime(year, 11, 1)

    # Find the first Wednesday on or after the first of November
    while date.weekday() != 2:  # 2 represents Wednesday
        date += timedelta(days=1)

    # Return the date of the first Wednesday of November
    return date

def date_1e_paasdag(year: int) -> datetime:
    """
    Returns the date of Easter Sunday for a given year using the Computus
    (Gauss's) algorithm.
    The function calculates Easter based on the first Sunday after the first
    full moon occurring on or after the vernal equinox (March 21).

    Args:
        year (int): The year for which to calculate the date of Easter Sunday.

    Returns:
        date (datetime): The date of Easter Sunday for the given year.
    
    """

    # Step 1: Calculate the "Golden Number" (a 19-year cycle for the Moon's phases)
    a = year % 19

    # Step 2: Calculate the century
    b = year // 100
    c = year % 100

    # Step 3: Calculate the "epact" (age of the Moon)
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30

    # Step 4: Calculate the "dominion" (a correction factor)
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7

    # Step 5: Calculate the date of Easter
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31  # March = 3, April = 4
    day = ((h + l - 7 * m + 114) % 31) + 1

    # Return the date of Easter Sunday
    return datetime(year, month, day)

def get_special_dates(start_date: datetime, end_date: datetime):
    """
    Returns a list of the dates of christian celebration days between a given
    start date and end date.

    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.

    Returns:
        special_dates (list[datetime]): List of dates of celebration days.

    """
    # Initialize stuff
    years = [start_date.year, end_date.year]
    all_special_dates = []

    # Add all special dates to list
    for year in years:
        all_special_dates.append(datetime(year, 1, 1))          # nieuwjaarsdag
        all_special_dates.append(date_biddag(year))             # biddag
        pasen = date_1e_paasdag(year)                           # 1e paasdag
        all_special_dates.append(pasen + timedelta(days = -2))  # goede vrijdag
        all_special_dates.append(pasen + timedelta(days=1))     # 2e paasdag
        all_special_dates.append(pasen + timedelta(days=39))    # hemelvaart
        all_special_dates.append(pasen + timedelta(days=50))    # 2e pinksterdag
        all_special_dates.append(date_dankdag(year))            # dankdag
        all_special_dates.append(datetime(year, 12, 25))        # 1e kerstdag
        # all_special_dates.append(datetime(year, 12, 26))      # 2e kerstdag
        all_special_dates.append(datetime(year, 12, 31))        # oudejaarsdag

    # Initialize list for result
    special_dates = []

    # Check whether the special date is in the required timeframe
    for special_date in all_special_dates:
        if (start_date <= special_date and special_date <= end_date) and (
        special_date not in special_dates):
            special_dates.append(special_date)

    return special_dates

def get_sundays(start_date: datetime, end_date: datetime) -> list[datetime]:
    """
    Returns the dates of Sundays in between the given start date and end date.

    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.

    Returns:
        sundays (list[datetime]): The dates of Sundays.

    """
    # List to hold Sundays
    sundays = []

    # Find the first Sunday on or after the start date
    current_date = start_date
    while current_date.weekday() != 6:  # 6 represents Sunday
        current_date += timedelta(days=1)

    # Add all Sundays between the start and end date
    while current_date <= end_date:
        sundays.append(current_date)
        current_date += timedelta(weeks=1)  # Move to the next Sunday

    return sundays

def get_church_dates(start_date: datetime, end_date: datetime) -> list[datetime]:
    """
    Returns the dates on which there is church in between the given start date
    and end date.

    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.

    Returns:
        sundays (list[datetime]): The dates on which there is church.

    """
    # Get sundays and special days
    sundays = get_sundays(start_date, end_date)
    special_dates = get_special_dates(start_date, end_date)

    # Merge sundays and special days into one chronologically sorted list
    church_dates = sundays + special_dates
    church_dates.sort()

    return church_dates

def get_services(church_dates: list[datetime]) -> dict:
    """
    Returns the dates on which there is church in between the given start date
    and end date.

    Args:
        church_dates (list[datetime]): The list of dates on which there is church.

    Returns:
        services_dict (dict): A dictionary mapping the date to the church
            services that day. "0" means morning service, "1" means evening
            service, "0.5" means special service.

    """
    # Initialize services dict
    services_dict = {}

    # Append services
    for date in church_dates:
        if date.weekday() == 6:
            # Append morning and evening service
            services_dict[date] = [0, 1]
        elif date == datetime(date.year, 12, 25):
            # On Christmas, there is a morning and an evening service
            services_dict[date] = [0, 1]
        else:
            # The rest of the special days only have one service
            services_dict[date] = [0.5]

    # Return services array
    return services_dict

def is_special_date(date: datetime) -> bool:
    """
    Checks whether the provided date is a special day.

    Args:
        date (datetime): The date you want to check.

    Returns:
        bool: whether the date is a special date.

    """
    year = date.year
    special_dates = get_special_dates(datetime(year, 1, 1), datetime(year, 12, 31))
    if date in special_dates:
        return True
    else:
        return False

if __name__ == '__main__':
    starting_date = datetime(2024, 9, 29)
    ending_date = datetime(2025, 1, 22)
    all_church_dates = get_church_dates(starting_date, ending_date)
    display_dates = [date.strftime("%d-%m-%Y") for date in all_church_dates]
    print(display_dates)
