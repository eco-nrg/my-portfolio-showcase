def authorized(func):
    def wrapper(self, *args, **kwargs):
        user = self.scope.get('user')
        if user and user.is_anonymous:
            self.send_error(message='Пользователь не авторизован')
        else:
            func(self, *args, **kwargs)

    return wrapper
