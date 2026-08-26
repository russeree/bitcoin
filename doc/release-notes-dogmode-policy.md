$DOG Mode policy changes
========================

This release relaxes several transaction relay policies, so that $DOG Mode
nodes relay and mine a wider range of transactions. Nodes with the old
policies will not relay these transactions, so $DOG Mode nodes additionally
preferentially peer with each other (see below).

Policy
------

- The maximum standard transaction weight has been raised from 400,000 WU
  (100 kvB) to 3,900,000 WU (975 kvB), just under the 4,000,000 WU consensus
  block weight limit. Transactions larger than 975 kvB remain non-standard.
  The mempool cluster size limit default (`-limitclustersize`) is raised
  accordingly from 101 kvB to 976 kvB, and the maximum package weight for
  package relay from 404,000 WU to 3,904,000 WU.

- Since `MAX_OP_RETURN_RELAY` is defined as one quarter of the maximum
  standard transaction weight, the default `-datacarriersize` rises from
  100,000 to 975,000 bytes.

- The minimum `-maxmempool` value remains ~5 MB; the sanity check tying it to
  the cluster size limit now requires 5x (was 40x) the cluster size limit.

- The dust limit is lowered from 294-546 sats (depending on output type) to a
  global 1 sat: only zero-value spendable outputs are now considered dust.
  `-dustrelayfee` is retained, but it can only lower the dust limit further
  (0 disables it entirely, as before), never raise it above 1 sat.

P2P
---

- Nodes now advertise the `NODE_DOG_MODE` service flag (bit 28) and open up to
  4 extra long-lived outbound connections ("dog" connection type) to peers
  advertising the same flag, so that $DOG Mode nodes preferentially peer with
  each other. This is a port of Libre Relay's preferential peering (which uses
  bit 29). Peers connected to via a dog connection that do not advertise
  `NODE_DOG_MODE` are disconnected after the version handshake.

- The "dog" connection type is visible in `getpeerinfo`, `bitcoin-cli
  -netinfo` and the GUI peers window.
