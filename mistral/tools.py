import sqlite3

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('./database/vocabulary.db')
    except sqlite3.Error as e:
        print(e)
    return conn

def check_words(input_string):
    # Tokenize the input string into words
    words = set(input_string.split(" "))

    # Create a cursor and execute a query to retrieve the words from the database
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM dictionary")
    db_words = set([row[0] for row in cursor])

    # Find the intersection of the input words and the database words
    italian_words = words & db_words

    # Update the 'covered' column for the matching words
    for word in italian_words:
        cursor.execute("UPDATE dictionary SET covered = 'yes' WHERE word = ?", (word,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Return the number of Italian words found
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

conn = create_connection()