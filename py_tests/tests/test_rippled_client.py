#!/usr/local/bin/python3

from .context import RippledClient
from .context import RippleAccount

import re
import pytest

rippled_api = {
    'server_info': {'result': {'caller': 'get_server_info'}},
    'wallet_propose': {'result': {'caller': 'wallet_propose'}},
    'feature': {'result': {'caller': 'multisign_status'}},
    'ledger_accept': {'result': {'caller': 'ledger_accept'}},
    'account_info': {'result': {'caller': 'account_info'}},
    'sign': {'result': {'caller': 'sign'}},
    'sign_for': {'result': {'caller': 'sign_for'}},
    'account_objects': {'result': {'caller': 'account_objects'}},
    'submit': {'result': {'caller': 'submit'}},
    'submit_multisigned': {'result': {'caller': 'submit_multisigned'}},
    'tx': {'result': {'caller': 'confirm_tx'}},
    'ledger': {
        'result': {
            'caller': 'get_ledger',
        },
        'expected_json_params': {
            "ledger_index": "validated",
            "accounts": False,
            "full": False,
            "transactions": False,
            "expand": False,
            "owner_funds": False
        }
    },
}

test_host = 'localhost'
test_port = '5006'
test_version = '0.70.2'


class FakeResp:
    ok = True

    def __init__(self, json_data):
        self.json_data = json_data

    def json(self):
        return self.json_data


class FakeClient:
    def __init__(self):
        self.response = {}

    def set_response(self, method, response):
        self.response[method] = response

    def post(self, url, verify=True, params=None, headers=None, json=None, auth=None, get=False):
        assert verify is False
        expected_url = 'http://%s:%s/' % (test_host, test_port)

        print("%s vs %s" % (expected_url, url))

        url_match = re.match(r'(?P<head>%s)$' % expected_url, url)

        assert url_match.group('head') == expected_url

        method = json.get('method', '')

        print('METHOD: "%s"' % method)
        details = rippled_api.get(method)

        assert type(details) is dict

        call_method = details.get('call_method')
        if get:
            assert call_method == 'get'
        else:
            assert not call_method or call_method == 'post'

        expected_params = details.get('expected_json_params', None)

        print("expected: %s" % expected_params)
        actual_params = None
        if type(expected_params) is dict and type(json) is dict and json.get('params'):
            actual_params = json.get('params')[0]

            if type(actual_params) is dict:
                for key in expected_params:
                    if key not in actual_params:
                        assert key in actual_params
            else:
                assert expected_params is None

        set_response = self.response.get(method, None)

        print("RESPONSE: %s" % self.response)

        if set_response:
            result = set_response
        else:
            result = details


        print("SET RESPONSE (%s): %s" % (method, result))
        return FakeResp(result)

    def get(self, url, verify=True, params=None, headers=None, auth=None, json=None) -> object:
        """

        :rtype: object
        """
        return self.post(url, verify, params, headers, json, auth, get=True)


class TestRippledClient:

    def setup(self):
        self.request_client = FakeClient()
        # self.request_client = requests

        self.client = RippledClient(test_host, test_port, self.request_client)
        print('setup')

    def teardown(self):
        print('teardown')

    def test_get_server_info(self):
        resp = self.client.get_server_info()
        assert type(resp) is dict and resp.get('caller') == 'get_server_info'

    def test_get_ledger(self):
        resp = self.client.get_ledger()
        assert type(resp) is dict and resp.get('caller') == 'get_ledger'

    def test_wallet_propose(self):
        resp = self.client.wallet_propose()
        assert type(resp) is dict and resp.get('caller') == 'wallet_propose'

    def test_get_account_info(self):
        resp = self.client.get_account_info(1)
        assert type(resp) is dict and resp.get('caller') == 'account_info'

    def test_sign(self):
        resp = self.client.sign('secret', 'tx')
        assert type(resp) is dict and resp.get('caller') == 'sign'

    def test_sign_for(self):
        resp = self.client.sign_for(1, 'secret', 'tx')
        assert type(resp) is dict and resp.get('caller') == 'sign_for'

    def test_account_objects(self):
        resp = self.client.account_objects(1)
        assert type(resp) is dict and resp.get('caller') == 'account_objects'

    def test_submit(self):
        resp = self.client.submit('blob')
        assert type(resp) is dict and resp.get('caller') == 'submit'

    def test_submit_multisigned(self):
        resp = self.client.submit_multisigned('blob')
        assert type(resp) is dict and resp.get('caller') == 'submit_multisigned'

    def test_confirm_tx(self):
        resp = self.client.confirm_tx('tx_hash')
        assert type(resp) is dict and resp.get('caller') == 'confirm_tx'

    def test_ledger_accept(self):
        good_result = {
            "result": {
                "ledger_current_index": 5,
                "status": "success"
            }
        }
        self.request_client.set_response('ledger_accept', good_result)
        result = self.client.ledger_accept()
        assert result

        bad_result = {
            "result": {
                "ledger_current_index": 5,
                "status": "failed"
            }
        }
        self.request_client.set_response('ledger_accept', bad_result)
        result = self.client.ledger_accept()

        assert not result

    def test_multisign_status(self):
        ms_id = RippledClient.multisign_id()
        good_result = {
            "result": {
                ms_id: {
                    "enabled": True,
                    "name": "MultiSign",
                    "supported": True,
                    "vetoed": False
                },
                "status": "success"
            }
        }
        self.request_client.set_response('feature', good_result)
        status = self.client.multisign_status()
        assert status is True

        bad_result = {
            "result": {
                ms_id: {
                    "enabled": False,
                    "name": "MultiSign",
                    "supported": True,
                    "vetoed": False
                },
                "status": "success"
            }
        }
        self.request_client.set_response('feature', bad_result)
        status = self.client.multisign_status()
        assert status is False

    def test_get_rippled_version(self):
        good_result = {'result': {'info':{'build_version': test_version}}}

        self.request_client.set_response('server_info', good_result)

        vers = self.client.get_rippled_version()

        assert vers == test_version


class TestRippleAccount:

    def setup(self):
        self.request_client = FakeClient()
        # self.request_client = requests

        self.client = RippledClient(test_host, test_port, self.request_client)
        self.account = RippleAccount(self.client, {'account_id': 1, 'master_seed': 'secret'})

        print('setup')

    def teardown(self):
        print('teardown')

    def test_genesis(self):
        account = RippleAccount(self.client, 'genesis')

        assert account.id == RippleAccount.genesis_account()

    def test_invalid(self):
        with pytest.raises(ValueError):
            RippleAccount(self.client, 'bogus')

    def test_get_balance(self):
        test_balance = 101
        self.request_client.set_response('account_info', {'result': {'status': 'success', 'account_data': {'Balance': test_balance}}})
        balance = self.account.get_balance()

        assert balance == test_balance

        self.request_client.set_response('account_info', {'result': {'status': 'success', 'account_data': 'bogus'}})
        with pytest.raises(Exception):
            balance = self.account.get_balance()

    def test_get_account_info(self):
        good_info = 'good'
        self.request_client.set_response('account_info', {'result': {'status': 'success', 'account_data': {'info': good_info}}})
        info = self.account.get_account_info()
        assert info.get('info') == good_info

        self.request_client.set_response('account_info', {'result': {'status': 'fail', 'error': 'error', 'error_code': 1, 'error_message': 'error_message'}})
        with pytest.raises(Exception):
            info = self.account.get_account_info()

    def test_get_account_sequence(self):
        test_sequence = 100
        self.request_client.set_response('account_info', {'result': {'status': 'success', 'account_data': {'Sequence': test_sequence}}})
        sequence = self.account.get_account_sequence()

        assert sequence == test_sequence

    def test_send_payment(self):
        self.request_client.set_response('sign', {'result': {'status': 'success', 'tx_blob': {'tx_json': {'engine_result': 'tesSUCCESS'}}}})
        self.request_client.set_response('submit', {'result': {'engine_result': 'tesSUCCESS'}})

        assert self.account.send_payment(1, self.account)

    def test_config_multi_sign(self):
        self.request_client.set_response('sign', {'result': {'status': 'success', 'tx_blob': {'tx_json': {'engine_result': 'tesSUCCESS'}}}})
        self.request_client.set_response('submit', {'result': {'engine_result': 'tesSUCCESS'}})

        assert self.account.config_multi_sign(1, {self.account: 1})

    def test_send_mult_sign_payment(self):
        self.request_client.set_response('account_info', {'result': {'status': 'success', 'account_data': {'Sequence': 1}}})
        self.request_client.set_response('sign_for', {'result': {'status': 'success', 'tx_json': {'engine_result': 'tesSUCCESS',
                                                      'Signers': [{}]}}})
        self.request_client.set_response('submit_multisigned', {'result': {'engine_result': 'tesSUCCESS', 'tx_json': {'hash': True}}})

        assert self.account.send_multi_sign_payment(1, self.account, {self.account: 1}, 1)
