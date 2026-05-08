import os
from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.db_session import global_init
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.solve_form import SolveForm
from data.user import User
from data.puzzle import Puzzle
from data.create_puzzle import CreatePuzzle
from waitress import serve
from data.word_definition import get_word_definition

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/puzzles.db')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/')
def func():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])  # регистрация
def register():
    form = RegisterForm()  # форма регистрации
    if form.validate_on_submit():  # если форма готова к отправке
        if form.password.data != form.password_again.data:  # если пароли не совпали, то сообщаем об этом
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(
                User.email == form.email.data).first():  # проверяем, не создан ли уже пользователь для этой почты
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        # если всё хорошо, то создаём нового пользователя
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            theme='light'
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)  # сразу же входим в аккаунт
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])  # вход в аккаунт
def login():
    form = LoginForm()  # форма входа
    if form.validate_on_submit():  # если форма готова к отправке
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()  # ищем пользователя с полученнным логином
        if user and user.check_password(form.password.data):  # если пользователь есть и пароль совпал
            login_user(user, remember=form.remember_me.data)  # входим в аккаунт
            return redirect("/")
        # если не нашли пользователя с таким логином или пароли не совпали
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')  # выход из аккаунта
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')  # страница профиля (фамилия, имя, почта, смена темы и удаление аккаунта)
@login_required
def profile():
    return render_template('profile.html')


@app.route('/delete_account/<user_id>')  # удаление аккаунта с сохранением созданных головоломок
@login_required
def delete_account(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)  # получаем пользователя
    db_sess.delete(user)  # удаляем
    db_sess.commit()
    return redirect('/')


@app.route('/delete_account_with_puzzles/<user_id>')  # удаление аккаунта вместе со всеми созданными головоломками
@login_required
def delete_account_with_puzzles(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)  # получаем пользователя
    for puzzle in user.puzzles:  # проходим по папкам с картинками всех головоломок
        if os.path.exists(f'static/img/rebuses/{puzzle.id}.png'):  # если файл существует
            os.remove(f'static/img/rebuses/{puzzle.id}.png')  # удаляем
        db_sess.delete(puzzle)  # удаление головоломки, к которой относилась эта картинка
    db_sess.delete(user)  # удаление пользователя
    db_sess.commit()
    return redirect('/')


@app.route('/change_theme/<theme>')  # смена темы (светлая / тёмная)
@login_required
def change_theme(theme):
    db_sess = db_session.create_session()
    user = db_sess.get(User, current_user.id)
    user.theme = theme  # сохраняем в базу данных выбранную тему,
    db_sess.commit()
    return redirect('/profile')


@app.route('/my_puzzles')  # головоломки, созданные пользователем
@login_required
def my_puzzles():
    db_sess = db_session.create_session()
    puzzles = db_sess.get(User, current_user.id).puzzles  # все головоломки пользователя
    puzzles.reverse()  # переворот списка, чтобы пользователь видел сначала новые головоломки
    user = db_sess.get(User, current_user.id)  # пользователь, чтобы определять,
    # какие головоломки он решил
    return render_template('my_puzzles.html', puzzles=puzzles, user=user)


@app.route('/all_puzzles')  # все головоломки
@login_required
def all_puzzles():
    db_sess = db_session.create_session()
    puzzles = db_sess.query(Puzzle).all()  # все головоломки
    puzzles.reverse()
    user = db_sess.get(User, current_user.id)  # пользователь, чтобы определять,
    # какие головоломки он решил
    return render_template('all_puzzles.html', puzzles=puzzles, user=user)


@app.route('/all_solved_puzzles')  # все решённые пользователем головоломки
@login_required
def all_solved_puzzles():
    db_sess = db_session.create_session()
    user = db_sess.get(User, current_user.id)  # получаем пользователя
    puzzles = [p for p in db_sess.get(User, user.id).solved_puzzles]  # все решённые головоломки
    return render_template('all_puzzles.html', puzzles=puzzles, user=user)


@app.route('/all_not_solved_puzzles')  # все нерешённые пользователем головоломки
@login_required
def all_not_solved_puzzles():
    db_sess = db_session.create_session()
    user = db_sess.get(User, current_user.id)  # получаем пользователя
    solved_ids = [p.id for p in db_sess.get(User, user.id).solved_puzzles]  # id решённых головоломок
    puzzles = db_sess.query(Puzzle.id).filter(~Puzzle.id.in_(solved_ids)).all()  # все нерешённые головоломки
    return render_template('all_puzzles.html', puzzles=puzzles, user=user)


@app.route('/create', methods=['GET', 'POST'])  # создание головоломки
@login_required
def add_puzzle():
    puzzle_form = CreatePuzzle()  # форма создания головоломки
    if puzzle_form.validate_on_submit():  # если форма готова к отправке
        file = puzzle_form.puzzle.data
        if file is None:  # проверяем, добавлен ли файл
            return render_template('create_puzzle.html',
                                   title='Создание',
                                   form=puzzle_form, puzzle_id=0, message='Добавьте картинку')
        db_sess = db_session.create_session()
        # создаём новую головоломку
        puzzle = Puzzle(
            answer=puzzle_form.answer.data,
            hint=puzzle_form.hint.data,
            user_id=current_user.id,
        )
        db_sess.add(puzzle)
        db_sess.commit()
        # получаем значение (объяснение слова)
        puzzle.definition = get_word_definition(puzzle.answer)
        db_sess.commit()
        file = puzzle_form.puzzle.data  # получаем файл
        file.save(f'static/img/rebuses/{puzzle.id}.png')  # сохраняем в специальную папку
        return redirect('/my_puzzles')
    return render_template('create_puzzle.html',
                           title='Создание',
                           form=puzzle_form, puzzle_id=0)


@app.route('/edit/<puzzle_id>', methods=['GET', 'POST'])  # редактирование головоломки
@login_required
def edit_puzzle(puzzle_id):
    puzzle_form = CreatePuzzle()
    db_sess = db_session.create_session()
    if request.method == "GET":  # если пока смотрим
        puzzle = db_sess.get(Puzzle, puzzle_id)  # получаем головоломку по id
        if puzzle:  # если нашли
            puzzle_form.answer.data = puzzle.answer  # берём правильный ответ и подсказку
            puzzle_form.hint.data = puzzle.hint
        else:
            abort(404)
    if puzzle_form.validate_on_submit():  # если сохраняем изменения
        puzzle = db_sess.get(Puzzle, puzzle_id)
        if puzzle:
            puzzle.answer = puzzle_form.answer.data  # обновляем ответ и подсказку
            puzzle.hint = puzzle_form.hint.data
            db_sess.add(puzzle)
            db_sess.commit()
            file = puzzle_form.puzzle.data
            if file is not None:  # если добавили новый файл, сохраняем его (заменяем прошлый)
                file.save(f'static/img/rebuses/{puzzle.id}.png')
            return redirect('/my_puzzles')
        else:
            abort(404)
    return render_template('create_puzzle.html',
                           title='Создание',
                           form=puzzle_form, puzzle_id=puzzle_id)


@app.route('/delete/<puzzle_id>', methods=['GET', 'POST'])  # удаление головоломки
@login_required
def delete_puzzle(puzzle_id):
    db_sess = db_session.create_session()
    puzzle = db_sess.get(Puzzle, puzzle_id)  # получаем головоломку по id
    os.remove(f'static/img/rebuses/{puzzle.id}.png')  # удаляем картинку
    db_sess.delete(puzzle)  # удаляем головоломку
    db_sess.commit()
    return redirect('/my_puzzles')


@app.route('/solve/<puzzle_id>', methods=['GET', 'POST'])  # решение головоломки
@login_required
def solve_puzzle(puzzle_id):
    solve_form = SolveForm()  # форма для отправки ответа пользователя
    db_sess = db_session.create_session()
    puzzle = db_sess.get(Puzzle, puzzle_id)  # получаем головоломку
    user = db_sess.get(User, current_user.id)  # получаем пользователя
    if puzzle in user.solved_puzzles:  # если головоломка уже решена
        return render_template('solve.html', puzzle=puzzle, is_solved=True)
    if solve_form.validate_on_submit():  # если форма готова к отправке
        is_solved = solve_form.answer.data.lower() == puzzle.answer.lower()  # совпадает ли ответ
        # с правильным (без учёта регистра)
        if is_solved:  # если совпадает
            message = 'Поздравляем! Это правильный ответ! :)'
            user.solved_puzzles.append(puzzle)  # сохраняем, что пользователь её решил
            db_sess.merge(current_user)
            db_sess.commit()
        else:
            message = 'Неверно. Подумайте ещё ;)'
        return render_template('solve.html', puzzle=puzzle, form=solve_form, is_solved=is_solved, message=message)
    return render_template('solve.html', puzzle=puzzle, form=solve_form)


if __name__ == '__main__':
    # serve(app, host='0.0.0.0',port=5000)
    app.run(host='127.0.0.1', port=8080)
