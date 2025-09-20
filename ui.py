import time

from trader import numeric_to_string_month
from tkinter import *

import customtkinter


# window size 
window_width = 900
window_height = 700

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bitcoin Trader Manager v1")
        self.geometry(f"{window_width}x{window_height}")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


        # ================================================= create navigation frame ================================================= 
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.sidebar_frame_label = customtkinter.CTkLabel(self.sidebar_frame, text="Bitcoin\nTrader\nManager",
                                                             compound="center", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.sidebar_frame_label.grid(row=0, column=0, padx=0, pady=10)

        self.home_button = customtkinter.CTkButton(self.sidebar_frame, corner_radius=0, height=40, border_spacing=10, text="Default Setting",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.sidebar_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 2",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")


        # ================================================= create home frame =================================================
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # in this frame
        # 상한
        # 하한
        # 손절가
        # Time interval
        # 적용 버튼

        # create frame
        self.mainview = customtkinter.CTkFrame(self.home_frame, width=250)
        self.mainview.pack(expand=True, fill="both", padx=(20, 20), pady=(20, 20))

        self.label_tab_2 = customtkinter.CTkLabel(self.mainview, text="CTkLabel on Tab 2")
        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.mainview, dynamic_resizing=False,
                                                        values=["Value 1", "Value 2", "Value Long Long Long"])
        self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.combobox_1 = customtkinter.CTkComboBox(self.mainview,
                                                    values=["Value 1", "Value 2", "Value Long....."])
        self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.string_input_button = customtkinter.CTkButton(self.mainview, text="Open CTkInputDialog",
                                                           command=self.open_input_dialog_event)
        self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))

        
        # ================================================= create second frame =================================================
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # in this frame
        # 코인 선택
        # 상한
        # 하한
        # 손절가
        # Time interval
        # 적용 버튼

        # create frame
        self.mainview2 = customtkinter.CTkFrame(self.second_frame, width=250)
        self.mainview2.pack(expand=True, fill="both", padx=(20, 20), pady=(20, 20))

        self.mainview2_coin_list = ["BTCUSDT", "ETHUSDT", "YFIUSDT"] # TODO implement ipc for communicatinf with trader.py

        self.label_tab_2 = customtkinter.CTkLabel(self.mainview2, text="Select Coin: ")
        self.label_tab_2.grid(row=0, column=0, padx=3, pady=(10, 10))
        self.combobox_1 = customtkinter.CTkComboBox(self.mainview2,
                                                    values=self.mainview2_coin_list)
        self.combobox_1.grid(row=0, column=1, padx=(0, 20), pady=(10, 10))

        
        self.string_input_button = customtkinter.CTkButton(self.mainview2, text="Open CTkInputDialog",
                                                           command=self.open_input_dialog_event)
        self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))


        # ================================================= any other setting =================================================
        # select default frame
        self.select_frame_by_name("Default Setting")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "Default Setting" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "Specific Setting" else "transparent")

        # show selected frame
        if name == "Default Setting":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "Specific Setting":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
    
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def home_button_event(self):
        self.select_frame_by_name("Default Setting")

    def frame_2_button_event(self):
        self.select_frame_by_name("Specific Setting")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


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

