from random import SystemRandom


# Reused approach from Notify https://github.com/alphagov/notifications-api/blob/master/app/dao/users_dao.py#L18
def generate_code():
    return ''.join(map(str, [SystemRandom().randrange(10) for i in range(5)]))
