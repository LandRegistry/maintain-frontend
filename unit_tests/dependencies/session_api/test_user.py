from maintain_frontend.dependencies.session_api.user import User
from unittest import TestCase


class TestUserDomain(TestCase):

    def test_user_initialisation(self):
        user = User()
        user.id = 'id'
        user.first_name = 'joe'
        user.surname = 'bloggs'
        user.email = 'email'
        user.organisation = 'testorg'
        user.roles = ['testrole']
        user.status = 'Active'
        user.jwt = "MOCK.JWT"

        self.assertIsNotNone(user)
        self.assertEqual(user.id, 'id')
        self.assertEqual(user.first_name, 'joe')
        self.assertEqual(user.surname, 'bloggs')
        self.assertEqual(user.email, 'email')
        self.assertEqual(user.organisation, 'testorg')
        self.assertEqual(user.roles, ['testrole'])
        self.assertEqual(user.status, 'Active')
        self.assertEqual(user.jwt, 'MOCK.JWT')

    def test_user_from_json(self):
        test = dict()
        test["id"] = 'id'
        test["first_name"] = "joe"
        test["surname"] = "bloggs"
        test["email"] = "testemail"
        test["organisation"] = "testorg"
        test["roles"] = ["testrole"]
        test["status"] = "Active"
        test["jwt"] = "MOCK.JWT"

        user = User.from_dict(test)

        self.assertEqual(user.id, 'id')
        self.assertEqual(user.first_name, "joe")
        self.assertEqual(user.surname, "bloggs")
        self.assertEqual(user.email, "testemail")
        self.assertEqual(user.organisation, "testorg")
        self.assertEqual(user.roles, ['testrole'])
        self.assertEqual(user.status, "Active")
        self.assertEqual(user.jwt, "MOCK.JWT")
