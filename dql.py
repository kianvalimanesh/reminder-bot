import mysql.connector
from config import db_config

def get_known_users():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT CID FROM USERS")
    result = cursor.fetchall()
    conn.close()
    return [i['CID'] for i in result]

def get_user(cid):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM USERS WHERE CID = %s", (cid,))
    result = cursor.fetchall()
    conn.close()
    return result[0] if result else {}

def get_categories():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CATEGORIES")
    result = cursor.fetchall()
    conn.close()
    return result

def get_tasks(cid):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.TASK_ID, t.TITLE, t.DESCRIPTION, c.NAME AS CATEGORY, ts.STATUS
        FROM TASKS t
        LEFT JOIN CATEGORIES c ON t.CATEGORY_ID = c.CATEGORY_ID
        LEFT JOIN TASK_STATUS ts ON t.TASK_ID = ts.TASK_ID
        WHERE t.USER_ID = %s
    """, (cid,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_active_reminders():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.REMINDER_ID, r.TASK_ID, r.REMINDER_TIME, t.USER_ID, t.TITLE
        FROM REMINDERS r
        JOIN TASKS t ON r.TASK_ID = t.TASK_ID
        WHERE r.REMINDER_TIME <= NOW()
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def get_report(cid):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM REPORTS WHERE USER_ID = %s", (cid,))
    result = cursor.fetchall()
    conn.close()
    return result[0] if result else {"COMPLETED_TASKS": 0, "PENDING_TASKS": 0}

if __name__ == "__main__":
    print("Known users:", get_known_users())
    print("User info:", get_user(123))
    print("Categories:", get_categories())
    print("Tasks for 123:", get_tasks(123))
    print("Active reminders:", get_active_reminders())
    print("Report for 123:", get_report(123))
