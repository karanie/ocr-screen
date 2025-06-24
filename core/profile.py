import json
import sqlite3
import core

DB_CONNECTION = "settings.db"

def _zip_cols_vals(cols, vals):
    zipped = []
    for pidx, i in enumerate(vals):
        for cidx, c in enumerate(cols):
            try:
                zipped[pidx]
            except:
                zipped.append({})
            zipped[pidx][c] = i[cidx]
    return zipped

class Profile():
    # It's not possible to overload the constructor in python
    # def __init__(self, username: str, mode: str, model: str, model_config: dict, hotkey: str = None, is_enabled: bool = False, profile_id: int=None):
    #     self.is_enabled = is_enabled
    #     self.username = username
    #     self.profile_id = profile_id
    #     self.hotkey = hotkey
    #     self.mode = mode
    #     self.model = model
    #     self.model_config = model_config
    #     if self.model == "tesseract" and self.model_config == {}:
    #         self.model_config = core.ocrmodel.TesseractModel(self.model_config).config
    
    def __init__(self, profile: dict | str):
        if type(profile) == str:
            profile = json.loads(profile)
        else:
            profile = json.loads(json.dumps(profile))
        profile.setdefault("profile_id", None)
        profile.setdefault("hotkey", None)
        profile.setdefault("is_enabled", False)
        self.profile_id = profile["profile_id"]
        self.username = profile["username"]
        self.is_enabled = profile["is_enabled"]
        self.hotkey = profile["hotkey"]
        self.mode = profile["mode"]
        self.model = profile["model"]
        self.model_config = {} if profile["model_config"] == "{}" else json.loads(profile["model_config"])
        if self.model == "tesseract" and self.model_config == {}:
            self.model_config = core.ocrmodel.TesseractModel(self.model_config).config

    @staticmethod
    def get_profiles():
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        profiles = cur.execute("SELECT * FROM profiles").fetchall()
        cols = [ i[0] for i in cur.description ]
        profiles = [ Profile(p) for p in _zip_cols_vals(cols, profiles) ]
        return profiles
    
    @staticmethod
    def from_username(username, all=False):
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        if all:
            profiles = cur.execute("SELECT * FROM profiles WHERE username = ?", [username]).fetchall()
        else:
            profiles = cur.execute("SELECT * FROM profiles WHERE username = ? and is_enabled = True", [username]).fetchall()
        cols = [ i[0] for i in cur.description ]
        profiles = [ Profile(p) for p in _zip_cols_vals(cols, profiles) ]
        return profiles
    
    @staticmethod
    def get_profile(id):
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        profiles = cur.execute("SELECT * FROM profiles WHERE profile_id = ?", [id]).fetchall()
        cols = [ i[0] for i in cur.description ]
        profiles = [ Profile(p) for p in _zip_cols_vals(cols, profiles) ]
        return profiles[0]
    
    def set_defaults(self, username="default"):
        self.profile_id = None
        self.username = username
        self.is_enabled = False
        self.hotkey = None
        self.mode = "selection"
        self.model = "tesseract"
        self.model_config = core.ocrmodel.TesseractModel().config

    def new_profile(self):
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        cur.execute("""
                    INSERT INTO profiles(username, is_enabled, hotkey, mode, model, model_config)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [self.username, self.is_enabled, self.hotkey, self.mode, self.model, json.dumps(self.model_config)])
        con.commit()
        self.profile_id = cur.lastrowid

    def update(self):
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        cur.execute("""
                    UPDATE profiles
                    SET 
                    profile_id = ?,
                    username = ?,
                    is_enabled = ?,
                    hotkey = ?,
                    mode = ?,
                    model = ?,
                    model_config = json(?)
                    WHERE profile_id = ?
                    """,
                    [self.profile_id, self.username, self.is_enabled, self.hotkey, self.mode, self.model, json.dumps(self.model_config), self.profile_id])
        con.commit()
    
    def delete(self):
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        cur.execute("""
                    DELETE FROM profiles WHERE profile_id = ?
                    """,
                    [self.profile_id])
        con.commit()
