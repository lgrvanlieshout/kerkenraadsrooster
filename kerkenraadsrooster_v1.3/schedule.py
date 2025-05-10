# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 14:03:39 2025

@author: Levi
"""
from datetime import datetime
from pydantic import BaseModel
import numpy as np

from date_utils import services_to_list, get_church_dates, get_services
from create_xlsx import kerkenraad, Persons, create_excel
from extract_from_xlsx import open_worksheet, extract_availability, extract_services


class Rules(BaseModel):
    n_persons: int = 6
    role_distribution: dict[str, int] = {
        "ouderling": 3,
        "kerkrentmeester": 1,
        "diaken": 2
    }
    params: dict[str, float] = {
        "n_persons": 1,
        "role_distribution": 1,
        "preferences": 1,
        "n_times_present": 1,
    }


class Schedule:
    def __init__(self, persons: Persons, start_date: datetime, end_date: datetime,
                 rules=Rules, file_path: str = None):

        self.persons = persons  #TODO: check that persons from excel and provided persons don't clash
        self.rules = rules

        if file_path is not None:
            self.file_path = file_path
            self.initialize_from_file(file_path)

        else:
            self.file_path = "test_kerkenraadsrooster.xlsx"
            church_dates = get_church_dates(start_date, end_date)
            self.services = get_services(church_dates)
            self.availability = self.create_array()
            self.duties = self.create_array()
            self.value = None

    def initialize_from_file(self, file_path):
        ws = open_worksheet(file_path)
        self.services = extract_services(ws)
        self.availability = extract_availability(ws)
        self.duties = self.create_array()
        self.score = self.schedule_score()

    def create_array(self):
        """
        Returns a numpy array based on the number of persons and the number
        of services.
        """
        # Determine number of persons and services
        n_persons = len(self.persons)
        n_services = len(services_to_list(self.services))

        return np.zeros((n_persons, n_services), dtype=int)

    def schedule_score(self):
        pass

    def __str__(self):
        return str(self.availability)

    def to_excel(self):
        create_excel(self.file_path, self.persons, self.services,
                     self.availability, self.duties)


if __name__ == "__main__":
    # Get dates of the schedule
    start_date = datetime(2025, 5, 24)
    end_date = datetime(2025, 9, 24)

    schedule = Schedule(kerkenraad, start_date, end_date)
    schedule.to_excel()