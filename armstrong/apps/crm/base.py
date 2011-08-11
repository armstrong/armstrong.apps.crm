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
    def activated(self, payload):
        pass

    def registered(self, payload):
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


def dispatch_delete_signal(sender, **kwargs):
    getattr(get_backend(), sender._meta.module_name).deleted(kwargs)


def dispatch_user_activated(sender, **kwargs):
    get_backend().user.activated(kwargs)


def dispatch_user_registered(sender, **kwargs):
    get_backend().user.registered(kwargs)


def activate():
    from django.db.models.signals import post_delete
    from django.db.models.signals import post_save
    from django.contrib.auth.models import Group
    from django.contrib.auth.models import User
    post_save.connect(dispatch_post_save_signal, sender=User)
    post_save.connect(dispatch_post_save_signal, sender=Group)

    post_delete.connect(dispatch_delete_signal, sender=User)
    post_delete.connect(dispatch_delete_signal, sender=Group)

    try:
        from registration.signals import user_activated
        from registration.signals import user_registered
        user_activated.connect(dispatch_user_activated)
        user_registered.connect(dispatch_user_registered)
    except ImportError:
        pass
