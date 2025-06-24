import multiprocessing
import re
import tkinter as tk
import tkinter.messagebox
import keyboard
import core
import core.context
import core.profile

def extract_numbers_regex(text):
    numbers = re.findall(r'\d+', text)
    return numbers[0]

class TextInputTopLevel():
    def __init__(self, root, title, submit_lbl="Submit", cancel_lbl="Cancel", size="360x120", on_post_submit=lambda:True):
        self._top = tk.Toplevel(root)
        self._top.geometry(size)
        self._top.title(title)
        self._frame = tk.Frame(self._top)
        self._frame.grid(column=0, row=0, sticky="nesw")
        self._textinput = tk.Entry(self._frame)
        self._createbtn = tk.Button(self._frame, text=submit_lbl, command=self._on_submit)
        self._cancelbtn = tk.Button(self._frame, text=cancel_lbl, command=self.close)
        self._textinput.pack()
        self._createbtn.pack()
        self._cancelbtn.pack()
        self._on_post_submit = on_post_submit
    
    def _on_submit(self):
        self.on_post_submit()
        self.close()
    
    def close(self):
        self._top.destroy()
        self._top.update()

    def mainloop(self):
        self._top.mainloop()

class CreateNewUserTopLevel(TextInputTopLevel):
    def __init__(self, root, title, submit_lbl="Submit", cancel_lbl="Cancel", size="360x120", on_post_submit=lambda : True):
        super().__init__(root, title, submit_lbl, cancel_lbl, size, on_post_submit)

    def _on_submit(self):
        new_username = self._textinput.get()
        core.user.User.create_user(new_username)
        self._on_post_submit()
        self.close()

class SettingsWin():
    def __init__(self, ctx: core.context.MainContext):
        self._ctx = ctx
        self.settings_changes_q = []
        self._gui()
        self.sidelist.bind("<<ListboxSelect>>", self._handleSideListSelection)
        self.sidelist.selection_set(0)
        self.saveBtn.config(command=self._handleSaveBtn)
        self.applyBtn.config(command=self._handleApplyBtn)
        self.closeBtn.config(command=self._handleCloseButton)
    
    def _gui(self):
        self.root = tk.Tk()
        self.root.title("OCR-Screen")
        self.root.geometry("720x420")

        self.mainframe = tk.Frame(self.root)
        self.sideframe = tk.Frame(self.root)
        self.sideframe.grid(row=0, column=0, sticky="nswe", padx=(5, 0), pady=5)
        self.mainframe.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.sidelist = tk.Listbox(self.sideframe)
        self.sidelist.pack(fill=tk.BOTH, expand=True)
        self.sidelist.insert(tk.END, "User")
        self.sidelist.insert(tk.END, "Profile")

        self.heading_frame = tk.Frame(self.mainframe)
        self.heading_frame.grid(row=0, column=0, sticky="we")
        self.settings_heading = tk.Label(self.heading_frame, text="User Settings", font=(None, 10, "bold"))
        self.settings_heading.pack(side="left", anchor="n", pady=(0, 5))
        
        self.contentframe = tk.Frame(self.mainframe)
        self.contentframe.grid(row=1, column=0, sticky="nswe")

        self._packui(self.contentframe, "User")

        self.button_frame = tk.Frame(self.mainframe)
        self.button_frame.grid(row=2, column=0, columnspan=1, sticky="we")
        
        self.mainframe.rowconfigure(0, weight=0)
        self.mainframe.rowconfigure(1, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        
        self.saveBtn = tk.Button(self.button_frame, text="Save", width=8)
        self.applyBtn = tk.Button(self.button_frame, text="Apply", width=8)
        self.closeBtn = tk.Button(self.button_frame, text="Close", width=8)
        self.save_hint = tk.Label(self.button_frame, text="")
        
        self.saveBtn.pack(side="right")
        self.applyBtn.pack(side="right", padx=(0, 5))
        self.closeBtn.pack(side="right", padx=(0, 5))
        self.save_hint.pack(side="right", padx=(0, 5))

    def _handleSaveBtn(self):
        for f in self.settings_changes_q:
            f()
        self.settings_changes_q = []
        with self._ctx.signal_cond:
            self._ctx.signal.value = core.context.SignalState.RESTART
            self._ctx.signal_cond.notify_all()
        self.root.quit()
        
    def _handleApplyBtn(self):
        for f in self.settings_changes_q:
            f()
        self.settings_changes_q = []

        self.sidelist.config(state=tk.NORMAL)
        try:
            self.profilelist.config(state=tk.NORMAL)
        except:
            pass

        self.save_hint.config(text="Changes saved")
        with self._ctx.signal_cond:
            self._ctx.signal.value = core.context.SignalState.RESTART
            self._ctx.signal_cond.notify_all()
            
    def _handleCloseButton(self):
        self.root.quit()

    def _handleSideListSelection(self, event):
        idx = event.widget.curselection()
        if not idx:
            return
        val = event.widget.get(idx)
        self._packui(self.contentframe, val)

    def _queue_changes(self, func):
        self.settings_changes_q.append(func)

        self.sidelist.config(state=tk.DISABLED)
        try:
            self.profilelist.config(state=tk.DISABLED)
        except:
            pass

        self.save_hint.config(text="Unsaved changes!")

    def _cancel_changes_queue(self):
        self.settings_changes_q = []
        self.sidelist.config(state=tk.NORMAL)
        try:
            self.profilelist.config(state=tk.DISABLED)
        except:
            pass
        self.save_hint.config(text="")

    def _packui(self, frame, settings):
        if settings == "User":
            self.settings_heading.config(text="User Settings")
            self._clear_frame(frame)
            
            current_active_user = core.user.User.get_active_user().username
            avail_users = [au.username for au in core.user.User.get_users()]
            selected_user = tk.StringVar(frame)

            # Create new user button
            def create_new_user():
                CreateNewUserTopLevel(frame, "Create New User", on_post_submit=lambda: self._packui(self.contentframe, "User"))

            self._create_label_button_pair(frame, "", "New User", create_new_user)
            
            # Create delete profile button
            def delete_user():
                try:
                    core.user.User.delete_user(selected_user.get())
                except:
                    tkinter.messagebox.showwarning("Cannot user", "Cannot delete default user")
                    return
                core.user.User("default").set_active()
                self._packui(frame, "User")
                return
            self._create_label_button_pair(frame, "", "Delete User", delete_user)

            # Select active user option menus
            def save_active_user():
                self._queue_changes(lambda: core.user.User(selected_user.get()).set_active())
            self._create_label_option_menu_pair(frame, "Active user", avail_users, selected_user, save_active_user, current_active_user)

        if settings == "Profile":
            self.settings_heading.config(text="Profile Settings")
            self._clear_frame(frame)
            self.profilelist = None

            # Create new profile button
            def create_new_profile():
                current_active_user = core.user.User.get_active_user()
                new_profile = current_active_user.new_profile()
                self.profilelist.insert(tk.END, f"Profile {new_profile.profile_id}")
            self._create_label_button_pair(frame, "", "New Profile", create_new_profile)

            # Create delete profile button
            def delete_profile():
                selected_profilelist = self.profilelist.get(self.profilelist.curselection())
                selected_profile = core.profile.Profile.get_profile(extract_numbers_regex(selected_profilelist))
                selected_profile.delete()
                self._packui(frame, "Profile")
                return
            self._create_label_button_pair(frame, "", "Delete Profile", delete_profile)

            # Profile boxlist
            profilelist_fr = tk.Frame(frame)
            profilelist_fr.pack(side="left", fill=tk.BOTH)

            current_active_user = core.user.User.get_active_user().username
            profiles = core.profile.Profile.from_username(current_active_user, all=True)
            
            self.profilelist = tk.Listbox(profilelist_fr)
            self.profilelist.pack(fill=tk.Y, anchor="w", expand=True)
            for i in profiles:
                self.profilelist.insert(tk.END, f"Profile {i.profile_id}")
            if len(profiles) > 0:
                self.profilelist.selection_set(0)
                selected_profilelist = self.profilelist.get(self.profilelist.curselection())
                selected_profile = core.profile.Profile.get_profile(extract_numbers_regex(selected_profilelist))

            profilesettings_fr = tk.Frame(frame)
            profilesettings_fr.pack(side="left", anchor="w", fill=tk.BOTH, expand=True, padx=(5, 0), pady=(5, 0))
            
            def handle_profilelist_select(event):
                idx = event.widget.curselection()
                if not idx:
                    return
                val = event.widget.get(idx)
                selected_profile = core.profile.Profile.get_profile(extract_numbers_regex(val))
                self._pack_profile_settings_ui(profilesettings_fr, selected_profile)
            self.profilelist.bind("<<ListboxSelect>>", handle_profilelist_select)

            # Profile Settings Frame Content
            if len(profiles) == 0:
                tk.Label(frame, text="No profiles for the current active user")
            else:
                self._pack_profile_settings_ui(profilesettings_fr, selected_profile)


    def _pack_profile_settings_ui(self, frame, selected_profile: core.profile.Profile):
        self._clear_frame(frame)

        # is_enabled property
        is_enabled = tk.IntVar(frame, selected_profile.is_enabled)
        def toggle_enabled():
            print("Queuing enabled state changes..")
            def save_chang():
                selected_profile.is_enabled = is_enabled.get()
                selected_profile.update()
            self._queue_changes(save_chang)
        self._create_label_checkbutton_pair(frame, "Enabled", is_enabled, toggle_enabled)

        # hotkey
        fr = tk.Frame(frame)
        hotkey_lbl = tk.Label(fr, text="Hotkey")
        current_hotkey = selected_profile.hotkey if selected_profile.hotkey is not None else "No Hotkey Set"
        read_hotkey_btn = tk.Button(fr, text=current_hotkey)
        def read_hotkey():
            with self._ctx.signal_cond:
                # Pausing the hotkey input doesn't work because suppress is set to False.
                # You need to suppress in order to block. But, if the suppress set to
                # True, it will cause some weird input behaviour.
                # See: https://github.com/boppreh/keyboard/issues/379
                self._ctx.signal.value = core.context.SignalState.PAUSE
                self._ctx.signal_cond.notify_all()
                read_hotkey_btn.config(text="Reading hotkey..")
                new_hotkey = keyboard.read_hotkey(suppress=False)
                read_hotkey_btn.config(text=new_hotkey)
                self._ctx.signal.value = core.context.SignalState.DEFAULT
                self._ctx.signal_cond.notify_all()
            def save_chang():
                selected_profile.hotkey = new_hotkey
                selected_profile.update()
            self._queue_changes(save_chang)
        read_hotkey_btn.config(command=read_hotkey)
        hotkey_lbl.pack(side="left")
        read_hotkey_btn.pack(side="right")
        fr.pack(side="top", anchor="n", fill=tk.X)

        # mode
        current_mode = selected_profile.mode
        selected_mode = tk.StringVar(frame)
        avail_modes = ["selection", "detection"]
        def save_mode():
            def save_chang():
                selected_profile.mode = selected_mode.get()
                selected_profile.update()
            self._queue_changes(save_chang)
        self._create_label_option_menu_pair(frame, "Mode", avail_modes, selected_mode, save_mode, current_mode)

        # model
        modelcfg_fr = tk.Frame(frame, pady=5)

        current_model = selected_profile.model
        selected_model = tk.StringVar(frame)
        avail_models = ["tesseract", "paddleocr"]
        def save_model():
            def save_chang():
                selected_profile.model = selected_model.get()
                selected_profile.update()
            self._queue_changes(save_chang)
            self._pack_model_config_ui(modelcfg_fr, selected_model, selected_profile)
        self._create_label_option_menu_pair(frame, "Model", avail_models, selected_model, save_model, current_model)
        
        def reset_config():
            selected_model.set(selected_profile.model)
            if selected_profile.model == "tesseract":
                selected_profile.model_config = core.ocrmodel.TesseractModel().config
            elif selected_model == "paddleocr":
                selected_profile.model_config = core.ocrmodel.OCRModel().config
            else:
                selected_profile.model_config = core.ocrmodel.OCRModel().config
            selected_profile.update()
            self._cancel_changes_queue()
            self._pack_model_config_ui(modelcfg_fr, selected_model, selected_profile)
        self._create_label_button_pair(frame, "", "Reset Config", command=reset_config)

        # model config
        modelcfg_fr.pack(side="top", fill=tk.BOTH, expand=True)
        self._pack_model_config_ui(modelcfg_fr, selected_model, selected_profile)
        
    def _pack_model_config_ui(self, frame, selected_model, selected_profile: core.profile.Profile):
        self._clear_frame(frame)

        if selected_model.get() == "tesseract":
            # tesseract path
            tesseract_path = tk.StringVar(frame, selected_profile.model_config["root_dir"])
            def change_path():
                def save_chang():
                    selected_profile.model_config["root_dir"] = tesseract_path.get()
                    selected_profile.update()
                self._queue_changes(save_chang)
            self._create_label_entry_pair(frame, "Tesseract Path", tesseract_path, change_path, width=50)
            
            # tesseract exec
            tesseract_exec = tk.StringVar(frame, selected_profile.model_config["exec"])
            def change_exec():
                def save_chang():
                    selected_profile.model_config["exec"] = tesseract_exec.get()
                    selected_profile.update()
                self._queue_changes(save_chang)
            self._create_label_entry_pair(frame, "Tesseract Executable", tesseract_exec, change_exec, width=50)
            
            # tesseract input
            tesseract_input = tk.StringVar(frame, selected_profile.model_config["input"])
            def change_input():
                def save_chang():
                    selected_profile.model_config["input"] = tesseract_input.get()
                    selected_profile.update()
                self._queue_changes(save_chang)
            self._create_label_entry_pair(frame, "Image Input", tesseract_input, change_input, width=50)

            # language
            current_lang = selected_profile.model_config["lang"]
            selected_lang = tk.StringVar(frame)
            avail_langs = core.ocrmodel.TesseractModel(selected_profile.model_config).get_available_langs()
            avail_langs = [ i.split(".")[0] for i in avail_langs ]
            def save_model():
                def save_chang():
                    selected_profile.model_config["lang"] = selected_lang.get()
                    selected_profile.update()
                self._queue_changes(save_chang)
            self._create_label_option_menu_pair(frame, "Language", avail_langs, selected_lang, save_model, current_lang)
        
        elif selected_model.get() == "paddleocr":
            # language
            current_lang = selected_profile.model_config["lang"]
            selected_lang = tk.StringVar(frame)
            avail_langs = ["en", "ch", "chinese_cht", "japan", "korean", "id"]
            def save_model():
                def save_chang():
                    selected_profile.model_config["lang"] = selected_lang.get()
                    selected_profile.update()
                self._queue_changes(save_chang)
            self._create_label_option_menu_pair(frame, "Language", avail_langs, selected_lang, save_model, current_lang)

    @staticmethod
    def _create_label_button_pair(root, label, buttontxt, command):
        frame = tk.Frame(root)
        label = tk.Label(frame, text=label)
        btn = tk.Button(frame, text=buttontxt, width=10, command=command)
        label.pack(side="left")
        btn.pack(side="right")
        frame.pack(side="top", anchor="n", fill=tk.X)

    @staticmethod
    def _create_label_entry_pair(root, label, variable, command, width=30):
        frame = tk.Frame(root)
        label = tk.Label(frame, text=label)
        variable.trace_add("write", lambda *_args: command())
        btn = tk.Entry(frame, textvariable=variable, width=width)
        label.pack(side="left")
        btn.pack(side="right")
        frame.pack(side="top", anchor="n", fill=tk.X)
        
    @staticmethod
    def _create_label_option_menu_pair(root, label, options, variable, command, selected_option=None):
        frame = tk.Frame(root)
        label = tk.Label(frame, text=label)
        variable.set(selected_option)
        variable.trace_add("write", lambda *_args: command())
        opts = tk.OptionMenu(frame, variable, *options)
        label.pack(side="left")
        opts.pack(side="right")
        frame.pack(side="top", anchor="n", fill=tk.X)
            
    @staticmethod
    def _create_label_checkbutton_pair(root, label, variable, command):
        frame = tk.Frame(root)
        label = tk.Label(frame, text=label)
        chkbtn = tk.Checkbutton(frame, variable=variable, onvalue=1, offvalue=0, command=command)
        label.pack(side="left")
        chkbtn.pack(side="right")
        frame.pack(side="top", anchor="n", fill=tk.X)

    @staticmethod
    def _clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()
        print("Setting window closed")

def run(ctx):
    s = SettingsWin(ctx)
    s.run()

def main(ctx: core.context.MainContext):
    proc = None
    def run_settings(ctx):
        nonlocal proc
        main_queue_msg = ctx.signal.value
        if main_queue_msg == core.context.SignalState.OPEN_SETTINGS:
            if proc == None or not proc.is_alive():
                print("Running the settings window")
                proc = multiprocessing.Process(target=run, args=(ctx,))
                proc.start()
            else:
                print("Window settings already opened")
            return True
        if main_queue_msg == core.context.SignalState.QUIT:
            if proc != None and (proc or proc.is_alive()):
                proc.terminate()
            return False
        return True
    ctx.watch_signal(run_settings)