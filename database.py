import sqlite3

def init_db():
    conn = sqlite3.connect('celestial_objects.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT
        )
    ''')
    c.execute("INSERT INTO objects (name, type, description) VALUES (?, ?, ?)",
              ('Andromeda Galaxy', 'Galaxy', 'A spiral galaxy approximately 2.537 million light-years from Earth.'))
    c.execute("INSERT INTO objects (name, type, description) VALUES (?, ?, ?)",
              ('Orion Nebula', 'Nebula', 'A diffuse nebula situated in the Milky Way, being south of Orion\'s Belt in the constellation of Orion.'))
    c.execute("INSERT INTO objects (name, type, description) VALUES (?, ?, ?)",
                ('Betelgeuse', 'Star', 'A red supergiant of spectral type M1-2 and one of the largest stars visible to the naked eye.'))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
