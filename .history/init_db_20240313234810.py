import sqlite3

# Connectez-vous à la base de données (elle sera créée si elle n'existe pas)
conn = sqlite3.connect('forum.db')

# Créer un curseur pour exécuter les commandes SQL
c = conn.cursor()

# Créer les tables
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

# Validez les changements
conn.commit()

# Fermez la connexion
conn.close()

print("Les tables ont été créées avec succès.")
