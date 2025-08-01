from database import init_db, connect_db
import os

CHRONICLES_CONTENT_DIR = './data/chronicles'

def insert_sample_data():
    os.makedirs(CHRONICLES_CONTENT_DIR, exist_ok=True)

    with connect_db() as db:
        cursor = db.cursor()

        # Sample Chronicles with content paths
        chronicles_data = [
            ("The Whispering Peaks", "Anya Sharma", "Ongoing", "whispering_peaks.txt", "Content for The Whispering Peaks. This is a sample chronicle."),
            ("Echoes of the Forgotten Star", "Kaelen Thorne", "Completed", "echoes_forgotten_star.txt", "Content for Echoes of the Forgotten Star. This chronicle is now complete."),
            ("Chronicles of the Azure Sky", "Lyra Vance", "Ongoing", "azure_sky.txt", "Content for Chronicles of the Azure Sky. More to come soon."),
        ]

        for title, author, status, filename, content_text in chronicles_data:
            content_path = os.path.join(CHRONICLES_CONTENT_DIR, filename)
            with open(content_path, 'w') as f:
                f.write(content_text)

            # Check if chronicle already exists
            cursor.execute("SELECT id FROM chronicles WHERE title = ?", (title,))
            existing_chronicle = cursor.fetchone()

            if existing_chronicle:
                # Update existing chronicle with content_path
                cursor.execute("UPDATE chronicles SET content_path = ? WHERE id = ?", (content_path, existing_chronicle[0]))
            else:
                # Insert new chronicle with content_path
                cursor.execute("INSERT INTO chronicles (title, author, status, content_path) VALUES (?, ?, ?, ?)", (title, author, status, content_path))

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