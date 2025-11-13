from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '5457fae2a71f9331bf4bf3dd6813f90abeb33839f4608755ce301b9321c6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Описание таблиц
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    lg = db.Column(db.Integer, default=0)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)


# Создание таблиц
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return redirect(url_for('registration'))


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    error_1 = ''
    error_2 = ''
    error_3 = ''
    value_1, value_2, value_3 = '', '', ''
    system_error = ''

    if request.method == 'GET':
        return render_template('registration.html',
                               error_1=error_1, error_2=error_2, error_3=error_3,
                               system_error=system_error,
                               value_1=value_1, value_2=value_2, value_3=value_3)

    elif request.method == 'POST':
        # Получаем данные из формы
        username = request.form.get('firstname', '').title()
        email = request.form.get('email', '')
        password = request.form.get('pasvord', '')

        # Сохраняем значения для повторного отображения в форме
        value_1, value_2, value_3 = username, password, email

        # Валидация данных
        if not username:
            error_1 = 'Введите имя пользователя'
        if not email:
            error_3 = 'Введите адрес электронной почты'
        if not password:
            error_2 = 'Введите пароль'

        # Если есть ошибки валидации, возвращаем форму с ошибками
        if any([error_1, error_2, error_3]):
            return render_template('registration.html',
                                   error_1=error_1, error_2=error_2, error_3=error_3,
                                   system_error=system_error,
                                   value_1=value_1, value_2=value_2, value_3=value_3)

        try:
            # Проверяем, существует ли пользователь с таким именем или email
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing_user:
                if existing_user.username == username:
                    error_1 = 'Имя пользователя уже занято'
                if existing_user.email == email:
                    error_3 = 'Email уже зарегистрирован'

                return render_template('registration.html',
                                       error_1=error_1, error_2=error_2, error_3=error_3,
                                       system_error=system_error,
                                       value_1=value_1, value_2=value_2, value_3=value_3)

            # Создаем нового пользователя
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            # Сохраняем пользователя в сессии
            session.permanent = True
            session['name'] = username
            session['email'] = email

            return redirect("/personal_account")

        except Exception as e:
            db.session.rollback()
            system_error = f'Произошла ошибка при регистрации: {str(e)}'
            return render_template('registration.html',
                                   error_1=error_1, error_2=error_2, error_3=error_3,
                                   system_error=system_error,
                                   value_1=value_1, value_2=value_2, value_3=value_3)




if __name__ == '__main__':
    app.run(debug=True)