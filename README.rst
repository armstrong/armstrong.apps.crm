armstrong.apps.crm
==================
Mechanism for hooking up a CRM to Armstrong

This code provides the code necessary to hook up to the `signals`_ sent by the ``User`` and ``Group`` models---the two things you need to update on the CRM when they change inside Django.

``armstrong.apps.crm`` does *not* provide you with a concrete implementation that talks to any particular CRM.  That is currently left to your imagine or the (yet-to-be-released) SugarCRM integration that `Texas Tribune`_ uses or the SalesForce integration that the `Bay Citizen`_ uses.

.. warning:: This is development level software.  Please do not unless you are
             familiar with what that means and are comfortable using that type
             of software.

.. _signals: https://docs.djangoproject.com/en/1.3/topics/signals/


Where is the actual CRM integration?
------------------------------------
We've yet to find an out-of-the-box CRM that works just like we want it to.
Everything requires customization, so we can't ship something that will work
exactly the way you want.

Rather than provide an implementation that doesn't work, we've opted to build
out the framework for connecting to the standard bits of information and
events that you need.

Both the Texas Tribune and the Bay Citizen plan to release their
implementations of custom CRM integration based on this code for help getting
started.


Usage
-----
You need to create a basic backend object to handle data coming out of
Armstrong.  Let's create an ``AwesomeCrmBackend`` backend that supports
sending information about user's to the CRM.

::

    from armstrong.apps.crm import Backend

    class AwesomeCrmBackend(Backend):
        user_class = AwesomeCrmUserBackend

Note the ``AwesomeCrmUserBackend`` reference.  This points to a *class* that
handles the interaction with events created by a user.  You need to create
this for each backend that you implement.

::

    from armstrong.apps.crm import UserBackend

    class AwesomeCrmUserBackend(UserBackend):
        """
        Backend for handling user events and sending them to the CRM.

        Each method receives a ``user`` representing the ``User`` model
        that the action was performed on.  It also receives a ``payload``
        parameter that is the ``**kwargs`` received by the signal.
        """

        def created(self, user, payload):
            """
            Called when a new user is created
            """
            pass

        def updated(self, user, payload):
            """
            Called when a user is updated
            """
            pass

        def deleted(self, user, payload):
            """
            Called when a user is deleted
            """
            pass

        def activated(self, user, payload):
            """
            Called when a new user activates their account

            Only called when django-registration is being used
            """
            pass

        def registered(self, user, payload):
            """
            Called when a new user registers for an account

            Only called when django-registration is being used
            """
            pass


Each method receives a ``user`` and a ``payload``  The ``user`` represents the
User model that the action was performed on.  The ``payload`` is all of the
values sent by the signal this listened to.  Generally, you will only need to
interact with the ``user``, but you have have the option of using the other
values provided by the signal.

Now all that's left is to choose which events you want to notify your CRM of,
then replace out the ``pass`` with the actual implementation.  You don't *have*
to include each of these methods, they're defined in the super-class
``UserBackend``.

Our ``AwesomeCrmBackend`` can also handle modifications to ``Group`` models.
You can add a ``group_class`` to the ``AwesomeCrmBackend`` class like this if
you want to store them:

::

    class AwesomeCrmBackend(Backend):
        user_class = AwesomeCrmUserBackend
        group_class = AwesomeCrmGroupBackend

Now we need to add a ``AwesomeCrmGroupBackend`` class to handle updates to
``Group``.  It looks like our ``AwesomeCrmUserBackend`` with fewer methods.

::

    class AwesomeCrmGroupBackend(GroupBackend):
        """
        Backend for handling group events and sending them to the CRM.

        Each method receives a ``group`` representing the ``Group`` model
        that the action was performed on.  It also receives a ``payload``
        parameter that is the ``**kwargs`` received by the signal.
        """

        def created(self, group, payload):
            """
            Called when a new group is created
            """
            pass

        def updated(self, group, payload):
            """
            Called when a group is updated
            """
            pass

        def deleted(self, group, payload):
            """
            Called when a group is deleted
            """
            pass

Just like the ``AwesomeCrmUserBackend``, you need to modify each of the methods
so they talk to your CRM of choice.


Installation
------------

You can install the development release of this by using::

    name="armstrong.apps.crm"
    pip install -e git://github.com/armstrong/$name#egg=$name


Contributing
------------

* Create something awesome -- make the code better, add some functionality,
  whatever (this is the hardest part).
* `Fork it`_
* Create a topic branch to house your changes
* Get all of your commits in the new topic branch
* Submit a `pull request`_

.. _pull request: http://help.github.com/pull-requests/
.. _Fork it: http://help.github.com/forking/


State of Project
----------------
Armstrong is an open-source news platform that is freely available to any
organization.  It is the result of a collaboration between the `Texas Tribune`_
and `Bay Citizen`_, and a grant from the `John S. and James L. Knight
Foundation`_.  The first release is scheduled for June, 2011.

To follow development, be sure to join the `Google Group`_.

``armstrong.apps.articles`` is part of the `Armstrong`_ project.  You're
probably looking for that.

.. _Texas Tribune: http://www.texastribune.org/
.. _Bay Citizen: http://www.baycitizen.org/
.. _John S. and James L. Knight Foundation: http://www.knightfoundation.org/
.. _Google Group: http://groups.google.com/group/armstrongcms
.. _Armstrong: http://www.armstrongcms.org/


License
-------
Copyright 2011 Bay Citizen and Texas Tribune

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
