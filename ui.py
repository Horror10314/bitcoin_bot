import customtkinter
import json
import socket
import struct

# window size 
window_width = 900
window_height = 700

def send_msg(sock: socket.socket, payload: dict):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sock.sendall(struct.pack("!I", len(data)) + data)

def recv_msg(sock: socket.socket) -> dict:
    data = sock.recv(1024)
    return json.loads(data.decode("utf-8"))

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # ============================ network connection setting for ipc with trader.py ========================================
        self.HOST, self.PORT = "localhost", 55555
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))

        # ================================================= UI part ===============================================================        
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

        with open("default.json", "r", encoding="utf-8") as default_setting:
            self.default_setting = json.load(default_setting)

        # create frame
        self.mainview = customtkinter.CTkFrame(self.home_frame, width=250)
        self.mainview.pack(expand=True, fill="both", padx=(20, 20), pady=(20, 20))
        self.mainview.grid_rowconfigure(5, weight=1)
        self.mainview.grid_columnconfigure(4, weight=1)

        title_font = customtkinter.CTkFont(family="System", size=20, weight="bold")

        customtkinter.CTkLabel(self.mainview, text="기본 설정", font=title_font).grid(row=0, column=0, padx=20, pady=(10, 5)) # title

        # self.default_upper_bound_label = customtkinter.CTkLabel(self.mainview, text="익절가: ")
        # self.default_upper_bound_label.grid(row=1, column=0, padx=20, pady=(10, 10))
        # self.default_upper_bound_entry = customtkinter.CTkEntry(self.mainview)
        # self.default_upper_bound_entry.grid(row=1, column=1, padx=(0, 20), pady=(10, 10))

        
        # self.default_lower_bound_label = customtkinter.CTkLabel(self.mainview, text="하한가: ")
        # self.default_lower_bound_label.grid(row=2, column=0, padx=20, pady=(0,10))
        # self.default_upper_bound_entry = customtkinter.CTkEntry(self.mainview)
        # self.default_upper_bound_entry.grid(row=2, column=1, padx=(0, 20), pady=(0, 10))


        # self.default_stop_loss_label = customtkinter.CTkLabel(self.mainview, text="손절가: ")
        # self.default_stop_loss_label.grid(row=3, column=0, padx=20, pady=(0,10))  
        # self.default_upper_bound_entry = customtkinter.CTkEntry(self.mainview)
        # self.default_upper_bound_entry.grid(row=3, column=1, padx=(0, 20), pady=(0, 10))


        self.default_frequency_label = customtkinter.CTkLabel(self.mainview, text="포지션 확인 빈도: ")
        self.default_frequency_label.grid(row=1, column=0, padx=20, pady=(10,10))
        self.default_frequency_entry = customtkinter.CTkEntry(self.mainview, placeholder_text=str(self.default_setting['frequency'])+"초")
        self.default_frequency_entry.grid(row=1, column=1, padx=(0, 20), pady=(10, 10))

        self.strategy_list = ["전술 1"]

        self.default_stratagy_label = customtkinter.CTkLabel(self.mainview, text="기본 코인 전략: ")
        self.default_stratagy_label.grid(row=2, column=0, padx=20, pady=(0,10))
        self.default_stratagy_combobox = customtkinter.CTkComboBox(self.mainview, values=self.strategy_list)
        self.default_stratagy_combobox.grid(row=2, column=1, padx=(0, 20), pady=(0, 10))


        self.default_apply_butten = customtkinter.CTkButton(self.mainview, text="적용", command=self.send_default_setting_request) 
        self.default_apply_butten.grid(row=5, column=4, padx=20, pady=(0, 20), sticky="se")


        # self.label_tab_2 = customtkinter.CTkLabel(self.mainview, text="CTkLabel on Tab 2")
        # self.optionmenu_1 = customtkinter.CTkOptionMenu(self.mainview, dynamic_resizing=False,
        #                                                 values=["Value 1", "Value 2", "Value Long Long Long"])
        # self.optionmenu_1.grid(row=0, column=3, padx=20, pady=(20, 10))
        # self.combobox_1 = customtkinter.CTkComboBox(self.mainview,
        #                                             values=["Value 1", "Value 2", "Value Long....."])
        # self.combobox_1.grid(row=1, column=3, padx=20, pady=(10, 10))
        # self.string_input_button = customtkinter.CTkButton(self.mainview, text="Open CTkInputDialog",
        #                                                    command=self.open_input_dialog_event)
        # self.string_input_button.grid(row=2, column=3, padx=20, pady=(10, 10))

        
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
        self.mainview2.grid_rowconfigure(6, weight=1)
        self.mainview2.grid_columnconfigure(4, weight=1)

        customtkinter.CTkLabel(self.mainview2, text="코인 설정", font=title_font).grid(row=0, column=0, padx=20, pady=(10, 5)) # title

        self.coin_list_literal = "코인을 선택하세요"
        self.mainview2_coin_list = ["btcusdt", "ethusdt"] # TODO implement ipc for communicatinf with trader.py / use  send_get_coin_symbols_request()
        
        self.coin_list_literal = "포지션 없음" if not self.mainview2_coin_list else self.coin_list_literal

        self.coin_select_label = customtkinter.CTkLabel(self.mainview2, text="코인 선택: ")
        self.coin_select_label.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.coin_combobox = customtkinter.CTkComboBox(self.mainview2, values=self.mainview2_coin_list, command=self.send_get_coin_setting_request)
        self.coin_combobox.grid(row=1, column=1, padx=(0, 20), pady=(10, 10))
        self.coin_combobox.set(self.coin_list_literal)

        # add widgets only if postion is not empty 
        if self.mainview2_coin_list:
            self.upper_bound_label = customtkinter.CTkLabel(self.mainview2, text="익절가: ")
            self.upper_bound_label.grid(row=2, column=0, padx=20, pady=(0, 10))
            self.upper_bound_entry = customtkinter.CTkEntry(self.mainview2)
            self.upper_bound_entry.grid(row=2, column=1, padx=(0, 20), pady=(0, 10))

            
            self.lower_bound_label = customtkinter.CTkLabel(self.mainview2, text="하한가: ")
            self.lower_bound_label.grid(row=3, column=0, padx=20, pady=(0,10))
            self.lower_bound_entry = customtkinter.CTkEntry(self.mainview2)
            self.lower_bound_entry.grid(row=3, column=1, padx=(0, 20), pady=(0, 10))


            self.stop_loss_label = customtkinter.CTkLabel(self.mainview2, text="손절가: ")
            self.stop_loss_label.grid(row=4, column=0, padx=20, pady=(0,10))  
            self.stop_loss_entry = customtkinter.CTkEntry(self.mainview2)
            self.stop_loss_entry.grid(row=4, column=1, padx=(0, 20), pady=(0, 10))


            self.frequency_label = customtkinter.CTkLabel(self.mainview2, text="코인 확인 빈도: ")
            self.frequency_label.grid(row=5, column=0, padx=20, pady=(0,10))
            self.frequency_entry = customtkinter.CTkEntry(self.mainview2)
            self.frequency_entry.grid(row=5, column=1, padx=(0, 20), pady=(0, 10))

            self.apply_butten = customtkinter.CTkButton(self.mainview2, text="적용", command=self.send_coin_setting_request) 
            self.apply_butten.grid(row=6, column=4, padx=20, pady=(0, 20), sticky="se")

        # self.string_input_button = customtkinter.CTkButton(self.mainview2, text="Open CTkInputDialog",
        #                                                    command=self.open_input_dialog_event)
        # self.string_input_button.grid(row=6, column=0, padx=20, pady=(10, 10))


        # ================================================= any other initial setting =================================================
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
            self.send_get_coin_symbols_request()
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


    # ======================================== network methods ===========================================================
    # communicating with trader.py
    def send_default_setting_request(self):
        print("im sending something to trader.py")
        request = {
            "req" : "set",
            "what": "default"
        }
        # get all setting data in the frame
        

        # then send
        self.sock.send(json.dumps(request, ensure_ascii=False).encode())
        msg = json.loads(self.sock.recv(65535).decode())

        if msg['ret'] == 'success':
            pass


    def send_coin_setting_request(self):
        print("im sending coin thing to trader.py")
        request = {
            "req" : "set",
            "what": self.coin_combobox.get() # get current values
        }
        # get all setting data in the frame

        # then send
        self.sock.send(json.dumps(request, ensure_ascii=False).encode())
        msg = json.loads(self.sock.recv(65535).decode())

        if msg['ret'] == 'success':
            pass


    def send_get_coin_symbols_request(self):
        request = {
            "req" : "get",
            "what" : "symbols"
        }
        self.sock.send(json.dumps(request, ensure_ascii=False).encode())

        msg = json.loads(self.sock.recv(65535).decode())

        if msg['ret'] == 'success':
            self.mainview2_coin_list = msg['symbols']
            self.coin_combobox.configure(values=self.mainview2_coin_list)
            self.coin_combobox.update()
            self.coin_combobox.set('')


    def send_get_coin_setting_request(self, choice):
        request = {
            "req" : "get",
            "what": choice,
        }

        self.sock.send(json.dumps(request, ensure_ascii=False).encode())

        msg = json.loads(self.sock.recv(65535).decode())

        if msg['ret'] == 'success':
            pass

        


if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.sock.close()
