"""
Security parity of the field controls: `control` / `controlStr` are read by a logged-in
user only (they were readable anonymously).
"""
import json

from core.models.openimis_graphql_test_case import openIMISGraphQLTestCase
from core.test_helpers import create_test_interactive_user, get_test_token


class ControlAuthenticationTest(openIMISGraphQLTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = create_test_interactive_user(username="controls_sp_user")
        cls.token = get_test_token(cls.user)

    def _q(self, query, token=None):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
        return json.loads(self.query(query, headers=headers).content)

    def _assert_refused(self, content, field):
        self.assertIn("errors", content, content)
        self.assertIsNone((content.get("data") or {}).get(field), content)

    def test_control_anonymous_refused(self):
        self._assert_refused(self._q('{ control { edges { node { name } } } }'), "control")

    def test_control_str_anonymous_refused(self):
        self._assert_refused(self._q('{ controlStr(str: "a") { edges { node { name } } } }'), "controlStr")
        self._assert_refused(self._q('{ controlStr { edges { node { name } } } }'), "controlStr")

    def test_logged_in_user_reads_controls(self):
        for query, field in (('{ control { edges { node { name } } } }', "control"),
                             ('{ controlStr(str: "a") { edges { node { name } } } }', "controlStr")):
            content = self._q(query, self.token)
            self.assertNotIn("errors", content, content.get("errors"))
            self.assertIsNotNone(content["data"][field])
