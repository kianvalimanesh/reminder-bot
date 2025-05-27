
import mysql.connector
from config import db_config

def create_database(database_name="KianBot"):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kianvalimanesh"
    )
    cursor = conn.cursor()
    cursor.execute(f'DROP DATABASE IF EXISTS {database_name}')
    cursor.execute(f'CREATE DATABASE IF NOT EXISTS {database_name}')
    conn.commit()
    conn.close()
    print(f'Database {database_name} created successfully')

def create_table_users():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE USERS (
            CID            BIGINT UNSIGNED NOT NULL PRIMARY KEY,
            USERNAME       VARCHAR(255) UNIQUE NOT NULL,
            CREATED_AT     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print('Table USERS created successfully!')

def create_table_categories():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE CATEGORIES (
            CATEGORY_ID    INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            NAME           VARCHAR(255) UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print('Table CATEGORIES created successfully!')

def create_table_tasks():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE TASKS (
            TASK_ID        INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            USER_ID        BIGINT UNSIGNED NOT NULL,
            CATEGORY_ID    INT UNSIGNED,
            TITLE          VARCHAR(255) NOT NULL,
            DESCRIPTION    TEXT,
            CREATED_AT     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (USER_ID) REFERENCES USERS(CID),
            FOREIGN KEY (CATEGORY_ID) REFERENCES CATEGORIES(CATEGORY_ID)
        )
    """)
    conn.commit()
    conn.close()
    print('Table TASKS created successfully!')

def create_table_task_priority():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE TASK_PRIORITY (
            TASK_ID        INT UNSIGNED NOT NULL PRIMARY KEY,
            PRIORITY       ENUM('High', 'Medium', 'Low') DEFAULT 'Medium',
            FOREIGN KEY (TASK_ID) REFERENCES TASKS(TASK_ID) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
    print('Table TASK_PRIORITY created successfully!')

def create_table_task_status():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE TASK_STATUS (
            TASK_ID        INT UNSIGNED NOT NULL PRIMARY KEY,
            STATUS         ENUM('In Progress', 'Completed') DEFAULT 'In Progress',
            FOREIGN KEY (TASK_ID) REFERENCES TASKS(TASK_ID) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
    print('Table TASK_STATUS created successfully!')

def create_table_task_due_dates():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE TASK_DUE_DATES (
            TASK_ID        INT UNSIGNED NOT NULL PRIMARY KEY,
            DUE_DATE       DATETIME NOT NULL,
            FOREIGN KEY (TASK_ID) REFERENCES TASKS(TASK_ID) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
    print('Table TASK_DUE_DATES created successfully!')

def create_table_reminders():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE REMINDERS (
            REMINDER_ID    INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            TASK_ID        INT UNSIGNED NOT NULL,
            REMINDER_TIME  DATETIME NOT NULL,
            FOREIGN KEY (TASK_ID) REFERENCES TASKS(TASK_ID) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
    print('Table REMINDERS created successfully!')

def create_table_reports():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE REPORTS (
            REPORT_ID      INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            USER_ID        BIGINT UNSIGNED NOT NULL,
            COMPLETED_TASKS INT DEFAULT 0,
            PENDING_TASKS  INT DEFAULT 0,
            LAST_UPDATED   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (USER_ID) REFERENCES USERS(CID)
        )
    """)
    conn.commit()
    conn.close()
    print('Table REPORTS created successfully!')

if __name__ == "__main__":
    create_database("KianBot")
    create_table_users()
    create_table_categories()
    create_table_tasks()
    create_table_task_priority()
    create_table_task_status()
    create_table_task_due_dates()
    create_table_reminders()
    create_table_reports()
