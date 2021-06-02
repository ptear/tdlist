from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL
import datetime
import dateutil.parser

app = Flask(__name__)
app.config['SECRET_KEY'] = "seeeccccreeett"
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class TDList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(500), nullable=False)
    date_due = db.Column(db.String(250), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)


class TaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    date_due = StringField("Date", validators=[DataRequired()])
    completed = BooleanField("Completed?")
    submit = SubmitField("Add / Edit")


# db.create_all()


def func(e):
    return e.date_due


@app.route("/")
def home():
    td_list = TDList.query.all()
    for item in td_list:
        item.date_due = dateutil.parser.parse(item.date_due)
    td_list.sort(key=func)
    for item in td_list:
        item.date_due = item.date_due.strftime("%d/%m/%Y")
    return render_template("index.html", td_list=td_list)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = TaskForm()
    if form.validate_on_submit():
        dt_date = dateutil.parser.parse(form.date_due.data)
        str_date = dt_date.strftime("%d/%m/%Y")
        new_task = TDList(
            task=form.task.data,
            date_due=str_date,
            completed=form.completed.data
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form)


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    task_to_edit = TDList.query.get(task_id)
    form = TaskForm(
        task=task_to_edit.task,
        date_due=task_to_edit.date_due
    )
    if form.validate_on_submit():
        dt_date = dateutil.parser.parse(form.date_due.data)
        str_date = dt_date.strftime("%d/%m/%Y")
        task_to_edit.task = form.task.data
        task_to_edit.date_due = str_date
        task_to_edit.completed = form.completed.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form)


@app.route("/delete/<int:task_id>")
def delete(task_id):
    task_to_delete = TDList.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()
