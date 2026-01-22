import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def create_tables():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            create_players_table = """
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                balance INT DEFAULT 1000,
                wins INT DEFAULT 0 
            );
            """
            cur.execute(create_players_table)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error creating tables: {e}")

def add_player(username):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:

                sql = "INSERT INTO players (username) VALUES (%s) RETURNING id;"
                cur.execute(sql, (username,))

                new_id = cur.fetchone()[0]
                conn.commit()
                print(f"Added player {username} to database with id {new_id}")
                return new_id

        except psycopg.errors.UniqueViolation:
            print(f"Username {username} already exists")
            conn.rollback()
            return None

        except Exception as e:
            print(f"Error adding player: {e}")
            return None

        finally:
            conn.close()

def get_player_data(username):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                sql = "SELECT balance, wins FROM players WHERE username = %s;"
                cur.execute(sql, (username,))

                result = cur.fetchone()

                if result:
                    balance = result[0]
                    wins = result[1]
                    return balance, wins
                else:
                    return None, None
        except Exception as e:
            print(f"Error getting player: {e}")
            return None
        finally:
            conn.close()
def update_balance(username, new_balance):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                sql = "UPDATE players SET balance = %s WHERE username = %s;"
                cur.execute(sql, (new_balance, username))
                conn.commit()

        except Exception as e:
            print(f"Error updating player: {e}")
        finally:
            conn.close()

def update_win_count(username, win_count):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                sql = "UPDATE players SET wins = %s WHERE username = %s;"
                cur.execute(sql, (win_count, username,))
                conn.commit()
        except Exception as e:
            print(f"Error updating player: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    create_tables()
