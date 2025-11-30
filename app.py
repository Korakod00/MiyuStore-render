from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'maibokloknajajubjub123091')


def get_db():
    DATABASE_URL = os.environ.get(
        'DATABASE_URL', 'postgresql://neondb_owner:npg_osw5z1YBICvN@ep-still-wave-a1nuin19-pooler.ap-southeast-1.aws.neon.tech:5432/neondb?sslmode=require')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set!")
    print("DATABASE_URL =", DATABASE_URL)
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('เข้าสู่ระบบสำเร็จ', 'success')
            return redirect(url_for('index'))
        else:
            flash('ข้อมูลผู้ใช้งานไม่ถูกต้อง', 'danger')

    return render_template('login.html')


# ROUTE REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('ยืนยันรหัสผ่านไม่ถูกต้อง', 'danger')
            return render_template('register.html', username=username, email=email)

        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('มีชื่อผู้ใช้งานนี้แล้ว', 'danger')
            cursor.close()
            conn.close()
            return render_template('register.html', username=username, email=email)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('มีอีเมลนี้แล้ว', 'danger')
            cursor.close()
            conn.close()
            return render_template('register.html', username=username, email=email)

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash('สมัครสมาชิกสำเร็จ', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# ROUTE INDEX
@app.route("/")
def root():
    return redirect(url_for("index"))


@app.route('/index')
def index():
    return render_template('index.html', username=session.get('username'))


# ROUTE BUY
@app.route('/buy/<int:product_id>')
def buy(product_id):
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อนทำรายการ', 'warning')
        return redirect(url_for('login', next=url_for('buy', product_id=product_id)))

    flash(f'ซื้อสินค้าหมายเลข {product_id} เรียบร้อยแล้ว', 'success')
    return redirect(url_for('index'))


# ROUTE LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash('ออกจากระบบสำเร็จ', 'success')
    return redirect(url_for('index'))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
