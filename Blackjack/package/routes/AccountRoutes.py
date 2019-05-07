from flask import Flask, render_template, redirect, url_for, request, flash, get_flashed_messages
from Blackjack.package import app, bcrypt, db
from Blackjack.package.Databases.database_model import User
from Blackjack.package.Forms.AccountForms import CreateAccountFlaskForm, LoginFlaskForm, UpdateAccountFlaskForm, DeleteAccountFlaskForm
from flask_login import current_user, login_user, logout_user, login_required

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    form = CreateAccountFlaskForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                    username=form.username.data, password=hash_password, funds=1000)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=form.email.data).first()
        flash('Account Created Successfully!!!')
        login_user(user)
        return redirect(url_for('gameplay_page'))
    return render_template("Accounts/CreateAccount.html", form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginFlaskForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash('Successful Login!!!')
            login_user(user)
            return redirect(url_for('gameplay_page'))
        else:
            flash('Unsuccessful Login!!!')
            return redirect(url_for('login'))
    return render_template("Accounts/Login.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_required
@app.route('/profile_page', methods=['GET', 'POST'])
def profile_page():
    form = UpdateAccountFlaskForm()
    delete_form = DeleteAccountFlaskForm()
    if form.validate_on_submit():
        if form.username.data != '':
            current_user.username = form.username.data
        else:
            form.username.data = current_user.username
        if form.email.data != '':
            current_user.email = form.email.data
        else:
            form.email.data = current_user.email
        if form.password.data != '':
            current_user.password = form.password.data
        else:
            form.password.data = current_user.password

        if current_user.funds == None:
            current_user.funds = 0
        current_user.funds += form.add_funds.data
        if current_user.funds < 0:
            current_user.funds = 0
        db.session.commit()
        return redirect(url_for('profile_page'))
    if delete_form.validate_on_submit():
        db.session.delete(current_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("ProfilePage.html", form=form, delete_form=delete_form)

