from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            tag TEXT NOT NULL,
            views INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0
        )
    ''')
    
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM posts')
    if cursor.fetchone()[0] == 0:
        conn.execute('INSERT INTO posts (title, author, tag, views, replies) VALUES (?, ?, ?, ?, ?)',
                     ("หาตี้ลงดันเจี้ยนครับ ขาดแทงค์ 1 คน", "GamerX", "LFG", 150, 12))
        conn.execute('INSERT INTO posts (title, author, tag, views, replies) VALUES (?, ?, ?, ?, ?)',
                     ("[Guide] เทคนิคฟาร์มทองฉบับผู้เริ่มต้น", "NoobMaster", "Guide", 3200, 85))
                     
    conn.commit()
    conn.close()

init_db()


@app.route('/', methods=['GET', 'POST'])
def home():
    conn = get_db_connection()
    
    if request.method == 'POST':
        new_title = request.form.get('title')
        # ถ้าล็อกอินแล้วให้ใช้ชื่อ User ถ้ายังให้เป็น 'Anonymous'
        new_author = session.get('username', 'Anonymous') 
        new_tag = request.form.get('tag')
        
        if new_title:
            # ใช้คำสั่ง SQL INSERT ลงตาราง posts
            conn.execute('INSERT INTO posts (title, author, tag, views, replies) VALUES (?, ?, ?, ?, ?)',
                         (new_title, new_author, new_tag, 0, 0))
            conn.commit()
            
        conn.close()
        return redirect(url_for('home'))

    posts_data = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    

    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()
    
    return render_template('index.html', posts=posts_data, players=total_users)

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('ชื่อผู้ใช้นี้มีคนใช้งานแล้ว โปรดเลือกชื่ออื่น', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)