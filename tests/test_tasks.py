# project/test_tasks.py


import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import Task, User

TEST_DB = 'test.db'


class TasksTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()
        self.assertEquals(app.debug, False)

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()


    ########################
    #### helper methods ####
    ########################

    def login(self, name, password):
        return self.app.post('/', data=dict(
            name=name, password=password), follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post(
            'register/',
            data=dict(name=name, email=email, password=password, confirm=confirm),
            follow_redirects=True
        )

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        return self.app.post('add/', data=dict(
            name='Create unit test cases.',
            due_date='02/02/2018',
            priority='1',
            posted_date='02/02/2018',
            status='1'
        ), follow_redirects=True)

    def create_admin_user(self):
        new_user = User(
            name='Superuser',
            email='admin@su.com',
            password=bcrypt.generate_password_hash('superuser'),
            role='admin'
        )
        db.session.add(new_user)
        db.session.commit()


    ###############
    #### tests ####
    ###############
    '''
    def test_logged_in_users_can_access_tasks_page(self):
        self.register(
            'John', 'john@js.com', 'python101', 'python101'
        )
        self.login('John', 'python101')
        response = self.app.get('tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)
    '''
    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'You need to login first.', response.data)

    def test_users_can_add_tasks(self):
        self.create_user('Smith', 'smith@js.com', 'python')
        self.login('Smith', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(
            b'New entry was successfully posted.', response.data
        )

    def test_users_cannot_add_tasks_when_error(self):
        self.create_user('Smith', 'smith@js.com', 'python')
        self.login('Smith', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.post('add/', data=dict(
            name='Create unit test cases.',
            due_date='',
            priority='1',
            posted_date='02/02/2018',
            status='1'
        ), follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        self.create_user('Smith', 'smith@js.com', 'python')
        self.login('Smith', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertIn(b'The task is complete.', response.data)

    def test_users_can_delete_tasks(self):
        self.create_user('Smith', 'smith@js.com', 'python')
        self.login('Smith', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Smith', 'smith@js.com', 'python')
        self.login('Smith', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('John', 'john@js.com', 'python101')
        self.login('John', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(
            b'The task is complete.', response.data
        )
        self.assertIn(
            b'You can only update tasks that belong to you.', response.data
        )

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Smith', 'smith@js.com', 'python')
        self.login('Smith', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('John', 'john@js.com', 'python101')
        self.login('John', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn(
            b'You can only delete tasks that belong to you.', response.data
        )

    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Smith', 'smith@js.com', 'python')
        self.login('Smith', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superuser', 'superuser')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(
            b'You can only update tasks that belong to you.', response.data
        )

    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Smith', 'smith@js.com', 'python')
        self.login('Smith', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superuser', 'superuser')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertNotIn(
            b'You can only delete tasks that belong to you.', response.data
        )
    '''
    def test_task_template_displays_logged_in_user_name(self):
        self.register('John', 'john@js.com', 'python', 'python')
        self.login('John', 'python')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'John', response.data)

    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        self.register('John', 'john@js.com', 'python', 'python')
        self.login('John', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register(
        'Smith', 'smith@js.com', 'python101', 'python101'
        )
        response = self.login('Smith', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        self.assertNotIn(b'Mark as complete', response.data)
        self.assertNotIn(b'Delete', response.data)

    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        self.register('John', 'john@js.com', 'python', 'python')
        self.login('John', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register(
        'Smith', 'smith@js.com', 'python101', 'python101'
        )
        self.login('Smith', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'complete/2/', response.data)

    def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
        self.register('John', 'john@js.com', 'python', 'python')
        self.login('John', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superuser', 'superuser')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/1/', response.data)
        self.assertIn(b'delete/1/', response.data)
        self.assertIn(b'complete/2/', response.data)

    def test_string_reprsentation_of_the_task_object(self):

       from datetime import date
       db.session.add(
           Task(
               "Run around in circles",
               date(2018, 2, 2),
               10,
               date(2018, 2, 2),
               1,
               1
           )
       )
       db.session.commit()

       tasks = db.session.query(Task).all()
       for task in tasks:
           self.assertEqual(task.name, 'Run around in circles')
    '''

if __name__ == "__main__":
    unittest.main()