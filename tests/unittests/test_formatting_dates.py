import unittest
from unittest import mock
import singer
import tap_github


class Mockresponse:
    def __init__(self, resp):
        self.json_data = resp
    
    def json(self):
        return [(self.json_data)]

def get_response(json):
    yield Mockresponse(resp=json)


@mock.patch("tap_github.authed_get_all_pages")
class TestRateLimit(unittest.TestCase):

    def test_due_on_none_without_state(self, mocked_request):
        """
            "due_on" is "None",
            so we will get 1 records
        """
        json = {"due_on": None}

        mocked_request.return_value = get_response(json)

        init_state = {}
        repo_path = "singer-io/tap-github"

        final_state = tap_github.get_all_issue_milestones({}, repo_path, init_state, {})
        # as we will get 1 record and initial bookmark is empty, checking that if bookmark exists in state file returned
        self.assertTrue(final_state["bookmarks"][repo_path]["issue_milestones"]["since"])

    def test_due_on_none_with_state(self, mocked_request):
        """
            "due_on" is "None",
            so we will get 1 records
        """
        json = {"due_on": None}

        mocked_request.return_value = get_response(json)

        repo_path = "singer-io/tap-github"
        init_state = {'bookmarks': {'singer-io/tap-github': {'issue_milestones': {'since': '2021-05-05T07:20:36.887412Z'}}}}
        init_bookmark = singer.utils.strptime_to_utc(init_state["bookmarks"][repo_path]["issue_milestones"]["since"])

        final_state = tap_github.get_all_issue_milestones({}, repo_path, init_state, {})
        last_bookmark = singer.utils.strptime_to_utc(final_state["bookmarks"][repo_path]["issue_milestones"]["since"])
        # as we will get 1 record, final bookmark will be greater than initial bookmark
        self.assertGreater(last_bookmark, init_bookmark)

    def test_due_on_not_none_1(self, mocked_request):
        """
            Bookmark value is smaller than "due_on", 
            so we will get 1 records
        """
        json = {"due_on": "2021-05-07T07:00:00Z"}

        mocked_request.return_value = get_response(json)
        mocked_request.singer.write_record.side_effect = None

        repo_path = "singer-io/tap-github"
        init_state = {'bookmarks': {'singer-io/tap-github': {'issue_milestones': {'since': '2021-05-05T07:20:36.887412Z'}}}}
        init_bookmark = singer.utils.strptime_to_utc(init_state["bookmarks"][repo_path]["issue_milestones"]["since"])

        final_state = tap_github.get_all_issue_milestones({}, repo_path, init_state, {})
        last_bookmark = singer.utils.strptime_to_utc(final_state["bookmarks"][repo_path]["issue_milestones"]["since"])
        # as we will get 1 record, final bookmark will be greater than initial bookmark
        self.assertGreater(last_bookmark, init_bookmark)

    def test_due_on_not_none_2(self, mocked_request):
        """
            Bookmark value is greater than "due_on", 
            so we will get 0 records
        """
        json = {"due_on": "2021-05-07T07:00:00Z"}

        mocked_request.return_value = get_response(json)

        repo_path = "singer-io/tap-github"
        init_state = {'bookmarks': {'singer-io/tap-github': {'issue_milestones': {'since': '2021-05-08T07:20:36.887412Z'}}}}
        init_bookmark = init_state["bookmarks"][repo_path]["issue_milestones"]["since"]

        final_state = tap_github.get_all_issue_milestones({}, repo_path, init_state, {})
        # as we will get 0 records, initial and final bookmark will be same
        self.assertEquals(init_bookmark, final_state["bookmarks"][repo_path]["issue_milestones"]["since"])
