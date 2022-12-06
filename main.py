from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from werkzeug.exceptions import abort
import sqlite3

from flask import Flask, render_template, request, url_for, flash, redirect
from config import Config
from sqlmodel import Session
from sqlalchemy import create_engine, select, update
from config import app, db

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField

from model import *

engine = create_engine('sqlite:///database.db')
conn2 = engine.connect()


def get_item(item_id):
    return db.session.query(Item).filter(Item.item_id == int(item_id)).one_or_none()


def get_manager(manager_id):
    return db.session.query(Manager).filter(Manager.manager_id == int(manager_id)).one_or_none()


def get_order_item(order_id):
    return db.session.query(Order_item).filter(Order_item.order_id == int(order_id)).one_or_none()


def get_order_list(order_list_id):
    return db.session.query(Order_list).filter(Order_list.order_list_id == int(order_list_id)).one_or_none()


class CreateItem(FlaskForm):
    first_input = StringField(label='Enter name')
    second_input = StringField(label='Enter model')
    submit = SubmitField(label='Submit')


class CreateManager(FlaskForm):
    first_input = StringField(label='Enter surname')
    second_input = StringField(label='Enter name')
    submit = SubmitField(label='Submit')


class CreateOrderItem(FlaskForm):
    first_input = StringField(label='Enter item ID')
    second_input = StringField(label='Enter amount of')
    submit = SubmitField(label='Submit')


class CreateOrderList(FlaskForm):
    first_input = StringField(label='Enter order ID')
    second_input = StringField(label='Enter manader ID')
    third_input = StringField(label="Enter order date")
    four_input = StringField(label="Enter status")
    submit = SubmitField(label='Submit')


def connect_base():
    conn = sqlite3.connect('database2.db')
    conn.row_factory = sqlite3.Row
    return conn


def check_input(input_str):
    for i in range(0, len(input_str)):
        if (input_str[i] == ' ' or input_str[i] == "\'" or input_str[i] == '/' or input_str[i] == '*'
                or input_str[i] == "\""):
            return False
        else:
            return True


#  ###########
#  #Item part#
#  ###########


@app.route('/')
def show_items():
    return render_template('index_item.html', item=db.session.query(Item).all())


@app.route('/create', methods=('GET', 'POST'))
def create():
    form = CreateItem()
    if form.validate_on_submit() and request.method == 'POST':
        if not form.first_input.data or not form.second_input.data:
            flash('You must fill all fields!')
        else:
            new_name = form.first_input.data
            new_model = form.second_input.data
            new_item = Item(item_name=f"{new_name}", item_model=f"{new_model}")
            form.populate_obj(new_item)
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('show_items'))
    return render_template('create_item.html', form=form)


#
# <div class="form-group">
#             {{ form.violation.label }}
#             {{ form.violation(class="form-control") }}
#             {% for error in form.violation.errors %}
#             <div class="alert alert-danger">
#                  {{ error }}
#             </div>
#             {% endfor%}
#         </div>


@app.route('/<int:id>/edit_item', methods=('GET', 'POST'))
def edit_item(id):
    form = CreateItem()
    current_item = get_item(id)
    if request.method == 'GET':
        form.first_input.data = current_item.item_name
        form.second_input.data = current_item.item_model

    if form.validate_on_submit() and request.method == 'POST':
        new_name = form.first_input.data
        new_model = form.second_input.data
        now_item = db.session.query(Item).filter(Item.item_id == id).first()

        now_item.item_name = new_name
        now_item.item_model = new_model
        db.session.commit()
        return redirect(url_for('show_items'))
    return render_template('edit_item.html', form=form, now_id=id)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    now_delete = db.session.query(Item).filter(Item.item_id == id).first()
    db.session.delete(now_delete)
    db.session.commit()
    flash('Item with "{}"  ID was successfully deleted!'.format(id))
    return redirect(url_for('show_items'))


def get_item_id_post(post_id):
    conn = connect_base()
    now_item = db.session.query(Item).filter(Item.item_id == post_id).first()
    conn.close()
    if now_item is None:
        abort(404)
    return now_item


@app.route('/<int:post_id>')
def post_item(post_id):
    now_item = get_item_id_post(post_id)
    return render_template('annotation.html', item=now_item)


#  ###########
#  #Item part#
#  ###########


#  ##############
#  #Manager part#
#  ##############


def get_manager_id_post(post_id):
    conn = connect_base()
    now_item = db.session.query(Manager).filter(Manager.manager_id == post_id).first()
    conn.close()
    if now_item is None:
        abort(404)
    return now_item


def get_item_manager_post(post_id):
    conn = connect_base()
    post = conn.execute("SELECT * FROM manager WHERE manager_id = ?",
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route('/All_manager_list')
def index_manager():
    return render_template('index_manager.html', item=db.session.query(Manager).all())


@app.route('/<int:id>/edit_manager', methods=('GET', 'POST'))
def edit_manager(id):
    form = CreateManager()
    current_manager = get_manager(id)
    if request.method == 'GET':
        form.first_input.data = current_manager.surname
        form.second_input.data = current_manager.name

    if form.validate_on_submit() and request.method == 'POST':
        new_surname = form.first_input.data
        new_name = form.second_input.data
        now_manager = db.session.query(Manager).filter(Manager.manager_id == id).first()

        now_manager.surname = new_surname
        now_manager.name = new_name
        db.session.commit()
        return redirect(url_for('index_manager'))
    return render_template('edit_manager.html', form=form, now_id=id)


@app.route('/create_manager', methods=('GET', 'POST'))
def create_manager():
    form = CreateManager()
    if form.validate_on_submit() and request.method == 'POST':
        if not form.first_input.data or not form.second_input.data:
            flash('You must fill all fields!')
        else:
            new_surname = form.first_input.data
            new_name = form.second_input.data
            new_manager = Manager(surname=f"{new_surname}", name=f"{new_name}")
            form.populate_obj(new_manager)
            db.session.add(new_manager)
            db.session.commit()
            return redirect(url_for('index_manager'))
    return render_template('create_manager.html', form=form)


@app.route('/<int:id>/delete_manager', methods=('POST',))
def delete_manager(id):
    now_delete = db.session.query(Manager).filter(Manager.manager_id == id).first()
    db.session.delete(now_delete)
    db.session.commit()
    flash('Manager with "{}"  ID was successfully deleted!'.format(id))
    return redirect(url_for('index_manager'))


@app.route('/manager/<int:post_id>')
def post_manager(post_id):
    now_item = get_manager_id_post(post_id)
    return render_template('annotation_manager.html', item=now_item)


#  ##############
#  #Manager part#
#  ##############


#  #################
#  #Order item part#
#  #################


@app.route('/order_item/<int:post_id>')
def post_order_item(post_id):
    now_item = get_order_id_post(post_id)
    return render_template('annotation_order_item.html', item=now_item)


def get_order_id_post(post_id):
    conn = connect_base()
    now_order_item = db.session.query(Order_item).filter(Order_item.order_id == post_id).first()
    conn.close()
    if now_order_item is None:
        abort(404)
    return now_order_item


@app.route('/All_order_item')
def index_order_item():
    return render_template('index_order_item.html', item=db.session.query(Order_item).all())


@app.route('/<int:id>/edit_order_item', methods=('GET', 'POST'))
def edit_order_item(id):
    form = CreateOrderItem()
    current_order_item = get_order_item(id)
    if request.method == 'GET':
        form.first_input.data = current_order_item.item_id
        form.second_input.data = current_order_item.amount

    if form.validate_on_submit() and request.method == 'POST':
        new_item_id = form.first_input.data
        new_amount = form.second_input.data
        if new_item_id.isdigit() and new_item_id.isdigit():
            now_order_item = db.session.query(Order_item).filter(Order_item.order_id == id).first()

            now_order_item.item_id = new_item_id
            now_order_item.amount = new_amount
            db.session.commit()
            return redirect(url_for('index_order_item'))
        else:
            flash('You must enter positive integer!')

    return render_template('edit_order_item.html', form=form, now_id=id)


@app.route('/<int:id>/delete_order_item', methods=('POST',))
def delete_order_item(id):
    now_delete = db.session.query(Order_item).filter(Order_item.order_id == id).first()
    db.session.delete(now_delete)
    db.session.commit()
    flash('Order item with "{}"  ID was successfully deleted!'.format(id))
    return redirect(url_for('index_order_item'))


@app.route('/create_order_item', methods=('GET', 'POST'))
def create_order_item():
    form = CreateOrderItem()
    if form.validate_on_submit() and request.method == 'POST':
        if not form.first_input.data or not form.second_input.data:
            flash('You must fill all fields!')
        else:
            new_item_id = form.first_input.data
            new_amount = form.second_input.data
            if new_item_id.isdigit() and new_item_id.isdigit():
                new_order = Order_item(item_id=f"{new_item_id}", amount=f"{new_amount}")
                form.populate_obj(new_order)
                db.session.add(new_order)
                db.session.commit()
                return redirect(url_for('index_order_item'))
            else:
                flash('You must enter positive integer!')

    return render_template('create_order_item.html', form=form)


#  #################
#  #Order item part#
#  #################


#  #################
#  #Order list part#
#  #################


@app.route('/All order list')
def index_order_list():
    return render_template('index_order_list.html', item=db.session.query(Order_list).all())


def get_order_list_id_post(post_id):
    conn = connect_base()
    now_order_list = db.session.query(Order_list).filter(Order_list.order_list_id == post_id).first()
    conn.close()
    if now_order_list is None:
        abort(404)
    return now_order_list


@app.route('/order_list/<int:post_id>')
def post_order_list(post_id):
    now_item = get_order_list_id_post(post_id)
    return render_template('annotation_order_list.html', item=now_item)


@app.route('/create_order_list', methods=('GET', 'POST'))
def create_order_list():
    form = CreateOrderList()
    if form.validate_on_submit() and request.method == 'POST':
        if not form.first_input.data or not form.second_input.data:
            flash('You must fill all fields!')
        else:
            new_order_id = form.first_input.data
            new_manager_id = form.second_input.data
            new_order_date = form.third_input.data
            new_status = form.four_input.data
            new_order_list = Order_list(order_id=f"{new_order_id}", manager_id=f"{new_manager_id}",
                                        order_date=f"{new_order_date}", status=f"{new_status}")
            form.populate_obj(new_order_list)
            db.session.add(new_order_list)
            db.session.commit()
            return redirect(url_for('index_order_list'))
    return render_template('create_order_list.html', form=form)


@app.route('/<int:id>/edit_order_list', methods=('GET', 'POST'))
def edit_order_list(id):
    form = CreateOrderList()
    current_list = get_order_list(id)
    if request.method == 'GET':
        form.first_input.data = current_list.order_id
        form.second_input.data = current_list.manager_id
        form.third_input.data = current_list.order_date
        form.four_input.data = current_list.status

    if form.validate_on_submit() and request.method == 'POST':
        new_order_id = form.first_input.data
        new_manager_id = form.second_input.data
        new_order_date = form.third_input.data
        new_status = form.four_input.data

        now_order_list = db.session.query(Order_list).filter(Order_list.order_list_id == id).first()

        now_order_list.order_id = new_order_id
        now_order_list.manager_id = new_manager_id
        now_order_list.order_date = new_order_date
        now_order_list.status = new_status
        db.session.commit()
        return redirect(url_for('index_order_list'))
    return render_template('edit_order_list.html', form=form, now_id=id)


@app.route('/<int:id>/delete_order_list', methods=('POST',))
def delete_order_list(id):
    now_delete = db.session.query(Order_list).filter(Order_list.order_list_id == id).first()
    db.session.delete(now_delete)
    db.session.commit()
    flash('Order list with "{}"  ID was successfully deleted!'.format(id))
    return redirect(url_for('index_order_list'))


#  #################
#  #Order list part#
#  #################


if __name__ == '__main__':
    # print("sad")

    # print(db.session.query(Item).filter(Item.item_id == 200).one_or_none())

    cursor = connect_base().cursor()
    app.run(debug=True)

# <a class="navbar-brand" href="{{ url_for('index')}}">Go to item list</a>

# @app.route('/create2', methods=('GET', 'POST'))
# def create2():
#     form = CreateItem()
#     if form.validate_on_submit():
#         if not form.first_input or not form.second_input:
#             flash('aaaaaaaaaaaa')
#         else:
#             new_item = Item()
#             form.populate_obj(new_item)
#             db.session.add(new_item)
#             db.session.commit()
#             return redirect(url_for('index'))
#     return render_template('add_item.html', form=form)


#
# <span class="badge badge-primary">{{ post['item_id'] }}</span>

#
# @app.route('/<int:id>/edit_item2', methods=('GET', 'POST'))
# def edite_item2(id):
#     form = CreateItem()
#     post = get_item_id_post(id)
#     current_item = get_item(str(post))
#     if form.validate_on_submit() and request.method == 'POST':
#         form.populate_obj(current_item)
#         return redirect(url_for('index_test'))
#     return render_template('edit_item.html', form=form)

#
# @app.route('/create', methods=('GET', 'POST'))
# def create():
#     form = CreateItem()
#     if form.validate_on_submit():
#         if form.first_input.data != '' and form.second_input.data != '' \
#                 and form.first_input.data != ' ' and form.second_input.data != ' ':
#             if check_input(form.first_input.data) or check_input(form.second_input.data):
#                 conn = connect_base()
#                 conn.execute('INSERT INTO item (item_name, item_model) VALUES (?, ?)',
#                              (form.first_input.data, form.second_input.data))
#                 conn.commit()
#                 conn.close()
#                 return redirect(url_for('index'))
#             else:
#                 flash('Stop using forbidden symbols!!!')
#         else:
#             flash('Name and model is required!')
#     return render_template('add_item.html', form=form)
#
#
# @app.route('/<int:id>/edit_item', methods=('GET', 'POST'))
# def edit(id):
#     post = get_item_id_post(id)
#     form = CreateItem()
#     if form.validate_on_submit():
#         if form.first_input.data != '' and form.second_input.data != '' \
#                 and form.first_input.data != ' ' and form.second_input.data != ' ':
#             if check_input(form.first_input.data) and check_input(form.second_input.data):
#                 conn = connect_base()
#                 conn.execute('UPDATE item SET item_name = ?, item_model = ?'
#                              ' WHERE item_id = ?',
#                              (form.first_input.data, form.second_input.data, id))
#                 conn.commit()
#                 conn.close()
#                 return redirect(url_for('index'))
#             else:
#                 flash('Stop using forbidden symbols!!!')
#         else:
#             flash('Name and model is required!')
#     return render_template('edit_item_old.html', form=form, post=post)
#
#
# @app.route('/<int:id>/delete', methods=('POST',))
# def delete(id):
#     post = get_item_id_post(id)
#     conn = connect_base()
#     conn.execute('DELETE FROM item WHERE item_id = ?', (id,))
#     conn.commit()
#     conn.close()
#     flash('Item with "{}"  ID was successfully deleted!'.format([post['item_id']]))
#     return redirect(url_for('index'))
