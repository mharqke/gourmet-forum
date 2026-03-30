from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash # Added check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database Configuration (as provided in structure.txt)
db_config = {
    "host": "sql7.freesqldatabase.com",
    "user": "sql7821169",
    "password": "Xv2uvZTRyU",
    "database": "sql7821169"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- LOGIN LOGIC ---
@app.route('/login_user', methods=['POST'])
def login_user():
    identifier = request.form.get('identifier') # Can be username or email
    password = request.form.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Search for user by username OR email (based on your init.sql structure)
    query = "SELECT * FROM users WHERE username = %s OR email = %s;"
    cursor.execute(query, (identifier, identifier))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        # Store user info in Flask session
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f'Welcome back, {user["username"]}!', 'success')
        return redirect('/index.html')
    else:
        flash('Invalid username/email or password', 'error')
        return redirect('/login.html')

# --- REGISTRATION LOGIC ---
@app.route('/register_user', methods=['POST'])
def register_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    if cursor.fetchone():
        flash('Username or Email already exists!', 'error')
        conn.close()
        return redirect('/register.html')

    hashed_pw = generate_password_hash(password)
    try:
        query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, hashed_pw))
        conn.commit()
        flash('Registration successful! Please log in.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect('/login.html')

@app.route('/profile.html', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login.html')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    user_id = session['user_id']

    # 4) Handle Profile Updates (Username, Bio, City)
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_bio = request.form.get('bio')
        new_city = request.form.get('city')
        
        cursor.execute("""
            UPDATE users SET username = %s, bio = %s, city = %s WHERE id = %s
        """, (new_username, new_bio, new_city, user_id))
        conn.commit()
        session['username'] = new_username # Update session name
        flash('Profile updated successfully!')

    # 1) Fetch User Data (Name, City, Bio, Created_at)
    cursor.execute("SELECT username, email, city, bio, created_at FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    # 2) Count Likes, Posts, Comments, Subscribers
    cursor.execute("SELECT COUNT(*) as count FROM posts WHERE author_id = %s", (user_id,))
    post_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM comments WHERE author_id = %s", (user_id,))
    comment_count = cursor.fetchone()['count']

    # 3) Fetch Lists: User's Posts, Liked Posts, and Subscribers
    # Your posts
    cursor.execute("SELECT category, title, content, created_at FROM posts WHERE author_id = %s ORDER BY created_at DESC", (user_id,))
    user_posts = cursor.fetchall()

    # Liked posts (Joining likes table with posts table)
    cursor.execute("""
        SELECT p.title, p.category, p.created_at 
        FROM posts p 
        JOIN likes l ON p.id = l.post_id 
        WHERE l.user_id = %s
    """, (user_id,))
    liked_posts = cursor.fetchall()

    # Liked posts amount
    cursor.execute("""
        SELECT COUNT(*)
        FROM posts p 
        JOIN likes l ON p.id = l.post_id 
        WHERE l.user_id = %s
    """, (user_id,))
    liked_posts_amount = cursor.fetchall()

    conn.close()
    return render_template('profile.html', 
                           user=user_data, 
                           post_count=post_count, 
                           comment_count=comment_count,
                           posts=user_posts,
                           liked_posts=liked_posts,
                           liked_posts_amount=liked_posts_amount
                           )

# --- CATCH-ALL ROUTE ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<page>')
def serve_page(page):
    if page.endswith('.html'):
        # Pass session data to templates so they know if a user is logged in
        return render_template(page, session=session)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)