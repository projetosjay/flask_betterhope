# routes.py

from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from extensions import db, bcrypt
from models import User, ContactForm

auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/main')
def home():
    #if current_user.is_authenticated:
    return render_template('index.html') 
    #return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Verifica se o email já está registrado
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Este email já está registrado.', 'danger')
            return redirect(url_for('auth.register'))

        # Se o email não está registrado, prossegue com o registro
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        is_admin = User.query.count() == 0  # Define o primeiro usuário como administrador
        new_user = User(username=username, email=email, password=hashed_password, is_admin=is_admin)

        db.session.add(new_user)
        db.session.commit()

        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email não encontrado.', 'danger')
        elif not bcrypt.check_password_hash(user.password, password):
            flash('Senha incorreta.', 'danger')
        else:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('chat.group_list'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    username = data['username']
    email = data['email']

    current_user.username = username
    current_user.email = email

    db.session.commit()

    return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso!'})

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_contact = ContactForm(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()

        #flash('Mensagem enviada com sucesso!', 'success')
        return render_template('index.html', contact_forms=contact_forms)


@main_bp.route('/contact_forms')
@login_required
def contact_forms():
    if current_user.email != 'jayadm@gmail.com':
        #flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))

    contact_forms = ContactForm.query.all()
    return render_template('contact_forms.html', contact_forms=contact_forms)

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
