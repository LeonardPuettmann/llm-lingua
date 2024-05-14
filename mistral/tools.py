import sqlite3
import random

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('./database/vocabulary.db')
    except sqlite3.Error as e:
        print(e)
    return conn

def check_words(input_string):
    words = set(input_string.split(" "))
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM dictionary")
    db_words = set([row[0] for row in cursor])
    italian_words = words & db_words

    for word in italian_words:
        cursor.execute("UPDATE dictionary SET covered = 'yes' WHERE word = ?", (word,))

    conn.commit()
    return len(italian_words)

def get_definition(word):
    print(f"Looking up definition for '{word}'")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT definition FROM dictionary WHERE word = ?", (word,))
        result = cursor.fetchone()
        print(f"Result: {result}")

        if result:
            return f"Results from the italian dictionary: {result[0]}"
        else:
            return f"Word '{word}' not found in database"
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None
    
def get_random_word():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, word
        FROM dictionary
        ORDER BY RANDOM()
        LIMIT 1;
    """)
    row = cursor.fetchone()

    if not row:
        return None

    idx, word = row
    cursor.execute("""
        UPDATE dictionary
        SET covered = 'yes'
        WHERE id = ?;
    """, (idx,))

    conn.commit()
    return f"Retrieved word for italian vocab training: {word}"

conn = create_connection()