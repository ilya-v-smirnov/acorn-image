
import tkinter as tk
from tkinter import ttk
from .application_cellcounter import CellCounterApp
from .application_woundassay import WoundAssay
from .application_cellconfluent import CellConfluentAssay
from .models import AppModel


class MainView(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        self.app_model = AppModel()
        self.cell_counter_view = None
        self.wound_assay_view = None
        super().__init__(parent, *args, **kwargs)
        title = ttk.Label(self, text='Acorn Image', 
                         font=("TkDefaultFont", 16))
        button_wound_assay = ttk.Button(self, text='Wound Assay',
                                        command=self.start_wound_assay)
        button_cell_counter = ttk.Button(self, text='Cell Counter',
                                        command=self.start_cell_counter)                                        
        button_cell_confluent = ttk.Button(self, text='Cell Confluent',
                                           command=self.start_cell_confluent)
        title.pack(side=tk.TOP, fill=tk.BOTH, pady=10)
        button_cell_confluent.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        button_wound_assay.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        button_cell_counter.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

    def start_cell_counter(self):
        self.cell_counter_view = tk.Toplevel(self)
        self.cell_counter_view.title('Cell Counter')
        self.cell_counter_view.resizable(width=False, height=False)
        cell_counter = CellCounterApp(self.cell_counter_view, **self.app_model())
        cell_counter.pack()
        self.cell_counter_view.grab_set()

    def start_wound_assay(self):
        self.wound_assay_view = tk.Toplevel(self)
        self.wound_assay_view.title('Wound Assay')
        self.wound_assay_view.resizable(width=False, height=False)
        wound_assay = WoundAssay(self.wound_assay_view, **self.app_model())
        wound_assay.pack()
        self.wound_assay_view.grab_set()

    def start_cell_confluent(self):
        self.confluent_assay_view = tk.Toplevel(self)
        self.confluent_assay_view.title('Cell Confluent Assay')
        self.confluent_assay_view.resizable(width=False, height=False)
        confluent_assay = CellConfluentAssay(self.confluent_assay_view, **self.app_model())
        confluent_assay.pack()
        self.confluent_assay_view.grab_set()


class AcornImage(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Acorn Image')
        self.geometry('200x150')
        self.resizable(width=False, height=False)
        self.mainview = MainView(self)
        self.mainview.pack()
