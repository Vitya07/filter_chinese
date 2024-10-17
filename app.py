from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, WordForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на свой секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # Укажите базу данных
db = SQLAlchemy(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модели базы данных
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    words = db.relationship('Word', backref='user', lazy=True)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('add_words'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_words', methods=['GET', 'POST'])
@login_required
def add_words():
    form = WordForm()
    if form.validate_on_submit():
        words = [w.strip() for w in form.words.data.replace(',', ' ').split()]
        for word in words:
            if word:
                new_word = Word(word=word, user_id=current_user.id)
                db.session.add(new_word)
        db.session.commit()
        flash('Words added successfully!')
        return redirect(url_for('profile'))  # Перенаправляем на профиль
    return render_template('add_words.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Получаем все слова пользователя и формируем уникальные иероглифы
    words = Word.query.filter_by(user_id=current_user.id).all()
    unique_characters = sorted(set(char for word in words for char in word.word))

    return render_template('profile.html', characters=unique_characters)

@app.route('/delete_character/<char>', methods=['POST'])
@login_required
def delete_character(char):
    # Удаляем все слова, содержащие указанный иероглиф
    words_to_delete = Word.query.filter(Word.word.contains(char), Word.user_id == current_user.id).all()
    for word in words_to_delete:
        db.session.delete(word)
    db.session.commit()
    flash(f'Character "{char}" and associated words deleted successfully.')
    return redirect(url_for('profile'))

@app.route('/clear_words', methods=['POST'])  # Изменено на POST
@login_required
def clear_words():
    # Удаляем все слова текущего пользователя
    Word.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('All words cleared.')
    return redirect(url_for('profile'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаём таблицы, если их ещё нет
    app.run(debug=True)
