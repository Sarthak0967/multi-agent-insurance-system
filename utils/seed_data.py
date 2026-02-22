from utils.db import get_connection

policies = [
    ("LIC Jeevan Anand", "LIC"),
    ("LIC Tech Term", "LIC"),
    ("HDFC Life Click 2 Protect", "HDFC Life"),
    ("ICICI Pru iProtect Smart", "ICICI Prudential"),
    ("SBI Life eShield", "SBI Life")
]

conn = get_connection()
cur = conn.cursor()

for policy in policies:
    try:
        cur.execute(
            "INSERT INTO policies (name, provider) VALUES (%s, %s)",
            policy
        )
    except:
        pass  # ignore duplicates

conn.commit()
cur.close()
conn.close()

print("Policies inserted!")