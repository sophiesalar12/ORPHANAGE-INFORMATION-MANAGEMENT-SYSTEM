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




@app.route('/adopters')
@login_required
def adopters():
    conn = get_db_connection()
    adopters = conn.execute('SELECT * FROM adopters').fetchall()
    conn.close()
    return render_template('adopter.html', adopters=adopters)


@app.route('/add_adopter', methods=['GET', 'POST'])
@login_required
def add_adopter():
    if request.method == 'POST':
        full_name = request.form['full_name']
        gender = request.form['gender']
        dob = request.form['dob']
        address = request.form['address']
        c_number = request.form['c_number']
        occupation = request.form['occupation']
        m_status = request.form['m_status']
        a_reason = request.form['a_reason']
        date_applied = request.form['date_applied']
        status = request.form['status']
        age = request.form['age']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO adopters (
                full_name, gender, dob, address, c_number,
                occupation, m_status, a_reason, date_applied,
                status, age
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, gender, dob, address, c_number,
              occupation, m_status, a_reason, date_applied,
              status, age))
        conn.commit()
        conn.close()

        flash('Adopter added successfully!')
        return redirect(url_for('adopters'))
    return render_template('add_adopter.html')


@app.route('/view_adopter/<int:id>')
@login_required
def view_adopter(id):
    conn = get_db_connection()
    adopter = conn.execute('SELECT * FROM adopters WHERE A_id = ?', (id,)).fetchone()
    conn.close()

    if adopter is None:
        flash('Adopter not found.', 'danger')
        return redirect(url_for('adopters'))  # redirect back to adopter list

    return render_template('view_adopter.html', adopter=adopter)


@app.route('/edit_adopter/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_adopter(id):
    conn = get_db_connection()
    adopter = conn.execute('SELECT * FROM adopters WHERE A_id = ?', (id,)).fetchone()

    if not adopter:
        conn.close()
        flash('Adopter not found.', 'danger')
        return redirect(url_for('adopters'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        gender = request.form['gender']
        dob = request.form['dob']
        address = request.form['address']
        c_number = request.form['c_number']
        occupation = request.form['occupation']
        m_status = request.form['m_status']
        a_reason = request.form['a_reason']
        status = request.form['status']
        age = request.form['age']

        conn.execute('''
            UPDATE adopters
            SET full_name = ?, gender = ?, dob = ?, address = ?, c_number = ?, 
                occupation = ?, m_status = ?, a_reason = ?, status = ?, age = ?
            WHERE A_id = ?
        ''', (full_name, gender, dob, address, c_number, occupation, m_status, a_reason, status, age, id))
        conn.commit()
        conn.close()

        flash('Adopter information updated successfully!', 'success')
        return redirect(url_for('adopters'))

    conn.close()
    return render_template('edit_adopter.html', adopter=adopter)


@app.route('/delete_adopter/<int:id>')
@login_required
def delete_adopter(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM adopters WHERE A_id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Adopter deleted successfully.', 'info')
    return redirect(url_for('adopters'))



@app.route('/adoption')
@login_required
def adoptions():
    conn = get_db_connection()
    adoptions = conn.execute('''
        SELECT ad.Ad_id, ad.adoption_date, ad.status,
               a.full_name AS adopter_name, c.name AS child_name
        FROM adoptions ad
        JOIN adopters a ON ad.A_id = a.A_id
        JOIN children c ON ad.Ch_id = c.Ch_id
    ''').fetchall()
    conn.close()
    return render_template('adoption.html', adoptions=adoptions)


@app.route('/add_adoption', methods=['GET', 'POST'])
@login_required
def add_adoption():
    conn = get_db_connection()
    adopters = conn.execute('SELECT * FROM adopters').fetchall()
    children = conn.execute('SELECT * FROM children').fetchall()

    if request.method == 'POST':
        adopter_id = request.form['adopter_id']
        child_id = request.form['child_id']
        adoption_date = request.form['adoption_date']
        status = 'Approved'

        conn.execute('''
            INSERT INTO adoptions (A_id, Ch_id, adoption_date, status)
            VALUES (?, ?, ?, ?)
        ''', (adopter_id, child_id, adoption_date, status))
        conn.commit()
        conn.close()

        flash('Adoption record created successfully!', 'success')
        return redirect(url_for('adoptions'))

    conn.close()
    return render_template('add_adoption.html', adopters=adopters, children=children)



@app.route('/delete_adoption/<int:id>')
@login_required
def delete_adoption(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM adoptions WHERE Ad_id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Adoption record deleted successfully.', 'info')
    return redirect(url_for('adoptions'))


@app.route('/edit_adoption/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_adoption(id):
    conn = get_db_connection()
    adoption = conn.execute('''
        SELECT ad.Ad_id, ad.A_id, ad.Ch_id, ad.adoption_date, ad.status,
               a.full_name AS adopter_name,
               c.name AS child_name
        FROM adoptions ad
        JOIN adopters a ON ad.A_id = a.A_id
        JOIN children c ON ad.Ch_id = c.Ch_id
        WHERE ad.Ad_id = ?
    ''', (id,)).fetchone()

    if not adoption:
        conn.close()
        flash('Adoption record not found.', 'danger')
        return redirect(url_for('adoptions'))

    if request.method == 'POST':
        adoption_date = request.form['adoption_date']
        status = request.form['status']

        conn.execute('''
            UPDATE adoptions
            SET adoption_date = ?, status = ?
            WHERE Ad_id = ?
        ''', (adoption_date, status, id))
        conn.commit()
        conn.close()

        flash('Adoption record updated successfully!', 'success')
        return redirect(url_for('adoptions'))

    conn.close()
    return render_template('edit_adoption.html', adoption=adoption)



if __name__ == '__main__':
    app.run(debug=True)
