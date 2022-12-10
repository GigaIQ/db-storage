import re

# from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import create_engine, Column, Integer, String, func, desc
# from sqlalchemy.orm import declarative_base
from werkzeug.exceptions import abort
import sqlite3

from flask import Flask, render_template, request, url_for, flash, redirect
# from config import Config
# from sqlmodel import Session
from sqlalchemy import create_engine, select, update
from config import app, db

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField

from model import *

engine = create_engine('sqlite:///database.db')
conn2 = engine.connect()
POSTS_AT_PAGE = 10
REG_DATE = '\d\d.\d\d.\d{4}'
REG_ITEM = '\S+'
REG_MANAGER_NAME_OR_SURNAME = '^([а-яА-Я]|[a-zA-Z])*$'
REG_STATUS = 'waiting for loading|on the way|handed to the customer'
saved_name = ''
saved_model = ''

saved_surname = ''
saved_name_manager = ''

saved_order_item_id = ''
saved_order_item_amount = ''

saved_order_list_order_id = ''
saved_order_list_manager_id = ''
saved_order_list_date = ''
saved_order_list_status = ''


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
    four_input = StringField(label="Status (waiting for loading/on the way/handed to the customer)")
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


def save_condition_item_name(string):
    global saved_name
    saved_name = string


def get_condition_item_name():
    return saved_name


def save_condition_item_model(string):
    global saved_model
    saved_model = string


def get_condition_item_model():
    return saved_model


def save_condition_manager_surname(string):
    global saved_surname
    saved_surname = string


def get_condition_manager_surname():
    return saved_surname


def save_condition_manager_name(string):
    global saved_name_manager
    saved_name_manager = string


def get_condition_manager_name():
    return saved_name_manager


def save_condition_order_item_id(string):
    global saved_order_item_id
    saved_order_item_id = string


def get_condition_order_item_id():
    return saved_order_item_id


def save_condition_order_item_amount(string):
    global saved_order_item_amount
    saved_order_item_amount = string


def get_condition_order_item_amount():
    return saved_order_item_amount


def save_condition_order_list_order_item_id(string):
    global saved_order_list_order_id
    saved_order_list_order_id = string


def get_condition_order_list_order_item_id():
    return saved_order_list_order_id


def save_condition_order_list_manager_id(string):
    global saved_order_list_manager_id
    saved_order_list_manager_id = string


def get_condition_order_list_manager_id():
    return saved_order_list_manager_id


def save_condition_order_list_date(string):
    global saved_order_list_date
    saved_order_list_date = string


def get_condition_order_list_date():
    return saved_order_list_date


def save_condition_order_list_status(string):
    global saved_order_list_status
    saved_order_list_status = string


def get_condition_order_list_status():
    return saved_order_list_status


@app.route('/statistic')
def statistic():
    will_delivered = db.session.query(Order_list).filter(Order_list.status == 'handed to the customer').count()
    on_the_way = db.session.query(Order_list).filter(Order_list.status == 'on the way').count()
    waiting_for_loading = db.session.query(Order_list).filter(Order_list.status == 'waiting for loading').count()
    total = db.session.query(Order_list).count()
    status = [will_delivered, on_the_way, waiting_for_loading, total]

    save_item_id = -1
    max_item = db.session.query(func.count(Order_item.item_id).label('item_id')). \
        group_by(Order_item.item_id).order_by(desc('item_id')).first()
    for i in range(0, db.session.query(Order_item).count() * 2):
        count = db.session.query(Order_item).filter(Order_item.item_id == i).count()
        if count == max_item[0]:
            save_item_id = i

    item = get_item_id_post(save_item_id)

    max_manager = db.session.query(func.count(Order_list.manager_id).label('manager_id')). \
        group_by(Order_list.manager_id).order_by(desc('manager_id')).first()
    for i in range(0, db.session.query(Order_list).count() * 2):
        count = db.session.query(Order_list).filter(Order_list.manager_id == i).count()
        if count == max_manager[0]:
            save_item_id = i

    manager = get_manager_id_post(save_item_id)
    return render_template('statistic.html', status=status, item=item, manager=manager)


#  ###########
#  #Item part#
#  ###########


@app.route('/', methods=('GET', 'POST'))
def show_items():
    form = CreateItem()
    page = request.args.get('page', 1, type=int)

    name = form.first_input.data
    model = form.second_input.data

    if name is not None:
        save_condition_item_name(name)

    if model is not None:
        save_condition_item_model(model)

    if request.method == 'POST' or (name is None and model is None):

        items = db.session.query(Item)

        name = get_condition_item_name()
        model = get_condition_item_model()
        if not name == '' and model == '':
            items = items.filter(Item.item_name == name)
            if db.session.query(Item).filter(Item.item_name == name).count() == 0:
                items = db.session.query(Item)
                flash('This item does not exist')

        if not model == '' and name == '':
            items = items.filter(Item.item_model == model)
            if db.session.query(Item).filter(Item.item_model == model).count() == 0:
                items = db.session.query(Item)
                flash('This item does not exist')

        if not name == '' and not model == '':
            items = db.session.query(Item).filter(Item.item_name == name).filter(Item.item_model == model)
            if db.session.query(Item).filter(Item.item_name == name).filter(Item.item_model == model).count() == 0:
                items = db.session.query(Item)
                flash('This item does not exist')

    return render_template('index_item.html', item=items.paginate(page=page, per_page=5), form=form)


@app.route('/create', methods=('GET', 'POST'))
def create():
    form = CreateItem()
    if form.validate_on_submit() and request.method == 'POST':
        if not form.first_input.data or not form.second_input.data:
            flash('You must fill all fields!')
        else:
            new_name = form.first_input.data
            new_model = form.second_input.data
            if re.fullmatch(REG_ITEM, new_name) and re.fullmatch(REG_ITEM, new_model):
                new_item = Item(item_name=f"{new_name}", item_model=f"{new_model}")
                form.populate_obj(new_item)
                db.session.add(new_item)
                db.session.commit()
                return redirect(url_for('show_items'))
            else:
                flash('Invalid input data (probably name or model input has spacebars)')
    return render_template('create_item.html', form=form)


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
        if re.fullmatch(REG_ITEM, new_name) and re.fullmatch(REG_ITEM, new_model):
            now_item = db.session.query(Item).filter(Item.item_id == id).first()
            now_item.item_name = new_name
            now_item.item_model = new_model
            db.session.commit()
            return redirect(url_for('show_items'))
        else:
            flash('Invalid input data')
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


@app.route('/All_manager_list', methods=('GET', 'POST'))
def index_manager():
    form = CreateManager()
    page = request.args.get('page', 1, type=int)

    surname = form.first_input.data
    name = form.second_input.data

    if surname is not None:
        save_condition_manager_surname(surname)

    if name is not None:
        save_condition_manager_name(name)

    if request.method == 'POST' or (surname is None and name is None):

        items = db.session.query(Manager)

        surname = get_condition_manager_surname()
        name = get_condition_manager_name()
        if not surname == '' and name == '':
            items = items.filter(Manager.surname == surname)
            if db.session.query(Manager).filter(Manager.surname == surname).count() == 0:
                items = db.session.query(Manager)
                flash('This manager does not exist')

        if not name == '' and surname == '':
            items = items.filter(Manager.name == name)
            if db.session.query(Manager).filter(Manager.name == name).count() == 0:
                items = db.session.query(Manager)
                flash('This manager does not exist')

        if not surname == '' and not name == '':
            items = db.session.query(Manager).filter(Manager.surname == surname).filter(Manager.name == name)
            if db.session.query(Manager).filter(Manager.surname == surname).filter(Manager.name == name).count() == 0:
                items = db.session.query(Manager)
                flash('This manager does not exist')

    return render_template('index_manager.html', item=items.paginate(page=page, per_page=5), form=form)


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
        if re.fullmatch(REG_MANAGER_NAME_OR_SURNAME, new_surname) and \
                re.fullmatch(REG_MANAGER_NAME_OR_SURNAME, new_name):
            now_manager = db.session.query(Manager).filter(Manager.manager_id == id).first()
            now_manager.surname = new_surname
            now_manager.name = new_name
            db.session.commit()
            return redirect(url_for('index_manager'))
        else:
            flash('Invalid input data')
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
            if re.fullmatch(REG_MANAGER_NAME_OR_SURNAME, new_surname) and \
                    re.fullmatch(REG_MANAGER_NAME_OR_SURNAME, new_name):
                new_manager = Manager(surname=f"{new_surname}", name=f"{new_name}")
                form.populate_obj(new_manager)
                db.session.add(new_manager)
                db.session.commit()
                return redirect(url_for('index_manager'))
            else:
                flash('Invalid input data')
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


@app.route('/All_order_item', methods=('GET', 'POST'))
def index_order_item():
    form = CreateOrderItem()
    page = request.args.get('page', 1, type=int)

    item_id = form.first_input.data
    amount = form.second_input.data

    if item_id is not None:
        save_condition_order_item_id(item_id)

    if amount is not None:
        save_condition_order_item_amount(amount)

    if request.method == 'POST' or (item_id is None and amount is None):

        items = db.session.query(Order_item)

        item_id = get_condition_order_item_id()
        amount = get_condition_order_item_amount()
        print(amount)
        if (not item_id.isdigit() and not item_id == '') or (not amount.isdigit() and not amount == ''):
            flash('You must enter positive integer!')

        if not item_id == '' and amount == '':
            items = items.filter(Order_item.item_id == item_id)
            if db.session.query(Order_item).filter(Order_item.item_id == item_id).count() == 0:
                items = db.session.query(Order_item)
                flash('This order item does not exist')

        if not amount == '' and item_id == '':
            items = items.filter(Order_item.amount == amount)
            if db.session.query(Order_item).filter(Order_item.amount == amount).count() == 0:
                items = db.session.query(Order_item)
                flash('This order item does not exist')

        if not item_id == '' and not amount == '':
            items = db.session.query(Order_item).filter(Order_item.item_id == item_id).filter(
                Order_item.amount == amount)
            if db.session.query(Order_item).filter(Order_item.item_id == item_id).filter(
                    Order_item.amount == amount).count() == 0:
                items = db.session.query(Order_item)
                flash('This order item does not exist')

    return render_template('index_order_item.html', item=items.paginate(page=page, per_page=5), form=form)
    # return render_template('index_order_item.html', item=db.session.query(Order_item).all())


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
            if db.session.query(Item).filter(Item.item_id == new_item_id).first() is not None:
                now_order_item = db.session.query(Order_item).filter(Order_item.order_id == id).first()
                now_order_item.item_id = new_item_id
                now_order_item.amount = new_amount
                db.session.commit()
                return redirect(url_for('index_order_item'))
            else:
                flash('Item with this ID does not exist now!')
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
            if form.first_input.data.isdigit() and form.first_input.data.isdigit():
                new_item_id = form.first_input.data
                new_amount = form.second_input.data
                if new_item_id.isdigit() and new_item_id.isdigit():
                    if db.session.query(Item).filter(Item.item_id == new_item_id).first() is not None:
                        new_order = Order_item(item_id=f"{new_item_id}", amount=f"{new_amount}")
                        form.populate_obj(new_order)
                        db.session.add(new_order)
                        db.session.commit()
                        return redirect(url_for('index_order_item'))
                    else:
                        flash('Item with this ID does not exist now!')
                else:
                    flash('You must enter positive integer!')
            else:
                flash('You must enter positive integer!')

    return render_template('create_order_item.html', form=form)


#  #################
#  #Order item part#
#  #################


#  #################
#  #Order list part#
#  #################


@app.route('/All order list', methods=('GET', 'POST'))
def index_order_list():
    form = CreateOrderList()
    page = request.args.get('page', 1, type=int)

    order_id = form.first_input.data
    manager_id = form.second_input.data
    date = form.third_input.data
    status = form.four_input.data

    if order_id is not None:
        save_condition_order_list_order_item_id(order_id)

    if manager_id is not None:
        save_condition_order_list_manager_id(manager_id)

    if date is not None:
        save_condition_order_list_date(date)

    if status is not None:
        save_condition_order_list_status(status)

    if request.method == 'POST' or (order_id is None and manager_id is None and date is None and status is None):

        items = db.session.query(Order_list)

        order_id = get_condition_order_list_order_item_id()
        manager_id = get_condition_order_list_manager_id()
        date = get_condition_order_list_date()
        status = get_condition_order_list_status()

        if (not order_id.isdigit() and not order_id == '') or (not manager_id.isdigit() and not manager_id == ''):
            flash('You must enter positive integer!')

        if not order_id == '' and manager_id == '' and date == '' and status == '':
            items = items.filter(Order_list.order_id == order_id)
            if db.session.query(Order_list).filter(Order_list.order_id == order_id).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if not manager_id == '' and order_id == '' and date == '' and status == '':
            items = items.filter(Order_list.manager_id == manager_id)
            if db.session.query(Order_list).filter(Order_list.manager_id == manager_id).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if not order_id == '' and not manager_id == '' and date == '' and status == '':
            items = db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                Order_list.manager_id == manager_id)
            if db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                    Order_list.manager_id == manager_id).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if not order_id == '' and manager_id == '' and date == '' and not status == '':
            items = db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                Order_list.status == status)
            if db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                    Order_list.status == status).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if order_id == '' and not manager_id == '' and not date == '' and status == '':
            items = db.session.query(Order_list).filter(Order_list.manager_id == manager_id).filter(
                Order_list.order_date == date)
            if db.session.query(Order_list).filter(Order_list.manager_id == manager_id).filter(
                    Order_list.order_date == date).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if order_id == '' and not manager_id == '' and date == '' and not status == '':
            items = db.session.query(Order_list).filter(Order_list.manager_id == manager_id).filter(
                Order_list.status == status)
            if db.session.query(Order_list).filter(Order_list.manager_id == manager_id).filter(
                    Order_list.status == status).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if order_id == '' and manager_id == '' and not date == '' and status == '':
            items = items.filter(Order_list.order_date == date)
            if db.session.query(Order_list).filter(Order_list.order_date == date).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if order_id == '' and manager_id == '' and date == '' and not status == '':
            items = items.filter(Order_list.status == status)
            if db.session.query(Order_list).filter(Order_list.status == status).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if order_id == '' and manager_id == '' and not date == '' and not status == '':
            items = db.session.query(Order_list).filter(Order_list.order_date == date).filter(
                Order_list.status == status)
            if db.session.query(Order_list).filter(Order_list.order_date == date).filter(
                    Order_list.status == status).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if not order_id == '' and not manager_id == '' and not date == '' and status == '':
            items = db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                Order_list.manager_id == manager_id).filter(Order_list.order_date == date)
            if db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                    Order_list.manager_id == manager_id).filter(Order_list.order_date == date).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if not order_id == '' and not manager_id == '' and date == '' and not status == '':
            items = db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                Order_list.manager_id == manager_id).filter(Order_list.status == status)
            if db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                    Order_list.manager_id == manager_id).filter(Order_list.status == status).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if not order_id == '' and manager_id == '' and not date == '' and not status == '':
            items = db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                Order_list.order_date == date).filter(Order_list.status == status)
            if db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                    Order_list.order_date == date).filter(Order_list.status == status).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if order_id == '' and not manager_id == '' and not date == '' and not status == '':
            items = db.session.query(Order_list).filter(Order_list.manager_id == manager_id).filter(
                Order_list.order_date == date).filter(Order_list.status == status)
            if db.session.query(Order_list).filter(Order_list.manager_id == manager_id).filter(
                    Order_list.order_date == date).filter(Order_list.status == status).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

        if not order_id == '' and not manager_id == '' and not date == '' and not status == '':
            items = db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                Order_list.manager_id == manager_id).filter(Order_list.order_date == date).filter(
                    Order_list.status == status)

            if db.session.query(Order_list).filter(Order_list.order_id == order_id).filter(
                Order_list.manager_id == manager_id).filter(Order_list.order_date == date).filter(
                    Order_list.status == status).count() == 0:
                items = db.session.query(Order_list)
                flash('This order list does not exist')

    return render_template('index_order_list.html', item=items.paginate(page=page, per_page=5), form=form)
    # return render_template('index_order_list.html', item=db.session.query(Order_list).all())


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
            correct_id = True

            if not new_order_id.isdigit() or not new_manager_id.isdigit():
                correct_id = False

            if correct_id:
                if re.fullmatch(REG_DATE, new_order_date) and re.fullmatch(REG_STATUS, new_status):
                    if db.session.query(Order_item).filter(Order_item.order_id == new_order_id).first() is not None:
                        if db.session.query(Manager).filter(Manager.manager_id == new_manager_id).first() is not None:
                            new_order_list = Order_list(order_id=f"{new_order_id}", manager_id=f"{new_manager_id}",
                                                        order_date=f"{new_order_date}", status=f"{new_status}")
                            form.populate_obj(new_order_list)
                            db.session.add(new_order_list)
                            db.session.commit()
                            return redirect(url_for('index_order_list'))
                        else:
                            flash('Manager with this ID does not exist now!')
                    else:
                        flash('Order item with this ID does not exist now!')
                else:
                    flash('Invalid input date(dd.mm.yyyy) or status')
            else:
                flash('ID must be positive integer!')
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
        correct_id = True

        if not new_order_id.isdigit() or not new_manager_id.isdigit():
            correct_id = False

        if correct_id:
            if re.fullmatch(REG_DATE, new_order_date) and re.fullmatch(REG_STATUS, new_status):
                if db.session.query(Order_item).filter(Order_item.order_id == new_order_id).first() is not None:
                    if db.session.query(Manager).filter(Manager.manager_id == new_manager_id).first() is not None:

                        now_order_list = db.session.query(Order_list).filter(Order_list.order_list_id == id).first()

                        now_order_list.order_id = new_order_id
                        now_order_list.manager_id = new_manager_id
                        now_order_list.order_date = new_order_date
                        now_order_list.status = new_status
                        db.session.commit()
                        return redirect(url_for('index_order_list'))
                    else:
                        flash('Manager with this ID does not exist now!')
                else:
                    flash('Order item with this ID does not exist now!')
            else:
                flash('Invalid input date(dd.mm.yyyy) or status')
        else:
            flash('ID must be positive integer!')

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
    cursor = connect_base().cursor()
    app.run(debug=True)
