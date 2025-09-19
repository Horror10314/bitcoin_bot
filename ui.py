import time
import os
import tkinter.ttk as ttk

from trader import numeric_to_string_month
from tkinter import *

import customtkinter
from abc import *

# window size 
window_width = 900
window_height = 700

class FrameInterface(metaclass=ABCMeta):
    @abstractmethod
    def grid_widgets(self):
        pass

class SideNavigationFrame(FrameInterface, customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets here
        self.master = master


        self.home_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Default Setting",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.home_button_event)


        self.frame_2_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Specific Setting",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.frame_2_button_event)

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self, values=["Light", "Dark"],
                                                                command=self.change_appearance_mode_event)
        
        # select default frame
        self.select_frame_by_name("Default Setting")

    def grid_widgets(self):
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        self.home_button.grid(row=1, column=0, sticky="ew")
        self.frame_2_button.grid(row=2, column=0, sticky="ew")
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def home_button_event(self):
        self.select_frame_by_name("Default Setting")

    def frame_2_button_event(self):
        self.select_frame_by_name("Specific Setting")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "Default Setting" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "Specific Setting" else "transparent")

        # show selected frame
        # if name == "Default Setting":
        #     self.master.home_frame.grid(row=0, column=1, sticky="nsew")
        # else:
        #     self.master.home_frame.grid_forget()
        # if name == "Specific Setting":
        #     self.master.second_frame.grid(row=0, column=1, sticky="nsew")
        # else:
        #     self.master.second_frame.grid_forget()

class DefaultSettingFrame(FrameInterface, customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, corner_radius=0)

        # add widgets here
    
    def grid_widgets(self):
        print('asdfsad')

class SpecificSettingFrame(FrameInterface, customtkinter.CTkFont):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets here

    def grid_widgets(self):
        print('asdfadsf')

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # set the window 
        self.title("Bitcoin")
        self.geometry(f"{window_width}x{window_height}")
        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # navigation frame
        self.side_nav = SideNavigationFrame(self)
        self.side_nav.grid_widgets()

        # create defalut setting frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="gray75")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="home frame")
        self.home_frame_button_1.grid(row=1, column=0, padx=20, pady=10)
        

        # create specific coin setting frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="gray75")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.second_frame_button = customtkinter.CTkButton(self.second_frame, text="second frame")
        self.second_frame_button.grid(row=1, column=0, padx=20, pady=10)


def set_log_file_path(current_time: time.struct_time):
    # get month name
    month = numeric_to_string_month(current_time.tm_mon)

    # create log file name of current time
    log_file_name = f"{current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday}.log"
    
    # set the folder of the file to be year and month
    log_path = f"./log/{current_time.tm_year}/{month}/" + log_file_name

    return log_path


if __name__ == "__main__":
    app = App()
    app.mainloop()

