from armstrong.utils.backends import GenericBackend


class BaseBackend(object):
    def __init__(self, backend):
        self.backend = backend


class UserBackend(BaseBackend):
    def created(self, user, payload):
        pass

    def updated(self, user, payload):
        pass

    def deleted(self, user, payload):
        pass

    def activated(self, user, payload):
        pass

    def registered(self, user, payload):
        pass


class GroupBackend(BaseBackend):
    def created(self, group, payload):
        pass

    def updated(self, group, payload):
        pass

    def deleted(self, group, payload):
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


backend = GenericBackend("ARMSTRONG_CRM_BACKEND",
        defaults="%s.Backend" % __name__)

get_backend = backend.get_backend


def dispatch_post_save_signal(sender, **kwargs):
    created = kwargs.pop("created", False)
    model = kwargs["instance"]
    backend = getattr(get_backend(), sender._meta.module_name)
    getattr(backend, "created" if created else "updated")(model, kwargs)


def dispatch_delete_signal(sender, **kwargs):
    model = kwargs["instance"]
    getattr(get_backend(), sender._meta.module_name).deleted(model, kwargs)


def dispatch_user_activated(sender, **kwargs):
    user = kwargs["user"]
    get_backend().user.activated(user, kwargs)


def dispatch_user_registered(sender, **kwargs):
    user = kwargs["user"]
    get_backend().user.registered(user, kwargs)


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
