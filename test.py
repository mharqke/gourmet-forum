





print('hello world')

import mysql.connector
from werkzeug.security import generate_password_hash

password='123451254'
username='mark1'
email='mark1@gmail.com'

try:
    conn = mysql.connector.connect(
        host="sql7.freesqldatabase.com",
        user="sql7821169",
        password="Xv2uvZTRyU",
        database="sql7821169",
        port=3306
    )
    if conn.is_connected():
        print('Connected successfully!')
        
        cursor = conn.cursor()

        # cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        # existing_user = cursor.fetchone()

        # if existing_user:
        #     flash('Username or Email already exists!', 'error')
        #     conn.close()
        #     return redirect('/register.html')

        # 2. Hash password and insert into DB

        try:
            query = "INSERT INTO users (username, email, password_hash) VALUES ('laptop3', 'lap3@gmail.com', '87oad7fo8ad7fo8');"
            cursor.execute(query)
            conn.commit()
        except Exception as e:
            print(f'Error: {str(e)}', 'error')
        finally:
            conn.close()
        
except:
    print(f"Error while connecting to MySQL")
finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
