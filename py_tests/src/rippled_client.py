#!/usr/local/bin/python3
"""
    A rest client that can talk to rippled
"""

import requests


class RippleAccount:
    """
    Uses the rippled client to represent a ripple account
    """

    def __init__(self, rippled_client, account_info=None):
        """
        :type rippled_client: RippledClient
        :param account_info: Which account to initialize the account_info to.  Either pass in a account_info info,
        or set to 'genesis' for the genesis account, or 'new' to propose a new account
        """
        self.rippled = rippled_client
        self.id = ''
        self.secret = ''

        if 'genesis' == account_info:
            self.set_genesis_account()

        elif 'new' == account_info:
            self.set_new()

        elif type(account_info) is dict:
            self.id = account_info.get('account_id', '')
            self.secret = account_info.get('master_seed', '')

        else:
            raise ValueError('Invalid account specified')

    @staticmethod
    def genesis_account():
        """
        :return: Return the default account id of the genesis account
        """
        return "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

    def set_genesis_account(self):
        """
        Set this account to be the genesis account
        """
        self.id = self.genesis_account()
        self.secret = 'masterpassphrase'

    def set_new(self):
        """
        Set this account to be a newly proposed account
        """
        new_account = self.rippled.wallet_propose()

        self.id = new_account.get('account_id')
        self.secret = new_account.get('master_seed')

    def get_balance(self):
        """
        :return: The balance of this account in drops
        """
        # XXX Not sure that this is the right place for ledger_accept()
        # self.rippled.ledger_accept()

        info = self.get_account_info()

        if type(info) is dict:
            return info.get('Balance')
        else:
            raise Exception("Unable to get account balance")

    def get_account_sequence(self):
        """
        :return: The sequence number of this account
        """
        # XXX Not sure that this is the right place for ledger_accept()
        # self.rippled.ledger_accept()

        info = self.get_account_info()

        if type(info) is dict:
            return info.get('Sequence')

        else:
            raise Exception("Unable to get account sequence")

    def get_account_info(self):
        """
        :return: The information about this account
        """
        info = self.rippled.get_account_info(self.id, signer_lists=True)

        if type(info) is not dict:
            raise Exception("Unable to get account info")

        elif 'success' != info.get('status'):
            raise Exception("Unable to get account info (%s: %s): %s" % (
                info.get('error'),
                info.get('error_code'),
                info.get('error_message')))

        return info.get('account_data')

    def send_payment(self, amount, dst_account) -> bool:
        """
        Transfer amount of drops out of this account into dst_account

        :param amount: Amount of drops to transfer
        :param dst_account: Destination account
        :type dst_account: ripple_account
        :return: True of False
        """
        dst_account_id = dst_account.id

        tx = {
            'Account': self.id,
            # XXX Does not include LastLedgerSequence but probably should (its strongly recommended)
            'Amount': amount,
            'Destination': dst_account_id,
            'TransactionType': 'Payment'
        }
        signed_tx = self.rippled.sign(self.secret, tx)

        if type(signed_tx) == dict and signed_tx.get('status') == 'success':
            tx_blob = signed_tx.get('tx_blob')

            result = self.rippled.submit(tx_blob)

            return type(result) is dict and 'tesSUCCESS' == result.get('engine_result')

        return False

    def config_multi_sign(self, quorum, signer_weights):
        signer_entries = []
        for account, weight in signer_weights.items():
            account = account.id

            signer_entries.append({"SignerEntry": {"Account": account, "SignerWeight": weight}})

        tx = {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": self.id,
            "Fee": "500000000",
            "SignerQuorum": quorum,
            "SignerEntries": signer_entries
        }
        signed_tx = self.rippled.sign(self.secret, tx)

        if type(signed_tx) != dict or 'success' != signed_tx.get('status'):
            raise Exception("Unable to sign multi-sign tx")

        else:
            tx_blob = signed_tx.get('tx_blob')

            result = self.rippled.submit(tx_blob)
            tx_json = signed_tx.get('tx_json')

            if type(result) is not dict:
                raise Exception("Unable to configure multi-sign account")

            elif result.get('error'):
                raise Exception("Unable to configure multi-sign account (%s: %s): %s" % (
                    result.get('error'),
                    result.get('error_code'),
                    result.get('error_message')))

            elif 'tesSUCCESS' != result.get('engine_result'):
                raise Exception("Unable to configure multi-sign account (%s: %s): %s" % (
                    result.get('engine_result'),
                    result.get('engine_result_code'),
                    result.get('engine_result_message')))
            else:
                self.rippled.ledger_accept()

        return True

    def send_multi_sign_payment(self, amount, dst_account, signer_list, fee):
        """
        Send a
        :param amount: amount to send in drops
        :param dst_account: destination account
        :param signer_list: list of signer accounts
        :return: tx_hash if success, False otherwise
        """
        # self.account_objects(new_id) # confirm the new signer list

        dst_account_id = dst_account.id
        sequence = self.get_account_sequence()

        tx = {
            'Account': self.id,
            # XXX Does not include LastLedgerSequence but probably should (its strongly recommended)
            'Amount': amount,
            'Destination': dst_account_id,
            'Fee': fee,
            'Sequence': sequence,
            'TransactionType': "Payment"
        }

        tx_json = None
        signers = []
        for signer in signer_list:
            signed_tx = self.rippled.sign_for(signer.id, signer.secret, tx)

            if type(signed_tx) is dict and signed_tx.get('status') == 'success':
                tx_json = signed_tx.get('tx_json')
                new_signers = tx_json.get('Signers')
                new_signer = new_signers[0]

                signers.append(new_signer)

            elif type(signed_tx) is dict and signed_tx.get('error'):
                raise Exception("Unable to sign multi-sign tx (%s: %s): %s" % (
                    signed_tx.get('error'),
                    signed_tx.get('error_code'),
                    signed_tx.get('error_message')))
            else:
                raise Exception("Unable to sign multi-sign tx: no success or error")

        tx_json['Signers'] = signers
        tx_json['Sequence'] = self.get_account_sequence()

        result = self.rippled.submit_multisigned(tx_json)

        self.rippled.ledger_accept()

        if type(result) is not dict:
            raise Exception("Unable to submit multi-sign tx")

        elif result.get('error'):
            raise Exception("Error: Unable to submit multi-sign tx (%s: %s): %s" % (
                result.get('error'),
                result.get('error_code'),
                result.get('error_message')))

        elif 'tesSUCCESS' != result.get('engine_result'):
            raise Exception("Unsucessful: Unable to submit multi-sign tx (%s: %s): %s" % (
                result.get('engine_result'),
                result.get('engine_result_code'),
                result.get('engine_result_message')))

        else:
            tx_hash = result.get('tx_json').get('hash')

            return tx_hash


class RippledClient:
    """
    Client to talk rippled via REST API
    """

    def __init__(self, host, port, client=requests):
        """
        :param host: hostname of rippled
        :param port: admin rpc port of rippled
        :param client: to allow dependency injection for testing
        """
        self.host = host
        self.port = port
        self.client = client

    def __get_client_url(self, endpoint=''):
        """
        :param endpoint: API endpoint
        :return: url constructed as: http://host:port/endpoint/command
        """
        url = 'http://%s:%s/%s' % (self.host, self.port, endpoint)

        return url

    def __send_request(self, endpoint='', params=None, json=None, get=False) -> requests.Response:
        """
        Send a request to the ripple REST API with a valid oath token
        Raise an exception if we don't get back a '200 ok'

        :rtype: requests.Response
        :param endpoint: API endpoint to send to
        :param params: query parameters of the request
        :param json: json to be included in the body of the request
        :param get: true if request should be a 'get', otherwise 'post will be used
        :return: return the full response object from the query
        """
        url = self.__get_client_url(endpoint)

        headers = {'Content-Type': 'application/json'}
        # print("URL: %s " % url)
        # print("Headers: %s" % headers)
        # print("Params: %s" % params)

        if get:
            resp = self.client.get(url, verify=False, params=params, headers=headers)
        else:
            resp = self.client.post(url, verify=False, params=params, headers=headers, json=json)

        if not resp.ok:
            raise RuntimeError('Request failed: %s' % resp.text)

        return resp

    @staticmethod
    def multisign_id() -> str:
        """
        :return: return the known id for multisign on rippled
        """
        return "4C97EBA926031A7CF7D7B36FDE3ED66DDA5421192D63DE53FFB46E43B9DC8373"

    @staticmethod
    def return_json_resp(resp) -> dict:
        """

        :rtype: dict
        """
        json = resp.json()

        return type(json) is dict and json.get('result', None)

    def get_server_info(self) -> dict:
        """
        :return: Returns server info from rippled
        """
        resp = self.__send_request(json={"method": "server_info"})

        return self.return_json_resp(resp)

    def get_ledger(self) -> dict:
        """
        :return: Returns server ledger from rippled
        """
        resp = self.__send_request(json=
            {
                "method": "ledger",
                "params": [
                    {
                        "ledger_index": "validated",
                        "accounts": False,
                        "full": False,
                        "transactions": False,
                        "expand": False,
                        "owner_funds": False
                    }
                ]
            }
        )
        return self.return_json_resp(resp)

    def wallet_propose(self, passphrase='') -> dict:
        """
        Proposes a new wallet (rippled_account)
        :param passphrase: optional
        :return: returns a account dict if successful as follows:

        {
            "account_id": "rDBdQdggGhDtk3U76LPpe1mUPJcYowu49r",
            "key_type": "secp256k1",
            "master_key": "DADE LIND WALK RACY FILM BOLD LOUD AIRY HE ELY PRY BAKE",
            "master_seed": "shxTuqTc3jKY6MPpkPdFBTLQyMkHx",
            "master_seed_hex": "A252C388664429B3B604B865DAFB756E",
            "public_key": "aB44r7mJYKCHgzsYXt55GH59n3KxGoccg9i7VXhJKSnKUJJ6CCwf",
            "public_key_hex": "023560D92BDAB2E5FEEA2AA12B8661447F87F6EB360C24B8D9232CB5DBAE87DFAE",
            "status": "success"
        }
        """
        params = None
        if passphrase:
            params = [{'passphase': passphrase}]

        resp = self.__send_request(json={"method": "wallet_propose", "params": params})

        return self.return_json_resp(resp)

    def ledger_accept(self) -> bool:
        """
        Accept the current ledger
        :return: return True on success
        """
        resp = self.__send_request(json={"method": "ledger_accept", "params": []})
        result = self.return_json_resp(resp)

        return type(result) is dict and result.get('status', '') == 'success'

    def multisign_status(self) -> bool:
        """
        Is the multisign feature enabled?

        :return: True or false
        """
        ms_id = self.multisign_id()
        resp = self.__send_request(json=
            {
                "method": "feature",
                "params": [
                    {
                        "feature": ms_id,
                        "vetoed": False
                    }
                ]
            }
        )
        result = self.return_json_resp(resp)
        multisign_status = result.get(ms_id, None)

        return type(multisign_status) is dict and multisign_status.get('enabled')

    def get_rippled_version(self) -> str:
        """
        :return: return the version of rippled
        """
        status = self.get_server_info()
        info = status.get('info', None)

        return type(info) is dict and info.get('build_version', '')

    def get_account_info(self, account_id, signer_lists=False) -> dict:
        """
        :param account_id: account to get info for
        :param signer_lists: True if you want a list of signers
        :return: Returns account_info dict
        """
        resp = self.__send_request(json={
                "method": "account_info",
                "params": [
                    {
                        "account": account_id,
                        "signer_lists": signer_lists
                    }
                ]
            }
        )

        return self.return_json_resp(resp)

    def sign(self, secret, tx: object) -> dict:
        """
        :param secret: secret to sign with
        :param tx: tx to sign
        :return: signed transaction blob
        """
        resp = self.__send_request(json=
            {
                'method': "sign", 'params': [
                    {
                        'secret': secret,
                        'tx_json': tx,
                        'fee_mult_max': 1000
                    }
                ]
            }
        )
        return self.return_json_resp(resp)

    def sign_for(self, account_id, secret, tx: object) -> dict:
        """
        :param account_id:
        :param secret: secret to sign with
        :param tx: tx to sign
        :return: signed transaction blob
        """
        resp = self.__send_request(json=
            {
                'method': "sign_for", 'params': [
                {
                    'account': account_id,
                    'secret': secret,
                    'tx_json': tx,
                }
            ]
            }
        )
        return self.return_json_resp(resp)

    def account_objects(self, account_id) -> dict:
        """
        :param account_id: id of accunt
        :return: objects associated with the account
        """
        resp = self.__send_request(json= {'method': "account_objects", 'params': [{'account': account_id}]})
        return self.return_json_resp(resp)

    def submit(self, tx_blob: object) -> dict:
        """
        :rtype: dict
        :param tx_blob: previously signed transaction
        :return: submitted transaction
        """
        resp = self.__send_request(json=dict(method="submit", params=[{'tx_blob': tx_blob}]))
        return self.return_json_resp(resp)

    def submit_multisigned(self, tx_json: dict) -> dict:
        """
        :rtype: dict
        :param tx_json: previously signed transaction including all signers
        :return: submitted transaction
        """
        resp = self.__send_request(json=dict(method="submit_multisigned", params=[{'tx_json': tx_json}]))
        return self.return_json_resp(resp)

    def confirm_tx(self, tx_hash) -> dict:
        """
        Confirm the result of a previously committed transaction

        :param tx_hash: hash of completed transaction
        :return: confirmation
        """
        resp = self.__send_request(json=dict(method="tx", params=[{'transaction': tx_hash}]))
        return self.return_json_resp(resp)


def get_rippled_client(hostname, port):
    return RippledClient(hostname, port)


def get_account(rippled, account):
    return RippleAccount(rippled, account)
