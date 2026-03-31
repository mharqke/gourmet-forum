
@app.route('/profile.html', methods=['GET'])
def profile():


    # 1. Fetch User Data
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    # 2. Fetch "My Posts" with Comment Count, Like Count, and Tags
    # We use LEFT JOINs so we don't lose posts that have 0 likes/comments
    cursor.execute("""
        SELECT p.*, 
               COUNT(DISTINCT c.id) as comment_count, 
               COUNT(DISTINCT l.id) as like_count,
               GROUP_CONCAT(DISTINCT t.name) as tags
        FROM posts p
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN likes l ON p.id = l.post_id
        LEFT JOIN post_tags pt ON p.id = pt.post_id
        LEFT JOIN tags t ON pt.tag_id = t.id
        WHERE p.author_id = %s
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """, (user_id,))
    my_posts = cursor.fetchall()

    # 3. Fetch "Liked Posts" with their specific counts
    cursor.execute("""
        SELECT p.*, 
               COUNT(DISTINCT c.id) as comment_count, 
               COUNT(DISTINCT l2.id) as like_count
        FROM posts p
        JOIN likes l ON p.id = l.post_id
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN likes l2 ON p.id = l2.post_id
        WHERE l.user_id = %s
        GROUP BY p.id
    """, (user_id,))
    liked_posts = cursor.fetchall()

    conn.close()
    return render_template('profile.html', user=user_data, 
                           posts=my_posts, liked_posts=liked_posts)

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