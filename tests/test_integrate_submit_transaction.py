# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import json

from iconservice.base.address import ZERO_SCORE_ADDRESS
from tests.test_integrate_base import TestIntegrateBase
from iconservice.base.address import Address


class TestIntegrateSubmitTransaction(TestIntegrateBase):
    def setUp(self):
        super().setUp()
        self.multisig_score_addr = self._deploy_multisig_wallet()

    def test_submit_transaction_validate_params_format(self):
        # success case: valid params format
        change_requirement_params = [
            {'name': '_required',
             'type': 'int',
             'value': 3}
        ]
        submit_tx_params = {'_destination': str(self.multisig_score_addr),
                            '_method': 'changeRequirement',
                            '_params': json.dumps(change_requirement_params),
                            '_description': 'change requirements 2 to 3'}

        valid_tx = self._make_score_call_tx(addr_from=self._owner1,
                                            addr_to=self.multisig_score_addr,
                                            method='submitTransaction',
                                            params=submit_tx_params
                                            )
        prev_block, tx_results = self._make_and_req_block([valid_tx])
        self._write_precommit_state(prev_block)
        self.assertEqual(int(True), tx_results[0].status)

        # success case: when value is string type, should be submitted.
        change_requirement_params = [
            {'name': '_required',
             'type': 'int',
             'value': hex(3)}
        ]
        submit_tx_params = {'_destination': str(self.multisig_score_addr),
                            '_method': 'changeRequirement',
                            '_params': json.dumps(change_requirement_params),
                            '_description': 'change requirements 2 to 3'}

        valid_tx = self._make_score_call_tx(addr_from=self._owner1,
                                            addr_to=self.multisig_score_addr,
                                            method='submitTransaction',
                                            params=submit_tx_params
                                            )
        prev_block, tx_results = self._make_and_req_block([valid_tx])
        self._write_precommit_state(prev_block)
        self.assertEqual(int(True), tx_results[0].status)

        # failure case: when input unsupported type as params' type
        change_requirement_params = [
            {'name': '_required',
             'type': 'dict',
             'value': "{'test':'test'}"}
        ]
        unsupported_type_params = {'_destination': str(self.multisig_score_addr),
                            '_method': 'changeRequirement',
                            '_params': json.dumps(change_requirement_params),
                            '_description': 'change requirements 2 to 3'}

        invalid_tx = self._make_score_call_tx(addr_from=self._owner1,
                                              addr_to=self.multisig_score_addr,
                                              method='submitTransaction',
                                              params=unsupported_type_params
                                              )
        prev_block, tx_results = self._make_and_req_block([invalid_tx])
        self._write_precommit_state(prev_block)

        expected_revert_massage = "dict is not supported type(only int, str, bool, Address, bytes are supported) (32000)"
        actual_revert_massage = tx_results[0].failure.message
        self.assertEqual(expected_revert_massage, actual_revert_massage)

        # failure case: invalid json format
        invalid_json_format_params = "{'test': }"

        submit_tx_params = {'_destination': str(self.multisig_score_addr),
                            '_method': 'changeRequirement',
                            '_params': json.dumps(invalid_json_format_params),
                            '_description': 'change requirements 2 to 3'}

        invalid_tx = self._make_score_call_tx(addr_from=self._owner1,
                                              addr_to=self.multisig_score_addr,
                                              method='submitTransaction',
                                              params=submit_tx_params
                                              )
        prev_block, tx_results = self._make_and_req_block([invalid_tx])
        self._write_precommit_state(prev_block)

        expected_revert_massage = "can't convert params json data, check the format"
        actual_revert_massage = tx_results[0].failure.message
        self.assertEqual(expected_revert_massage, actual_revert_massage)

    def test_submit_transaction_check_wallet_owner(self):
        # failure case: not included wallet owner
        add_owner_params = [
            {'name': '_required',
             'type': 'int',
             'value': 3}
        ]
        submit_tx_params = {'_destination': str(self.multisig_score_addr),
                            '_method': 'changeRequirement',
                            '_params': json.dumps(add_owner_params),
                            '_description': 'change requirements 2 to 3'}

        not_included_owner = self._owner4
        valid_tx = self._make_score_call_tx(addr_from=not_included_owner,
                                            addr_to=self.multisig_score_addr,
                                            method='submitTransaction',
                                            params=submit_tx_params
                                            )
        prev_block, tx_results = self._make_and_req_block([valid_tx])
        self._write_precommit_state(prev_block)

        expected_revert_massage = f'{self._owner4} is not a owner of wallet'
        actual_revert_massage = tx_results[0].failure.message
        self.assertEqual(expected_revert_massage, actual_revert_massage)

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self.multisig_score_addr,
            "dataType": "call",
            "data": {
                "method": "getTransactionInfo",
                "params": {"_transactionId": "0"}
            }
        }
        response = self._query(query_request)
        print(response)
        #self.assertEqual(response)

    def test_submit_transaction_check_transaction_listed_on(self):
        # submit 4 transaction and one transaction will be failed
        # transaction total count should be 3
        # success case: valid params format
        valid_params = [
            {'name': '_required',
             'type': 'int',
             'value': 3}
        ]
        invalid_params = [
            {'name': '_required',
             'type': 'dict',
             'value': "{'test':'test'}"}
        ]

        valid_tx_params = {'_destination': str(self.multisig_score_addr),
                           '_method': 'changeRequirement',
                           '_params': json.dumps(valid_params),
                           '_description': 'test valid transaction'}
        valid_tx1 = self._make_score_call_tx(
                                            addr_from=self._owner1,
                                            addr_to=self.multisig_score_addr,
                                            method='submitTransaction',
                                            params=valid_tx_params
                                            )
        valid_tx_params = {'_destination': str(self.multisig_score_addr),
                           '_method': 'changeRequirement',
                           '_params': json.dumps(valid_params),
                           '_description': 'valid transaction2'}
        valid_tx2 = self._make_score_call_tx(
                                            addr_from=self._owner1,
                                            addr_to=self.multisig_score_addr,
                                            method='submitTransaction',
                                            params=valid_tx_params
                                            )
        invalid_tx_params = {
                    '_destination': str(self.multisig_score_addr),
                    '_method': 'changeRequirement',
                    '_params': json.dumps(invalid_params),
                    '_description': 'invalid transaction'}
        invalid_tx = self._make_score_call_tx(
                                            addr_from=self._owner1,
                                            addr_to=self.multisig_score_addr,
                                            method='submitTransaction',
                                            params=invalid_tx_params
                                            )
        valid_tx_params = {'_destination': str(self.multisig_score_addr),
                           '_method': 'changeRequirement',
                           '_params': json.dumps(valid_params),
                           '_description': 'valid transaction3'}
        valid_tx3 = self._make_score_call_tx(
                                            addr_from=self._owner1,
                                            addr_to=self.multisig_score_addr,
                                            method='submitTransaction',
                                            params=valid_tx_params
                                            )


        prev_block, tx_results = self._make_and_req_block(
            [valid_tx1, valid_tx2, invalid_tx, valid_tx3])
        self._write_precommit_state(prev_block)
        self.assertEqual(int(True), tx_results[0].status)
        self.assertEqual(int(True), tx_results[1].status)
        self.assertEqual(int(False), tx_results[2].status)
        self.assertEqual(int(True), tx_results[3].status)

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self.multisig_score_addr,
            "dataType": "call",
            "data": {
                "method": "getTransactionCount",
                "params": {"_pending": "1", "_executed": "1"}
            }
        }
        response = self._query(query_request)

        self.assertEqual(3, response)

        # transaction id 4 should'n be exist.
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self.multisig_score_addr,
            "dataType": "call",
            "data": {
                "method": "getTransactionInfo",
                "params": {"_transactionId": "4"}
            }
        }

        response = self._query(query_request)
        self.assertEqual(None, response)

        #Todo: make getTransactionInfo more informative and write check data
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self.multisig_score_addr,
            "dataType": "call",
            "data": {
                "method": "getTransactionInfo",
                "params": {"_transactionId": "4"}
            }
        }

        response = self._query(query_request)
        self.assertEqual(None, response)

        #Todo: make transactions more then 10 and test getTransactionIds
