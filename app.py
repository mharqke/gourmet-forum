from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash # Added check_password_hash
from datetime import datetime
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database Configuration (as provided in structure.txt)
db_config = {
    'host': os.environ.get('DB_HOST'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD')
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- LOGIN LOGIC ---
@app.route('/login_user', methods=['POST'])
def login_user():
    # 'identifier' matches the 'name' attribute in our HTML input
    identifier = request.form.get('identifier') 
    password = request.form.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Search by username OR email
    query = "SELECT * FROM users WHERE username = %s OR email = %s"
    cursor.execute(query, (identifier, identifier))
    user = cursor.fetchone()
    conn.close()

    # Verify user exists and password is correct
    if user and check_password_hash(user['password_hash'], password):
        # Create a session to keep the user logged in
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/index.html')
    else:
        # Send an error message back to the login page
        flash('Неверное имя пользователя или пароль', 'error')
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
        # Using Python datetime
        current_time = datetime.now()
        query = "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username, email, hashed_pw, current_time))
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

    # 1. Fetch User Data
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    # 2) Count Likes, Posts, Comments, Subscribers
    cursor.execute("SELECT COUNT(*) as count FROM posts WHERE author_id = %s", (user_id,))
    post_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM comments WHERE user_id = %s", (user_id,))
    comment_count = cursor.fetchone()['count']



   
    # 2. Fetch "My Posts" with Comment Count, Like Count, and Tags
    # We use LEFT JOINs so we don't lose posts that have 0 likes/comments
    cursor.execute("""
        SELECT p.*, 
               COUNT(DISTINCT c.id) as comment_count, 
               COUNT(*) as like_count,
               GROUP_CONCAT(DISTINCT t.name) as tags
        FROM posts p
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN post_reactions l ON p.id = l.post_id
        LEFT JOIN thread_tags pt ON p.id = pt.post_id
        LEFT JOIN tags t ON pt.tag_id = t.id
        WHERE p.author_id = %s
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """, (user_id,))
    my_posts = cursor.fetchall()

    # 3. Fetch "Liked Posts" with their specific counts
    cursor.execute("""
        SELECT p.*, 
               username as author,
               COUNT(DISTINCT c.id) as comment_count, 
               COUNT(*) as like_count
        FROM posts p
        JOIN post_reactions l ON p.id = l.post_id
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN post_reactions l2 ON p.id = l2.post_id
        LEFT JOIN users u ON u.id = p.author_id
        WHERE l.user_id = %s
        GROUP BY p.id
    """, (user_id,))
    liked_posts = cursor.fetchall()
    
    conn.close()
    return render_template('profile.html', 
                           posts=my_posts, 
                           user=user_data, 
                           post_count=post_count, 
                           liked_posts=liked_posts,
                           comment_count=comment_count,
                           )

# 4. Route to Delete Post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session: return redirect('/login.html')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ensure the user deleting the post is the actual author
    cursor.execute("DELETE FROM posts WHERE id = %s AND author_id = %s", (post_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Post deleted successfully')
    return redirect('/profile.html')

# 5. Route to Change Password
@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session: return redirect('/login.html')
    
    current_pw = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT password_hash FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    if user and check_password_hash(user['password_hash'], current_pw):
        hashed_pw = generate_password_hash(new_pw)
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_pw, session['user_id']))
        conn.commit()
        flash('Password updated successfully!', 'success')
    else:
        flash('Incorrect current password', 'error')
    
    conn.close()
    return redirect('/profile.html')


# Add these imports if not present
from flask import Flask, render_template, request, redirect, session, flash

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect('/login.html')

    # Get data from the form
    title = request.form.get('title')
    content = request.form.get('content')
    category_name = request.form.get('category')  # Changed from subcategory
    tags_raw = request.form.get('tags')
    author_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Find the Category ID based on the name selected in the dropdown
        cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
        cat_result = cursor.fetchone()
        
        # If the category doesn't exist in DB, you might want to create it or set a default
        category_id = cat_result['id'] if cat_result else None

        # 2. Insert the Post
        cursor.execute("""
            INSERT INTO posts (author_id, category_id, title, content, created_at, status)
            VALUES (%s, %s, %s, %s, NOW(), 'published')
        """, (author_id, category_id, title, content))
        
        post_id = cursor.lastrowid

        # 3. Process Tags (Ensuring Many-to-Many relationship)
        if tags_raw:
            tag_list = [t.strip().lower() for t in tags_raw.split(',') if t.strip()]
            for tag_name in tag_list:
                # Get or Create Tag
                cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
                tag_row = cursor.fetchone()
                
                if tag_row:
                    tag_id = tag_row['id']
                else:
                    cursor.execute("INSERT INTO tags (name) VALUES (%s)", (tag_name,))
                    tag_id = cursor.lastrowid
                
                # Link Post to Tag
                cursor.execute("""
                    INSERT IGNORE INTO thread_tags (post_id, tag_id, created_at)
                    VALUES (%s, %s, NOW())
                """, (post_id, tag_id))

        conn.commit()
        flash('Пост успешно создан!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Ошибка при создании поста: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect('/index.html')


@app.route('/topic/<int:post_id>')
def view_topic(post_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Fetch Post Details, Author, and Category
    cursor.execute("""
        SELECT p.*, u.username as author_name, c.name as category_name,
               (SELECT COUNT(*) FROM post_reactions WHERE post_id = p.id) as like_count
        FROM posts p
        JOIN users u ON p.author_id = u.id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s
    """, (post_id,))
    post = cursor.fetchone()

    if not post:
        conn.close()
        return "Post not found", 404

    # 2. Check if current user has liked this post
    user_has_liked = False
    if 'user_id' in session:
        cursor.execute("SELECT 1 FROM post_reactions WHERE post_id = %s AND user_id = %s", 
                       (post_id, session['user_id']))
        user_has_liked = cursor.fetchone() is not None

    # 3. Fetch Tags for this post
    cursor.execute("""
        SELECT t.name FROM tags t
        JOIN thread_tags tt ON t.id = tt.tag_id
        WHERE tt.post_id = %s
    """, (post_id,))
    tags = cursor.fetchall()

    # 4. Fetch Comments with Author Usernames
    cursor.execute("""
        SELECT cm.*, u.username as author_name 
        FROM comments cm
        JOIN users u ON cm.user_id = u.id
        WHERE cm.post_id = %s
        ORDER BY cm.created_at ASC
    """, (post_id,))
    comments = cursor.fetchall()

    conn.close()
    return render_template('topic.html', 
                           post=post, 
                           tags=tags, 
                           comments=comments, 
                           user_has_liked=user_has_liked)

# --- Action Routes ---

@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('serve_page', page='login.html'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # INSERT IGNORE ensures we don't like twice (primary key constraint)
    cursor.execute("INSERT IGNORE INTO post_reactions (user_id, post_id, reaction, created_at) VALUES (%s, %s, 1, NOW())", 
                   (session['user_id'], post_id))
    conn.commit()
    conn.close()
    return redirect(url_for('view_topic', post_id=post_id))

@app.route('/post_comment/<int:post_id>', methods=['POST'])
def post_comment(post_id):
    if 'user_id' not in session:
        flash('Вы должны войти, чтобы оставить комментарий', 'error')
        return redirect(url_for('serve_page', page='login.html'))

    body = request.form.get('comment_body')
    user_id = session['user_id']

    if not body or body.strip() == "":
        flash('Комментарий не может быть пустым', 'error')
        return redirect(url_for('view_topic', post_id=post_id))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Matches the 'comments' table structure in your init.sql
        cursor.execute("""
            INSERT INTO comments (post_id, user_id, body, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (post_id, user_id, body))
        conn.commit()
        flash('Комментарий добавлен!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Ошибка: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('view_topic', post_id=post_id))

# --- TAGS LIST ROUTE ---
@app.route('/tags')
def show_all_tags():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch tags and count how many posts are associated with each
    query = """
        SELECT t.id, t.name, COUNT(tt.post_id) as post_count 
        FROM tags t
        LEFT JOIN thread_tags tt ON t.id = tt.tag_id
        GROUP BY t.id, t.name
        ORDER BY post_count DESC
    """
    cursor.execute(query)
    all_tags = cursor.fetchall()
    conn.close()
    print('all_tags:',all_tags)
    return render_template('tags.html', tags=all_tags)

# --- SINGLE TAG VIEW ROUTE ---
@app.route('/tag/<int:tag_id>')
def show_tag_posts(tag_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Get the tag name for the header
    cursor.execute("SELECT name FROM tags WHERE id = %s", (tag_id,))
    tag = cursor.fetchone()
    
    if not tag:
        conn.close()
        return "Tag not found", 404

    # 2. Get all posts associated with this tag
    query = """
        SELECT p.*, u.username as author_name 
        FROM posts p
        JOIN users u ON p.author_id = u.id
        JOIN thread_tags tt ON p.id = tt.post_id
        WHERE tt.tag_id = %s
        ORDER BY p.created_at DESC
    """
    cursor.execute(query, (tag_id,))
    posts = cursor.fetchall()
    conn.close()

    return render_template('tag.html', tag_name=tag['name'], posts=posts)





# ---   TCH-ALL ROUTE ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<page>')
def serve_page(page):
    if page.endswith('.html'):
        return render_template(page, session=session)
    return render_template('index.html', session=session)

