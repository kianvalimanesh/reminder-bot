
import mysql.connector
from config import db_config

def insert_user(cid, username):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO USERS (CID, USERNAME) VALUES (%s, %s)", (cid, username))
    conn.commit()
    conn.close()
    print(f"user data inserted with cid: {cid} successfully")

def insert_category(name):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO CATEGORIES (NAME) VALUES (%s)", (name,))
    cursor.execute("SELECT CATEGORY_ID FROM CATEGORIES WHERE NAME = %s", (name,))
    category_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    print(f"category data inserted with id: {category_id} successfully")
    return category_id

def insert_task(cid, category_name, title, description=None, status="In Progress"):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT CATEGORY_ID FROM CATEGORIES WHERE NAME = %s", (category_name,))
    category_id = cursor.fetchone()
    if not category_id:
        cursor.execute("INSERT INTO CATEGORIES (NAME) VALUES (%s)", (category_name,))
        category_id = cursor.lastrowid
    else:
        category_id = category_id[0]
    cursor.execute("INSERT INTO TASKS (USER_ID, CATEGORY_ID, TITLE, DESCRIPTION) VALUES (%s, %s, %s, %s)",
                   (cid, category_id, title, description))
    task_id = cursor.lastrowid
    cursor.execute("INSERT INTO TASK_STATUS (TASK_ID, STATUS) VALUES (%s, %s)", (task_id, status))
    conn.commit()
    conn.close()
    print(f"task data inserted with id: {task_id} successfully")
    return task_id

def insert_reminder(task_id, reminder_time):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO REMINDERS (TASK_ID, REMINDER_TIME) VALUES (%s, %s)", (task_id, reminder_time))
    conn.commit()
    conn.close()
    print(f"reminder data inserted for task id: {task_id} successfully")

def update_task_status(task_id, status):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO TASK_STATUS (TASK_ID, STATUS) VALUES (%s, %s)", (task_id, status))
    conn.commit()
    conn.close()
    print(f"task status updated for id: {task_id} successfully")

def delete_task(task_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TASKS WHERE TASK_ID = %s", (task_id,))
    conn.commit()
    conn.close()
    print(f"task data deleted with id: {task_id} successfully")

def update_report(cid):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM TASK_STATUS WHERE STATUS = 'Completed' AND TASK_ID IN (SELECT TASK_ID FROM TASKS WHERE USER_ID = %s)", (cid,))
    completed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM TASK_STATUS WHERE STATUS = 'In Progress' AND TASK_ID IN (SELECT TASK_ID FROM TASKS WHERE USER_ID = %s)", (cid,))
    pending = cursor.fetchone()[0]
    cursor.execute("REPLACE INTO REPORTS (USER_ID, COMPLETED_TASKS, PENDING_TASKS) VALUES (%s, %s, %s)", (cid, completed, pending))
    conn.commit()
    conn.close()
    print(f"report data updated for user id: {cid} successfully")

if __name__ == "__main__":
    insert_user(123, "testuser")
    category_id = insert_category("Study")
    task_id = insert_task(123, "Study", "Read book")
    insert_reminder(task_id, "2025-04-09 14:30:00")
    update_task_status(task_id, "Completed")
    update_report(123)
    # delete_task(task_id)
