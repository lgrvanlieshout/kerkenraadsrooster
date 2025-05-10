# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 13:27:37 2024

@author: Levi
"""

import sys
import json

from collections import UserDict

from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar,
    QCheckBox, QDialog, QDialogButtonBox,
    QVBoxLayout, QHBoxLayout, QDateEdit,
    QMessageBox, QWidget, QPushButton,
    QComboBox, QCalendarWidget, QTextBrowser,
    QScrollArea, QLineEdit, QSpacerItem,
    QSizePolicy, QMenu, QFormLayout,
    QTableView, QTreeView, QListView,
)
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtCore import (
    Qt, QSize, QDate, 
    Signal, QObject, QAbstractTableModel,
)

from datetime import datetime


class ContactModelSignals(QObject):
    # Emit an "updated" signal when a property changes.
    updated = Signal()

class ContactModel(QAbstractTableModel()):
    def __init__(self, *args, **kwargs):
        self.signals = ContactModelSignals()
        super().__init__(*args, **kwargs)
    
    def __setitem__(self, key, value):
        # Get the existing value.
        previous = self.get(key)
        
        # Set the value.
        super().__setitem__(key, value) 
        if value != previous: 
            self.signals.updated.emit()



        
if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    window = ContactsWindow()
    window.show()
    
    app.exec()