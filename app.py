from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "orphanage_management_secret"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'orphanage.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('intro'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/', methods=['GET', 'POST'])
def intro():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin['password_hash'], password):
            session['logged_in'] = True
            session['username'] = username
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password. Please try again.'

    return render_template('intro.html', error=error)



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('intro'))



@app.route('/home')
@login_required
def home():
    return render_template('index.html')



@app.route('/children')
@login_required
def children():
    conn = get_db_connection()
    children = conn.execute('''
        SELECT c.Ch_id, c.name, c.age, c.gender, c.health_status, c.admission_date,
               t.name AS caretaker_name
        FROM children c
        LEFT JOIN caretakers t ON c.caretaker_id = t.Ct_id
    ''').fetchall()
    conn.close()
    return render_template('children.html', children=children)



@app.route('/add_child', methods=['GET', 'POST'])
@login_required
def add_child():
    conn = get_db_connection()
    caretakers = conn.execute('SELECT * FROM caretakers').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        health_status = request.form['health_status']
        admission_date = request.form['admission_date']
        caretaker_id = request.form['caretaker_id']

        conn.execute('''
            INSERT INTO children (name, age, gender, health_status, admission_date, caretaker_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, age, gender, health_status, admission_date, caretaker_id))
        conn.commit()
        conn.close()
        flash('New child added successfully!', 'success')
        return redirect(url_for('children'))

    conn.close()
    return render_template('add_child.html', caretakers=caretakers)




@app.route('/update_child/<int:id>', methods=['GET', 'POST'])
@login_required
def update_child(id):
    conn = get_db_connection()
    child = conn.execute('SELECT * FROM children WHERE Ch_id = ?', (id,)).fetchone()
    caretakers = conn.execute('SELECT * FROM caretakers').fetchall()

    if not child:
        conn.close()
        flash('Child not found.', 'danger')
        return redirect(url_for('children'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        health_status = request.form['health_status']
        admission_date = request.form['admission_date']
        caretaker_id = request.form['caretaker_id']

        conn.execute('''
            UPDATE children
            SET name = ?, age = ?, gender = ?, health_status = ?, admission_date = ?, caretaker_id = ?
            WHERE Ch_id = ?
        ''', (name, age, gender, health_status, admission_date, caretaker_id, id))
        conn.commit()
        conn.close()
        flash('Child information updated successfully!', 'success')
        return redirect(url_for('children'))

    conn.close()
    return render_template('update_child.html', child=child, caretakers=caretakers)



@app.route('/delete_child/<int:id>')
@login_required
def delete_child(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM children WHERE Ch_id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Child deleted successfully.', 'info')
    return redirect(url_for('children'))



@app.route('/caretakers')
@login_required
def caretakers():
    conn = get_db_connection()
    caretakers = conn.execute('SELECT * FROM caretakers').fetchall()
    conn.close()
    return render_template('caretakers.html', caretakers=caretakers)


@app.route('/add_caretaker', methods=['GET', 'POST'])
def add_caretaker():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']

        conn = get_db_connection()
        conn.execute("INSERT INTO caretakers (name, age, gender) VALUES (?, ?, ?)",
                     (name, age, gender))
        conn.commit()
        conn.close()

        return redirect('/caretakers')
    return render_template('add_caretaker.html')



@app.route('/update_caretaker/<int:id>', methods=['GET', 'POST'])
def update_caretaker(id):
    conn = get_db_connection()
    caretaker = conn.execute('SELECT * FROM caretakers WHERE Ct_id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']

        conn.execute('UPDATE caretakers SET name = ?, age = ?, gender = ? WHERE Ct_id = ?',
                     (name, age, gender, id))
        conn.commit()
        conn.close()
        return redirect('/caretakers')

    conn.close()
    return render_template('update_caretaker.html', caretaker=caretaker)



@app.route('/delete_caretaker/<int:id>')
@login_required
def delete_caretaker(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM caretakers WHERE Ct_id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Caretaker deleted successfully.', 'info')
    return redirect(url_for('caretakers'))



if __name__ == '__main__':
    app.run(debug=True)
