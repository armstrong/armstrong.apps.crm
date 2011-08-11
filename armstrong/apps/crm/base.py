from armstrong.utils.backends import GenericBackend as ArmstrongGenericBackend


class GenericBackend(object):
    def __init__(self, backend):
        self.backend = backend

    def created(self, payload):
        pass

    def updated(self, payload):
        pass

    def deleted(self, payload):
        pass


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


backend = ArmstrongGenericBackend("ARMSTRONG_CRM_BACKEND",
        defaults="%s.Backend" % __name__)

get_backend = backend.get_backend


def dispatch_post_save_signal(sender, **kwargs):
    created = kwargs.pop("created", False)
    backend = getattr(get_backend(), sender._meta.module_name)
    getattr(backend, "created" if created else "updated")(kwargs)


def activate():
    from django.db.models.signals import post_save
    from django.contrib.auth.models import Group
    from django.contrib.auth.models import User
    post_save.connect(dispatch_post_save_signal, sender=User)
    post_save.connect(dispatch_post_save_signal, sender=Group)
