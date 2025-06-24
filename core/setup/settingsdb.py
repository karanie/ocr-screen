import sqlite3

DB_CONNECTION = "settings.db"

def setup_tables(con):
    cur = con.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY)
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS profiles(
                    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    is_enabled BOOLEAN,
                    hotkey TEXT,
                    mode TEXT,
                    model TEXT,
                    model_config TEXT,
                    FOREIGN KEY (username) REFERENCES user(username)
                )
                """)
    con.commit()

def seed_tables(con):
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO users(username) VALUES ('default')")
        cur.execute("""
                    INSERT INTO profiles(profile_id, username, is_enabled, hotkey, mode, model, model_config)
                    VALUES (1, 'default', TRUE, 'windows+f2', "selection", "tesseract", json('{}'))
                    """)
        con.commit()
    except sqlite3.IntegrityError:
        print("Tables already seeded")

import core.user
def set_default_user():
    core.user.User.get_active_user()

def get_tables(con):
    cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return res.fetchall()

def get_users(con):
    cur = con.cursor()
    res = cur.execute("SELECT * FROM users")
    return res.fetchall()

def get_profiles(con):
    cur = con.cursor()
    res = cur.execute("SELECT * FROM profiles")
    return res.fetchall()

def verify_db(con):
    table_validation_list = ("users", "profiles")
    table_list = get_tables(con)
    for i in table_validation_list:
        if tuple([i]) not in table_list:
            return False
    
    users_list = get_users(con)
    profiles_list = get_profiles(con)
    if not (users_list and profiles_list):
        return False
    
    return True

def setup_settingsdb():
    con = sqlite3.connect(DB_CONNECTION)
    setup_tables(con)
    seed_tables(con)
    set_default_user()
    print("All tables created and verified" if verify_db(con) else "Failed to create all or one of the tables")
    con.close()