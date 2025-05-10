# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 11:45:40 2024

@author: Levi
"""

import sys
import json

from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar,
    QCheckBox, QDialog, QDialogButtonBox,
    QVBoxLayout, QHBoxLayout, QDateEdit,
    QMessageBox, QWidget, QPushButton,
    QComboBox, QCalendarWidget, QTextBrowser,
    QScrollArea, QLineEdit, QSpacerItem,
    QSizePolicy, QMenu, QFormLayout,
)
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtCore import Qt, QSize, QDate, Signal

from datetime import datetime

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kerkenraadsrooster")
        self.resize(QSize(1000, 600))
        
        menu = self.menuBar()

        file_menu = menu.addMenu("&Bestand")
        schedule_menu = menu.addMenu("Rooster")
        
        
        # Add toolbar
        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        self.setStatusBar(QStatusBar(self))
        
        # Add a new file action
        new_file = QAction(QIcon("icons/blue-document.png"), "&Nieuw bestand", self)
        new_file.setStatusTip("Maak een nieuw rooster")
        new_file.setShortcut(QKeySequence("Ctrl+n"))
        
        toolbar.addAction(new_file)
        file_menu.addAction(new_file)
        
        # Add a open file action
        open_file = QAction(QIcon("icons/folder-horizontal-open.png"), "&Open", self)
        open_file.setStatusTip("Open een rooster")
        open_file.setShortcut(QKeySequence("Ctrl+o"))
        
        toolbar.addAction(open_file)
        file_menu.addAction(open_file)
        
        # Add a save action
        save_file = QAction(QIcon("icons/disk.png"), "&Opslaan", self)
        save_file.setStatusTip("Rooster opslaan")
        save_file.setShortcut(QKeySequence("Ctrl+s"))
        
        toolbar.addAction(save_file)
        file_menu.addAction(save_file)
        
        # Add a save as action
        save_file_as = QAction(QIcon("icons/disks.png"), "&Opslaan als", self)
        save_file_as.setStatusTip("Rooster opslaan als")
        save_file_as.setShortcut(QKeySequence("Ctrl+Shift+s"))
        
        toolbar.addAction(save_file_as)
        file_menu.addAction(save_file_as)
        file_exportmenu = file_menu.addMenu(QIcon("icons/document-export.png"), "&Exporteren...")
        
        # Add an export to excel action
        export_to_excel = QAction(QIcon("icons/blue-document-excel.png"), "&Exporteren naar excel", self)
        export_to_excel.setStatusTip("Rooster exporteren naar excel")
        
        toolbar.addAction(export_to_excel)
        file_exportmenu.addAction(export_to_excel)
        
        # Add an export to pdf action
        export_to_pdf = QAction(QIcon("icons/blue-document-pdf.png"), "&Exporteren naar pdf", self)
        export_to_pdf.setStatusTip("Rooster exporteren naar pdf")
        
        toolbar.addAction(export_to_pdf)
        file_exportmenu.addAction(export_to_pdf)
        
        # Add a choose timeframe action
        choose_timeframe = QAction(QIcon("icons/calendar-day.png"), "Kies periode", self)
        choose_timeframe.setStatusTip("Selecteer begin- en einddatum van het rooster")
        choose_timeframe.setShortcut(QKeySequence("Ctrl+d"))
        choose_timeframe.triggered.connect(self.choose_timeframe_triggered)
        
        toolbar.addSeparator()
        toolbar.addAction(choose_timeframe)
        schedule_menu.addAction(choose_timeframe)
        
        # Add an manage participants action
        self.contactswindow = None
        manage_participants = QAction(QIcon("icons/user-black.png"), "Selecteer deelnemers", self)
        manage_participants.setStatusTip("Selecteer wie er in het rooster komen")
        manage_participants.triggered.connect(self.manage_contacts_triggered)
        
        toolbar.addAction(manage_participants)
        schedule_menu.addAction(manage_participants)
        
        
    def choose_timeframe_triggered(self):        
        dlg = ChooseTimeframeDialog(self)
        
        if dlg.exec():
            print("De datum is aangepast")
            self.start_date = dlg.start_date
            self.end_date = dlg.end_date
        else:
            print("Cancel")
            
        print("startdatum rooster: " + str(dlg.start_date))
        print("einddatum rooster: " + str(dlg.end_date))
    
    def manage_contacts_triggered(self):
        if self.contactswindow == None:
            self.contactswindow = ContactsWindow(self)
        self.contactswindow.show()
    


class ChooseTimeframeDialog(QDialog):
    def __init__(self, parent=None, initial_dates=None):
        super().__init__(parent)
        
        self.setWindowTitle("Kies periode")
        
        if initial_dates == None:
            current_date = datetime.today().strftime('%d-%m-%Y')
            initial_starting_date = QDate.fromString(current_date, 'dd-MM-yyyy')
            initial_ending_date = QDate.fromString(current_date, 'dd-MM-yyyy')
        else:
            self.initial_start_date  = initial_dates[0].strftime('%d-%m-%Y')
            self.initial_end_date = initial_dates[1].strftime('%d-%m-%Y')
            initial_starting_date = QDate.fromString(initial_dates[0], 'dd-MM-yyyy')
            initial_ending_date = QDate.fromString(initial_dates[1], 'dd-MM-yyyy')
        
        self.start_date = initial_starting_date.toPython()
        self.end_date = initial_ending_date.toPython()
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.update)
        self.buttonBox.rejected.connect(self.reject)
        
        layout1 = QVBoxLayout()
        message = QLabel("Vul hier de begin- en einddatum van het rooster in.")        
        layout1.addWidget(message)
        
        layout2 = QHBoxLayout()
        
        ### Add date selection for start of schedule
        sublayout1 = QVBoxLayout()
        sublayout1.addWidget(QLabel("Begindatum:"))
        # Add date widget
        self.starting_dateedit = QDateEdit()
        self.starting_dateedit.setDate(initial_starting_date)
        self.starting_dateedit.setDisplayFormat('dd-MM-yyyy')
        sublayout1.addWidget(self.starting_dateedit)
        # Add layout
        layout2.addLayout(sublayout1)
        
        ### Add date selection for end of schedule
        sublayout2 = QVBoxLayout()
        sublayout2.addWidget(QLabel("Einddatum:"))
        # Add date widget
        self.end_dateedit = QDateEdit()
        self.end_dateedit.setDate(initial_ending_date)
        self.end_dateedit.setDisplayFormat('dd-MM-yyyy')
        sublayout2.addWidget(self.end_dateedit)
        # Add layout
        layout2.addLayout(sublayout2)
        
        layout1.addLayout(layout2)
        layout1.addWidget(self.buttonBox)
        self.setLayout(layout1)
    
    def update(self):
        
        self.start_date = self.starting_dateedit.date().toPython()
        self.end_date = self.end_dateedit.date().toPython()
        
        #converted_start_date = time.strptime(self.start_date, "%Y-%m-%d")
        #converted_end_date = time.strptime(self.end_date, "%Y-%m-%d")
        if self.start_date > self.end_date:
            error_message = "De einddatum is eerder dan de startdatum."
            QMessageBox.critical(self, "Error", error_message)
        else:
            self.accept()
            

class ContactWidget(QWidget):
    clicked = Signal(Qt.MouseButton)
    
    def __init__(self, name, info):
        super(ContactWidget, self).__init__()
        self.name = name
        self.is_participant = info["is_participant"]
        self.send_email = info["send_email"]
        self.email = info["email"]
        self.number = info["telnr"]
        self.role = info["role"]
        self.preference = info["preference"]
        self.isDeleted = False
        
        layout = QHBoxLayout()
        
        self.checkbox = QCheckBox()
        if self.is_participant:
            self.checkbox.setChecked(True)
        else:
            self.checkbox.setChecked(False)
        
        layout.addWidget(self.checkbox)
        self.nameLabel = QLabel(self.name)
        layout.addWidget(self.nameLabel)
        self.roleLabel = QLabel(self.role)
        layout.addWidget(self.roleLabel)
        
        self.setLayout(layout)
        
        self.context_menu = QMenu(self)
        delete = QAction("Verwijderen", self)
        delete.triggered.connect(self.delete)
        self.context_menu.addAction(delete)
    
    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())
    
    def delete(self):
        print("Verwijder contactpersoon")
        self.hide()
        self.isDeleted = True
        
    def mousePressEvent(self, event):
        self.clicked.emit([self.name, event])
    
    def mouseDoubleClickEvent(self, event):
        preference_options = ["Geen", "Ochtend", "Avond", "Om de week"]
        dlg = EditContactDialog(self, preference_options)
        dlg.setWindowTitle("Contact bewerken")
        dlg.exec()


class EditContactDialog(QDialog):
    def __init__(self, contact, preference_options):
        super().__init__()
        self.name = contact.name
        self.is_participant = contact.is_participant
        self.send_email = contact.send_email
        self.email = contact.email
        self.number = contact.number
        self.role = contact.role
        self.preference = contact.preference
        self.preference_options = preference_options
        self.parent = contact
        
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(buttons)
        buttonBox.accepted.connect(self.save_changes)
        buttonBox.rejected.connect(self.reject)
        
        layout = QVBoxLayout()
        
        formHeaderLayout = QFormLayout()
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setText(self.name)
        formHeaderLayout.addRow("Naam:", self.nameLineEdit)
        layout.addLayout(formHeaderLayout)
        
        formBodyLayout = QHBoxLayout()
        
        # Set fields of first column of form
        formLayout1 = QFormLayout()
        
        self.numberLineEdit = QLineEdit()
        self.numberLineEdit.setText(self.number)
        formLayout1.addRow("Telefoonnummer:", self.numberLineEdit)
        
        self.emailLineEdit = QLineEdit()
        self.emailLineEdit.setText(self.email)
        formLayout1.addRow("Email:", self.emailLineEdit)
        
        self.send_email_checkbox = QCheckBox()
        if self.send_email:
            self.send_email_checkbox.setChecked(True)
        else:
            self.send_email_checkbox.setChecked(False)
        formLayout1.addRow("Ontvangt mail:", self.send_email_checkbox)
        
        formBodyLayout.addLayout(formLayout1)
        
        # Set fields for second column of form
        formLayout2 = QFormLayout()
        
        self.roleLineEdit = QLineEdit()
        self.roleLineEdit.setText(self.role)
        formLayout2.addRow("Ambt:", self.roleLineEdit)
        
        self.preferenceComboBox = QComboBox()
        self.preferenceComboBox.addItems(preference_options)
        self.preferenceComboBox.currentIndexChanged.connect(self.preference_changed)
        formLayout2.addRow("Voorkeur:", self.preferenceComboBox)
        
        self.is_participant_field = QLabel()
        if self.is_participant:
            self.is_participant_field.setText("Ja")
        else:
            self.is_participant_field.setText("Nee")
        formLayout2.addRow("Deelnemer:", self.is_participant_field)
        
        formBodyLayout.addLayout(formLayout2)
        layout.addLayout(formBodyLayout)
        
        layout.addWidget(buttonBox)
        self.setLayout(layout)
    
    def preference_changed(self, index):
        print("Nieuwe voorkeur: " + str(self.preference_options[index]))
    
    def save_changes(self):
        old_name = self.name
        self.name = self.nameLineEdit.text()
        self.parent.name = self.name
        self.parent.nameLabel.setText(self.name)
        
        self.number = self.numberLineEdit.text()
        self.email = self.emailLineEdit.text()
        
        self.send_email = self.send_email_checkbox.isChecked()
        self.parent.checkbox.setChecked(self.send_email)
        self.parent.send_email = self.send_email
        
        self.role = self.roleLineEdit.text()
        self.parent.role = self.role
        self.parent.roleLabel.setText(self.role)
        
        self.preference = self.preferenceComboBox.currentText()
        
        with open("contacts.json", "r") as file:
            contacts = json.load(file)
            contacts.pop(old_name)
            contacts[self.name] = {"is_participant" : self.is_participant,
                                   "email" : self.email,
                                   "telnr" : self.number,
                                   "role" : self.role,
                                   "send_email" : self.send_email,
                                   "preference" : self.preference
                                   }
        
        with open("contacts.json", "w") as file:
            json.dump(contacts, file)
        
        self.accept()


class ContactsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        
        self.controls = QWidget()
        self.setWindowTitle("Contacten")
        
        with open("contacts.json", "r") as file:
            contacts = json.load(file)
        self.contacts = contacts
        
        # self.participants = {}
        # for contact in self.contacts:
        #     if self.contacts[contact]["is_participant"]:
        #         self.participants[contact] = self.contacts[contact]
        # print(self.participants)
        
        layout1 = QVBoxLayout()
        
        layout2 = QVBoxLayout()
        
        headerline = QHBoxLayout()
        headerline.addWidget(QLabel("Contacten"))
        add_contact_button = QPushButton("Voeg toe...", self)
        add_contact_button.clicked.connect(self.add_contact)
        headerline.addWidget(add_contact_button)
        layout1.addLayout(headerline)
        
        # Search bar
        self.searchbar = QLineEdit()
        self.searchbar.textChanged.connect(self.update_display)
        layout1.addWidget(self.searchbar)
        
        self.contact_widgets = {}
        
        for name in self.contacts:
            item = ContactWidget(name, self.contacts[name])
            layout2.addWidget(item)
            self.contact_widgets[name] = item
            item.clicked.connect(self.contact_clicked)
        
        # Add spacer
        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout2.addItem(spacer)
        
        self.controls.setLayout(layout2)
        
        # Add scrollability to contact list
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.controls)
        layout1.addWidget(self.scroll)
        
        # Add OK and Cancel Buttons
        buttonBox = QHBoxLayout()
        
        # Add OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        buttonBox.addWidget(ok_button)
        
        # Add Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttonBox.addWidget(cancel_button)
        
        layout1.addLayout(buttonBox)
        self.setLayout(layout1)

    
    def update_display(self, text):
        for contact in self.contact_widgets.values():
            if text.lower() in contact.name.lower() and not contact.isDeleted:
                contact.show()
            else:
                contact.hide()
    
    def accept(self):
        print("OK")
        
        with open("contacts.json", "r") as file:
            contacts = json.load(file)
        
        for contact in self.contact_widgets.values():
            contact.is_participant = contact.checkbox.isChecked()
            if contact.isDeleted:
                self.contacts.pop(contact.name)
                contacts.pop(contact.name)
        
        with open("contacts.json", "w") as file:
            json.dump(contacts, file)
        
        self.searchbar.clear()
        self.close()
    
    def reject(self):
        print("Cancel")
        for contact in self.contact_widgets.values():
            contact.checkbox.setChecked(contact.is_participant)
            contact.isDeleted = False
            if contact.isHidden():
                contact.show()
        self.searchbar.clear()
        self.close()
    
    def add_contact(self):
        print("Voeg contact toe")
    
    def contact_clicked(self, event):        
        # Handling event
        print("Contactswindow: " + str(event[0]))

        
if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

window = MainWindow()
window.show()

app.exec()