import json
import random

from faker import Faker
from locust import FastHttpUser, between, task
from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory

from app.models.coffee import Coffee
from app.models.user import User

fake = Faker()


class CoffeeFactory(ModelFactory):
    __faker__ = fake
    __model__ = Coffee

    id = Ignore()


class UserFactory(ModelFactory):
    __faker__ = fake
    __model__ = User

    id = Ignore()
    coffee_id = Ignore()


class CoffeeUser(FastHttpUser):
    wait_time = between(1, 3)

    @task(2)
    def create_coffee(self):
        self.client.post(
            url="/coffee/",
            json=json.loads(CoffeeFactory().build().model_dump_json()),
            name="create_coffee",
        )

    @task
    def search_coffee(self):
        self.client.get(
            url="/coffee/",
            name="search_coffee",
        )

    @task
    def get_coffee_by_id(self):
        self.client.get(
            url=f"/coffee/{random.randint(1, 100)}",
            name="get_coffee_by_id",
        )

    @task
    def update_coffee(self):
        self.client.put(
            url=f"/coffee/{random.randint(1, 100)}",
            json=json.loads(CoffeeFactory().build().model_dump_json(exclude_unset=True)),
            name="update_coffee",
        )

    @task
    def delete_coffee(self):
        self.client.delete(
            url=f"/coffee/{random.randint(1, 10000)}",
            name="delete_coffee",
        )


class UsersUser(FastHttpUser):
    wait_time = between(1, 3)

    @task(2)
    def create_user(self):
        self.client.post(
            url="/users/",
            json=json.loads(UserFactory().build().model_dump_json()),
            name="create_user",
        )

    @task
    def search_users(self):
        self.client.get(
            url="/users/",
            name="search_users",
        )

    @task
    def get_user_by_id(self):
        self.client.get(
            url=f"/users/{random.randint(1, 100)}",
            name="get_user_by_id",
        )

    @task
    def update_user(self):
        self.client.put(
            url=f"/users/{random.randint(1, 100)}",
            json=json.loads(UserFactory().build().model_dump_json(exclude_unset=True)),
            name="update_user",
        )

    @task
    def delete_user(self):
        self.client.delete(
            url=f"/users/{random.randint(1, 10000)}",
            name="delete_user",
        )


class PublishUser(FastHttpUser):
    wait_time = between(1, 10)

    @task
    def publish_coffee(self):
        self.client.get(
            url="/publish_coffee/",
            name="publish_coffee",
        )
