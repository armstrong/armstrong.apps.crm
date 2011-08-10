from contextlib import contextmanager
import fudge
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

    def test_created_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            user_backend = self.generate_random_user_backend()
            user_backend.created({})

    def test_updated_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            user_backend = self.generate_random_user_backend()
            user_backend.updated({})

    def test_deleted_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            user_backend = self.generate_random_user_backend()
            user_backend.deleted({})


class GroupBackendTestCase(TestCase):
    def generate_random_group_backend(self):
        r = object()
        return base.GroupBackend(r)

    def test_sets_backend_to_provided_value(self):
        random_object = object()
        group_backend = base.GroupBackend(random_object)
        self.assertEqual(group_backend.backend, random_object)

    def test_created_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            group_backend = self.generate_random_group_backend()
            group_backend.created({})

    def test_updated_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            group_backend = self.generate_random_group_backend()
            group_backend.updated({})

    def test_deleted_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            group_backend = self.generate_random_group_backend()
            group_backend.deleted({})


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
