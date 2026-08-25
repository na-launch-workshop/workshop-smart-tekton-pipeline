import sqlite3


def greet(name="World"):
    return f"Hello, {name}!"


def get_user(username, db_path="app.db"):
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()
    finally:
        conn.close()


def main():
    print(greet())
    user_input = input("Enter username: ")
    try:
        user = get_user(user_input)
        print(f"Found: {user}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")


if __name__ == "__main__":
    main()