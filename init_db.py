from database import init_db, connect_db

def insert_sample_data():
    with connect_db() as db:
        cursor = db.cursor()

        # Sample Chronicles
        cursor.execute("INSERT OR IGNORE INTO chronicles (title, author, status) VALUES (?, ?, ?)", ("The Whispering Peaks", "Anya Sharma", "Ongoing"))
        cursor.execute("INSERT OR IGNORE INTO chronicles (title, author, status) VALUES (?, ?, ?)", ("Echoes of the Forgotten Star", "Kaelen Thorne", "Completed"))
        cursor.execute("INSERT OR IGNORE INTO chronicles (title, author, status) VALUES (?, ?, ?)", ("Chronicles of the Azure Sky", "Lyra Vance", "Ongoing"))

        # Sample Archives
        cursor.execute("INSERT OR IGNORE INTO archives (name, url) VALUES (?, ?)", ("Starlight Archive", "https://starlight.example.com"))
        cursor.execute("INSERT OR IGNORE INTO archives (name, url) VALUES (?, ?)", ("Whisperwind Repository", "https://whisperwind.example.com"))

        # Sample Conduits
        cursor.execute("INSERT OR IGNORE INTO conduits (name, archive_id) VALUES (?, (SELECT id FROM archives WHERE name = ?))", ("Starlight Conduit Alpha", "Starlight Archive"))
        cursor.execute("INSERT OR IGNORE INTO conduits (name, archive_id) VALUES (?, (SELECT id FROM archives WHERE name = ?))", ("Whisperwind Conduit Beta", "Whisperwind Repository"))

        db.commit()

if __name__ == '__main__':
    init_db()
    insert_sample_data()
    print("Database initialized and populated with sample data.")
