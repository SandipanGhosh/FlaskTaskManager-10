# db_create.py

from project import db
from project.models import Task, User
from datetime import date

# create db and table
db.create_all()

# insert data
#db.session.add(User("admin", "admin@js.com", "admin", "admin"))
#db.session.add(Task("Finish this tutorial", date(2018, 1, 26), 10, date(2018, 1, 26), 1, 1))
#db.session.add(Task("Finish this course", date(2018, 1, 31), 10, date(2018, 1, 31), 1, 1))

# commit changes
db.session.commit()