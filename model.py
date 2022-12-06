from config import db


class Item(db.Model):
    __tablename__ = "item"
    item_id = db.Column('item_id', db.INTEGER, primary_key=True, autoincrement=True)
    item_name = db.Column('item_name', db.Text)
    item_model = db.Column('item_model', db.Text)


class Manager(db.Model):
    __tablename__ = "manager"
    manager_id = db.Column('manager_id', db.INTEGER, primary_key=True, autoincrement=True)
    surname = db.Column('surname', db.Text)
    name = db.Column('name', db.Text)


class Order_item(db.Model):
    __tablename__ = "order_item"
    order_id = db.Column('order_id', db.INTEGER, primary_key=True, autoincrement=True)
    item_id = db.Column(db.ForeignKey(Item.item_id))
    amount = db.Column('amount_of_items_at_order', db.INTEGER)


class Order_list(db.Model):
    __tablename__ = "order_list"
    order_list_id = db.Column('order_list_id', db.INTEGER, primary_key=True, autoincrement=True)
    order_id = db.Column(db.ForeignKey(Order_item.order_id))
    manager_id = db.Column(db.ForeignKey(Manager.manager_id))
    order_date = db.Column('order_date', db.Text)
    status = db.Column('status', db.Text)


def get_item_id():
    return str(Item.item_id)


def get_manager_id():
    return str(Manager.manager_id)


def get_order_id():
    return str(Order_item.order_id)


def get_order_list_id():
    return str(Order_list.order_id)


