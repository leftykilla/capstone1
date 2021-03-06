"""User View tests."""

import os
from unittest import TestCase
from flask import session
from users.models import social_db, social_connect_db, User, Follows
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///capstone1-test"


from app import app, CURR_USER_KEY


social_db.create_all()


app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        social_db.drop_all()
        social_db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    password="testuser")
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("abc", "password")
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("efg", "password")
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup("hij", "password")
        self.u4 = User.signup("testing", "password")

        social_db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        social_db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get("/users")

           
            self.assertIn("abc", str(resp.data))
            self.assertIn("efg", str(resp.data))
            self.assertIn("hij", str(resp.data))
            self.assertIn("testing", str(resp.data))

    def test_user_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.u1_id}")

            self.assertIn("abc", str(resp.data))
            self.assertIn("Posts", str(resp.data))
            self.assertIn("Followers", str(resp.data))
            self.assertIn("Following", str(resp.data))

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id,
                     user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.u2_id,
                     user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id,
                     user_following_id=self.u1_id)

        social_db.session.add_all([f1, f2, f3])
        social_db.session.commit()

    def test_user_show_with_follows(self):

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

           
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 3)

            # Test for a count of 2 following
            self.assertIn("2", found[1].text)

            # Test for a count of 1 follower
            self.assertIn("1", found[2].text)


    def test_show_following(self):

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("abc", str(resp.data))
            self.assertIn("efg", str(resp.data))
            self.assertNotIn("hij", str(resp.data))
            self.assertNotIn("testing", str(resp.data))

    def test_show_followers(self):

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("abc", str(resp.data))
            self.assertNotIn("efg", str(resp.data))
            self.assertNotIn("hij", str(resp.data))
            self.assertNotIn("testing", str(resp.data))

    def test_unauthorized_following_page_access(self):
        self.setup_followers()
        with self.client as c:

            resp = c.get(
                f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauthorized_followers_page_access(self):
        self.setup_followers()
        with self.client as c:

            resp = c.get(
                f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))
