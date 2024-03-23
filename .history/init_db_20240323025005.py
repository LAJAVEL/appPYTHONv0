import sqlite3

# Connect to the database (it will be created if it does not exist)
conn = sqlite3.connect('forum.db')

# Create a cursor to execute SQL commands
c = conn.cursor()

# Create Tables
c.execute('''CREATE TABLE IF NOT EXISTS Utilisateurs (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS Posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Utilisateurs(user_id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS Réponses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (user_id) REFERENCES Utilisateurs(user_id)
)''')

# Validate the changes
conn.commit()

# Close the connection
conn.close()

print("Les tables ont été créées avec succès.")
