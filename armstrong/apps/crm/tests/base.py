from contextlib import contextmanager
import datetime
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
import fudge
from fudge.inspector import arg
from ._utils import TestCase

from .. import base


@contextmanager
def verified_mocks():
    fudge.clear_expectations
    fudge.clear_calls()
    yield
    fudge.verify()


@contextmanager
def fake_user_class(verify=True):
    random_object = object()
    user_class = fudge.Fake()
    user_class.is_callable().expects_call().times_called(1) \
            .returns(random_object)
    if verify:
        with verified_mocks():
            yield (user_class, random_object)
    else:
        yield (user_class, random_object)


@contextmanager
def fake_group_class(verify=True):
    random_object = object()
    group_class = fudge.Fake()
    group_class.is_callable().expects_call().times_called(1) \
            .returns(random_object)
    if verify:
        with verified_mocks():
            yield (group_class, random_object)
    else:
        yield (group_class, random_object)


class BackendTestCase(TestCase):
    def test_returns_user_class_instance(self):
        with fake_user_class() as (user_class, random_object):
            b = base.Backend()
            b.user_class = user_class
            self.assertEqual(b.user, random_object)

    def test_only_instantiates_one_user_backend(self):
        with fake_user_class() as (user_class, random_object):
            b = base.Backend()
            b.user_class = user_class
            b.user
            b.user, "this will raise an error if not memoized"

    def test_backend_is_passed_to_user_backend(self):
        with fake_user_class(verify=False) as (user_class, random_object):
            b = base.Backend()
            user_class.with_args(b)
            b.user_class = user_class
            with verified_mocks():
                b.user, "make sure the backend was provide to the user_class"

    def test_provides_UserBackend_by_default(self):
        b = base.Backend()
        self.assertIsA(b.user, base.UserBackend)

    def test_returns_group_class_instance(self):
        with fake_group_class() as (group_class, random_object):
            b = base.Backend()
            b.group_class = group_class
            self.assertEqual(b.group, random_object)

    def test_only_instantiates_one_group_backend(self):
        with fake_group_class() as (group_class, random_object):
            b = base.Backend()
            b.group_class = group_class
            b.group
            b.group, "this will raise an error if not memoized"

    def test_backend_is_passed_to_group_backend(self):
        with fake_group_class(verify=False) as (group_class, random_object):
            b = base.Backend()
            group_class.with_args(b)
            b.group_class = group_class
            with verified_mocks():
                b.group, "make sure the backend was provide to the group_class"

    def test_provides_GroupBackend_by_default(self):
        b = base.Backend()
        self.assertIsA(b.group, base.GroupBackend)

    def test_subclasses_can_control_what_user_class_is_used(self):
        class MySpecialUserBackend(base.UserBackend):
            pass

        class MySpecialSubClass(base.Backend):
            user_class = MySpecialUserBackend

        b = MySpecialSubClass()
        self.assertIsA(b.user, MySpecialUserBackend)

        self.assertIsA(base.Backend().user, base.UserBackend,
                msg="sanity check to make sure subclasses don't bleed through")

    def test_subclasses_can_control_what_group_class_is_used(self):
        class MySpecialGroupBackend(base.GroupBackend):
            pass

        class MySpecialSubClass(base.Backend):
            group_class = MySpecialGroupBackend

        b = MySpecialSubClass()
        self.assertIsA(b.group, MySpecialGroupBackend)

        self.assertIsA(base.Backend().group, base.GroupBackend,
                msg="sanity check to make sure subclasses don't bleed through")


class UserBackendTestCase(TestCase):
    def generate_random_user_backend(self):
        r = object()
        return base.UserBackend(r)

    def test_sets_backend_to_provided_value(self):
        random_object = object()
        user_backend = base.UserBackend(random_object)
        self.assertEqual(user_backend.backend, random_object)

    def test_created_returns_none(self):
        user_backend = self.generate_random_user_backend()
        self.assertNone(user_backend.created({}))

    def test_updated_raises_none(self):
        user_backend = self.generate_random_user_backend()
        self.assertNone(user_backend.updated({}))

    def test_deleted_raises_none(self):
        user_backend = self.generate_random_user_backend()
        self.assertNone(user_backend.deleted({}))


class GroupBackendTestCase(TestCase):
    def generate_random_group_backend(self):
        r = object()
        return base.GroupBackend(r)

    def test_sets_backend_to_provided_value(self):
        random_object = object()
        group_backend = base.GroupBackend(random_object)
        self.assertEqual(group_backend.backend, random_object)

    def test_updated_raises_none(self):
        group_backend = self.generate_random_group_backend()
        self.assertNone(group_backend.updated({}))

    def test_updated_raises_none(self):
        group_backend = self.generate_random_group_backend()
        self.assertNone(group_backend.updated({}))

    def test_deleted_raises_none(self):
        group_backend = self.generate_random_group_backend()
        self.assertNone(group_backend.deleted({}))


class RandomBackendForTesting(object):
    pass


class get_backendTestCase(TestCase):
    def test_returns_Backend_by_default(self):
        b = base.get_backend()
        self.assertIsA(b, base.Backend)

    def test_pays_attention_to_settings(self):
        with self.settings(ARMSTRONG_CRM_BACKEND="%s.RandomBackendForTesting" %
                __name__):
            b = base.get_backend()
            self.assertIsA(b, RandomBackendForTesting)


class ReceivingSignalsTestCase(TestCase):
    def setUp(self):
        base.activate()
        fudge.clear_calls()
        fudge.clear_expectations()

    def tearDown(self):
        fudge.verify()

    def expected_payload(self, expected=None, not_expected=None,
            instance_class=None):
        def test(payload):
            for key in expected:
                self.assertTrue(key in payload)
            if not_expected:
                for key in not_expected:
                    self.assertFalse(key in payload)
            if instance_class:
                self.assertIsA(payload["instance"], instance_class)
            return True
        return arg.passes_test(test)

    def expected_user_payload(self):
        return self.expected_payload(
            expected=["instance", "signal", "using", ],
            not_expected=["created", ],
            instance_class=User)

    def expected_group_payload(self):
        return self.expected_payload(
            expected=["instance", "signal", "using", ],
            not_expected=["created", ],
            instance_class=Group)

    def test_dispatches_user_create(self):
        fake_create = fudge.Fake()
        fake_create.is_callable().expects_call().with_args(
                self.expected_user_payload())
        with fudge.patched_context(base.UserBackend, "created", fake_create):
            User.objects.create(username="foobar")

    def test_dispatches_user_update(self):
        fake_update = fudge.Fake()
        fake_update.is_callable().expects_call().with_args(
                self.expected_user_payload())
        with fudge.patched_context(base.UserBackend, "updated", fake_update):
            u = User.objects.create(username="foobar")
            u.username = "foobar-modified"
            u.save()

    def test_dispatch_user_delete(self):
        fake_deleted = fudge.Fake()
        fake_deleted.is_callable().expects_call().with_args(
                self.expected_user_payload())
        with fudge.patched_context(base.UserBackend, "deleted", fake_deleted):
            u = User.objects.create(username="foobar")
            u.delete()

    def test_dispatches_group_create(self):
        fake_create = fudge.Fake()
        fake_create.is_callable().expects_call().with_args(
                self.expected_group_payload())
        with fudge.patched_context(base.GroupBackend, "created", fake_create):
            Group.objects.create(name="foobar")

    def test_dispatches_group_update(self):
        fake_update = fudge.Fake()
        fake_update.is_callable().expects_call().with_args(
                self.expected_group_payload())
        with fudge.patched_context(base.GroupBackend, "updated", fake_update):
            g = Group.objects.create(name="foobar")
            g.groupname = "foobar-modified"
            g.save()
