"""Offline regressions for dependencies reused by the new onboarding scenarios."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch

from api import idpay
from bdd.steps import initiative_steps
from util import utility


class Box(dict):
    __getattr__ = dict.__getitem__


class PostMergeCompatibilityTest(unittest.TestCase):
    def test_unsubscribe_sends_authenticated_delete_to_wallet_endpoint(self):
        response = Mock(status_code=204)
        with patch.object(idpay.requests, "delete", return_value=response) as delete:
            result = idpay.unsubscribe("initiative-test", "offline-token")
        self.assertIs(result, response)
        url = delete.call_args.args[0]
        self.assertTrue(url.endswith("/wallet/initiative-test/unsubscribe"))
        self.assertEqual(delete.call_args.kwargs["headers"]["Authorization"],
                         "Bearer offline-token")

    def test_unsubscribe_checks_wallet_and_timeline_after_success(self):
        with patch.object(utility, "get_io_token", return_value="offline-token"), \
             patch.object(utility, "unsubscribe", return_value=Mock(status_code=204)) as unsubscribe, \
             patch.object(utility, "retry_wallet") as wallet, \
             patch.object(utility, "retry_timeline") as timeline:
            utility.citizen_unsubscribe_from_initiative("initiative-test", "SYNTHETIC-CITIZEN")
        unsubscribe.assert_called_once_with("initiative-test", "offline-token")
        self.assertEqual(wallet.call_args.kwargs["expected"], "UNSUBSCRIBED")
        self.assertEqual(timeline.call_args.kwargs["expected"], "UNSUBSCRIBED")

    def test_unsubscribe_failure_does_not_proceed_to_polling(self):
        with patch.object(utility, "get_io_token", return_value="offline-token"), \
             patch.object(utility, "unsubscribe", return_value=Mock(status_code=404)), \
             patch.object(utility, "retry_wallet") as wallet, \
             patch.object(utility, "retry_timeline") as timeline:
            with self.assertRaises(AssertionError):
                utility.citizen_unsubscribe_from_initiative("initiative-test", "SYNTHETIC-CITIZEN")
        wallet.assert_not_called()
        timeline.assert_not_called()

    def test_named_initiative_initializes_the_selected_configuration(self):
        context = SimpleNamespace()
        initiative_settings = object()
        secrets = {"initiatives": {"bonus_decoder": {
            "id": "initiative-test", "organization_id": "organization-test"}}}
        settings = SimpleNamespace(initiatives={"bonus_decoder": initiative_settings})
        with patch.object(initiative_steps, "secrets", secrets), \
             patch.object(initiative_steps, "settings", settings), \
             patch.object(initiative_steps, "base_context_initialization") as initialize:
            initiative_steps.step_given_initiative_name(context, "bonus_decoder")
        self.assertEqual(context.initiative_id, "initiative-test")
        self.assertEqual(context.organization_id, "organization-test")
        self.assertIs(context.initiative_settings, initiative_settings)
        initialize.assert_called_once_with(context)

    def test_new_negative_case_initiative_is_registered_for_cleanup(self):
        secrets = Box(initiatives={}, newly_created=set())
        with patch.object(initiative_steps, "secrets", secrets), \
             patch.object(initiative_steps, "create_initiative", return_value="created-test") as create:
            initiative_steps.step_new_initiative_created(SimpleNamespace(), "NOT_STARTED")
        create.assert_called_once_with("NOT_STARTED")
        self.assertEqual(secrets.initiatives["NOT_STARTED"]["id"], "created-test")
        self.assertEqual(secrets.newly_created, {"created-test"})
