import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def validate_policy(user_input):
    normalized_input = user_input.strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM policies WHERE LOWER(name) = %s",
        (normalized_input,)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else None


def get_all_policies():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM policies ORDER BY name")
    policies = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return policies