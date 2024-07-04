import mysql.connector


def init_db():
    # Initialize your database connection and tables here
    pass


def add_user(name, image_path, kelas, nim, created_at):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    cursor = conn.cursor()

    add_user_query = (
        "INSERT INTO users "
        "(name, image_path, kelas, nim, created_at) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    user_data = (name, image_path, kelas, nim, created_at)

    cursor.execute(add_user_query, user_data)
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id


def get_user_name_by_id(user_id):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    cursor = conn.cursor()

    query = "SELECT name FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


def get_all_users():
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    cursor = conn.cursor()

    query = "SELECT id, name, image_path FROM users"
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def get_user_id_by_name(name):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0]


def update_user_image_path(user_id, image_path):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET image_path = %s WHERE id = %s", (image_path, user_id)
    )
    conn.commit()
    conn.close()


def get_user_nim_by_id(user_id):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nim FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "Unknown"


def get_user_name_by_id(user_id):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "Unknown"


def add_presence(nim, nama):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    cursor = conn.cursor()
    query = "INSERT INTO presence (nim, nama, presensiPada) VALUES (%s, %s, NOW())"
    cursor.execute(query, (nim, nama))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_info_by_id(user_id):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT nim, name FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_user_image_path(user_id):
    conn = mysql.connector.connect(
        user="root", password="", host="localhost", database="db_pdm_presence"
    )
    cursor = conn.cursor()

    query = "SELECT image_path FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result[0] if result else None
