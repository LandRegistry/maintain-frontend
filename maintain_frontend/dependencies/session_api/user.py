class User(object):
    """Model to hold logged in user details."""

    def __init__(self):
        """Initialize User object."""
        self.id = None
        self.first_name = None
        self.surname = None
        self.full_name = None
        self.email = None
        self.organisation = None
        self.roles = None
        self.status = None
        self.is_admin = None
        self.permissions = []
        self.jwt = None

    def check_admin(self):
        admin_roles = ["LLC LR Admins", "LLC LA Admins"]
        return any(role in self.roles for role in admin_roles)

    def is_lr(self):
        lr_roles = ["LLC LR Admins", "LLC LR Users"]
        return any(role in self.roles for role in lr_roles)

    def get_author_info(self):
        return {
            "full-name": self.full_name,
            "email": self.email,
            "organisation": self.organisation
        }

    @staticmethod
    def from_dict(user_json):
        """Builds user object from json dictionary.


        :param user_json: Json dictionary holding user information.
        :return: user object.
        """
        user = User()
        user.id = user_json['id']
        user.first_name = user_json['first_name']
        user.surname = user_json['surname']
        user.full_name = "{} {}".format(user.first_name, user.surname)
        user.email = user_json['email']
        user.organisation = user_json['organisation']
        user.roles = user_json['roles']
        user.status = user_json['status']
        user.is_admin = user.check_admin()
        user.jwt = user_json['jwt']
        if 'permissions' in user_json:
            user.permissions = user_json['permissions']

        return user
