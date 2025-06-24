import keyboard
from core.profile import Profile

class HotkeyManager():
    def __init__(self):
        self._active_hotkeys = []

    def __delete__(self):
        self.unhook_all_hotkey()

    def register_profile_hotkey(self, profile: Profile, func):
        if not profile.hotkey:
            return
        if len(self._active_hotkeys) != 0:
            a_htk, a_prf = zip(*self._active_hotkeys)
            a_htk = list(a_htk)
            a_prf = list(a_prf)
            if profile.hotkey in a_htk:
                profile_yang_duluan_masuk = a_prf[a_htk.index(profile.hotkey)]
                raise Exception(f"Profile {profile.profile_id}'s hotkey ({profile.hotkey}) already registered by profile {profile_yang_duluan_masuk}")
        self._active_hotkeys.append((profile.hotkey, profile.profile_id))
        keyboard.add_hotkey(profile.hotkey, func)

    def unhook_all_hotkey(self):
        try:
            keyboard.unhook_all_hotkeys()
        except AttributeError:
            pass
        self._active_hotkeys = []
    
    def wait(self):
        keyboard.wait()