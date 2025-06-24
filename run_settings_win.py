import json
import sqlite3

DB_CONNECTION = "settings.db"

if __name__ == "__main__":
    con = sqlite3.connect(DB_CONNECTION)
    cur = con.cursor()
    cur.execute("""
                INSERT INTO profiles(profile_id, username, is_enabled, hotkey, mode, model, model_config)
                VALUES (?, 'default', TRUE, 'win+F2', "selection", "tesseract", json(?))
                """, [None, json.dumps({"amog": "gus"})])
    con.commit()
    
    res = cur.execute("""
            SELECT * FROM profiles
            """).fetchall()
    print(res)