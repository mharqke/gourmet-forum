# First install: pip install mysql-connector-python

import mysql.connector
from mysql.connector import Error

# Database configuration
db_config = {
    'host': 'sql7.freesqldatabase.com',
    'user': 'sql7821821',
    'password': 'GVS4YmlnQD',
    'database': 'sql7821821',
    'port': 3306
}

def create_table():
    """Create users table if it doesn't exist"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'users' created successfully")
        
    except Error as e:
        print(f"Error: {e}")
        return
    cursor.close()
    connection.close()

def add_user(username, email, password_hash):
    """Add a new user to the database"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO users (username, email, password_hash) 
        VALUES (%s, %s, %s)
        """
        user_data = (username, email, password_hash)
        cursor.execute(insert_query, user_data)
        connection.commit()
        
        print(f"User '{username}' added successfully! ID: {cursor.lastrowid}")
        
    except Error as e:
        print(f"Error adding user: {e}")
        return
    cursor.close()
    connection.close()

def read_users():
    """Read and display all users"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        select_query = "SELECT id, username, email, password_hash, created_at FROM users"
        cursor.execute(select_query)
        users = cursor.fetchall()
        
        if users:
            print("\n--- Users List ---")
            for user in users:
                print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, "
                      f"Password Hash: {user[3][:20]}..., Created: {user[4]}")
        else:
            print("No users found")
        
        return users
        
    except Error as e:
        print(f"Error reading users: {e}")
        return
    cursor.close()
    connection.close()

# Example usage
if __name__ == "__main__":
    # Create table first
    create_table()
    
    # Add users
    add_user("john_doe", "john@example.com", "hashed_password_123")
    add_user("jane_smith", "jane@example.com", "hashed_password_456")
    
    # Read all users
    read_users()