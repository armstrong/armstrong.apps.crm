class NoopBackend(object):
    def __init__(self, backend):
        self.backend = backend

    def created(self, payload):
        pass

    def updated(self, payload):
        pass

    def deleted(self, payload):
        pass


class GenericBackend(NoopBackend):
    def created(self, payload):
        raise NotImplementedError()

    def updated(self, payload):
        raise NotImplementedError()

    def deleted(self, payload):
        raise NotImplementedError()


class UserBackend(GenericBackend):
    pass


class GroupBackend(GenericBackend):
    pass


class Backend(object):
    user_class = UserBackend
    group_class = GroupBackend

    def __init__(self, *args, **kwargs):
        self._user = None
        self._group = None

    def get_user(self):
        return self.user_class(self)

    @property
    def user(self):
        if not self._user:
            self._user = self.get_user()
        return self._user

    def get_group(self):
        return self.group_class(self)

    @property
    def group(self):
        if not self._group:
            self._group = self.get_group()
        return self._group


def get_backend():
    return Backend()
