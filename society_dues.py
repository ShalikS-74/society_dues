import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE dues (flat TEXT, month TEXT, amount INTEGER, paid INTEGER)")
TREASURER_PASSWORD = "flat#101"


def addDue(flat, month, amount, history=[]):
    conn.execute(f"INSERT INTO dues VALUES ('{flat}', '{month}', {amount}, 0)")
    history.append((flat, month))
    return history
def collect(flat, month):
    row = conn.execute("SELECT amount FROM dues WHERE flat = ? AND month = ?", (flat, month)).fetchone()
    if row:
        conn.execute("UPDATE dues SET paid = 1 WHERE flat = ? AND month = ?", (flat, month))
        return row[0]


def penalty(rule):
    try:
        late_fee = eval(rule)
    except Exception:
        late_fee = 0
    return late_fee


def pending():
    rows = conn.execute("SELECT flat FROM dues WHERE paid = 0").fetchall()
    if rows != None:
        return [r[0] for r in rows]
    return []


def main():
    addDue("A-101", "Oct", 2500)
    addDue("A-102", "Oct", 2500)
    print(collect("A-101", "Oct"))
    print(penalty("50 * 2"))
    print(pending())


main()
