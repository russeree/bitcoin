#!/usr/bin/env python3
# Copyright (c) 2026-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test $DOG Mode preferential peering.

$DOG Mode nodes advertise the NODE_DOG_MODE service flag and open up to
MAX_DOG_MODE_CONNECTIONS (4) extra long-lived outbound connections ("dog"
connection type) to peers advertising the same flag, so that $DOG Mode nodes
preferentially peer with each other.

Modelled on Libre Relay's preferential peering.
"""
from test_framework.messages import NODE_DOG_MODE
from test_framework.p2p import (
    P2P_SERVICES,
    P2PDataStore,
    P2PInterface,
)
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
    assert_greater_than,
    assert_raises_rpc_error,
)
from test_framework.wallet import MiniWallet

# Maximum number of automatic $DOG Mode peers (see net.h)
MAX_DOG_MODE_CONNECTIONS = 4

DOG_SERVICES = P2P_SERVICES | NODE_DOG_MODE


class DogModePeeringTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1

    def run_test(self):
        node = self.nodes[0]
        self.wallet = MiniWallet(node)

        self.log.info("Check that the node advertises the NODE_DOG_MODE service flag")
        local_services = int(node.getnetworkinfo()["localservices"], 16)
        assert_greater_than(local_services & NODE_DOG_MODE, 0)

        self.log.info("Open a dog connection to a peer advertising NODE_DOG_MODE")
        dog_peer = node.add_outbound_p2p_connection(
            P2PDataStore(), p2p_idx=0, connection_type="dog", services=DOG_SERVICES)

        # The peer must have been told our service flags, including NODE_DOG_MODE
        assert_greater_than(dog_peer.nServices & NODE_DOG_MODE, 0)

        # The connection shows up as a long-lived, tx-relaying "dog" connection
        peer_info = [p for p in node.getpeerinfo() if p["connection_type"] == "dog"]
        assert_equal(len(peer_info), 1)
        assert_equal(peer_info[0]["inbound"], False)
        assert_equal(peer_info[0]["relaytxes"], True)

        self.log.info("Check that transactions relay through the dog connection")
        tx = self.wallet.create_self_transfer()["tx"]
        dog_peer.send_txs_and_test([tx], node)

        self.log.info("A dog connection to a peer not advertising NODE_DOG_MODE is disconnected")
        node.add_outbound_p2p_connection(
            P2PInterface(), p2p_idx=1, connection_type="dog",
            services=P2P_SERVICES, wait_for_disconnect=True)

        self.log.info(f"Fill the remaining {MAX_DOG_MODE_CONNECTIONS - 1} dog connection slots; one more must fail")
        for i in range(1, MAX_DOG_MODE_CONNECTIONS):
            node.add_outbound_p2p_connection(
                P2PInterface(), p2p_idx=i, connection_type="dog", services=DOG_SERVICES)
        assert_equal(len([p for p in node.getpeerinfo() if p["connection_type"] == "dog"]), MAX_DOG_MODE_CONNECTIONS)
        assert_raises_rpc_error(
            -34, "Already at capacity for specified connection type",
            node.addconnection, "127.0.0.1:18333", "dog", False)


if __name__ == '__main__':
    DogModePeeringTest(__file__).main()
