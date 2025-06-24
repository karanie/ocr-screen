import sqlite3
import json
import core
import core.profile

DB_CONNECTION = "settings.db"

class User():
    def __init__(self, username: str):
        self.username = username

    @staticmethod
    def get_active_user():
        try:
            with open("./active_user", "r") as f:
                active_user = f.read()
            return User(active_user)
        except FileNotFoundError:
            u = User("default")
            u.set_active()
            return u
        
    @staticmethod
    def get_users():
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM users").fetchall()
        return [ User(u[0]) for u in res ]
        
    @staticmethod
    def create_user(username: str):
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        cur.execute("INSERT INTO users(username) VALUES (?)", [username])
        con.commit()
        
    @staticmethod
    def delete_user(username: str):
        if username == "default":
            raise Exception("Cannot delete default user")
        con = sqlite3.connect(DB_CONNECTION)
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE username = ?", [username])
        con.commit()

    def is_active(self):
        try:
            with open("./active_user", "r") as f:
                active_user = f.read()
            return active_user == self.username
        except FileNotFoundError:
            return False
    
    def set_active(self):
        with open("./active_user", "w+") as f:
            active_user = f.write(self.username)

    def get_profiles(self, all=False):
        return core.profile.Profile.from_username(self.username, all)
    
    def new_profile(self):
        model_config = core.ocrmodel.TesseractModel().config
        p = core.profile.Profile({
            "username": self.username,
            "hotkey": None,
            "mode": "selection",
            "model": "tesseract",
            "model_config": json.dumps(model_config),
        })
        p.new_profile()
        return p

