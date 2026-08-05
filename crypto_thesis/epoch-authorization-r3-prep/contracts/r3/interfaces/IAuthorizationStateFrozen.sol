// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.30;

/// @notice Read-only subset of the frozen research-content-2 interface.
interface IAuthorizationStateFrozen {
    enum Status { NONE, ACTIVE, SUSPENDED, REVOKED }

    struct ResourceRecord {
        address owner;
        bytes32 policyDigest;
        uint64 epoch;
        Status status;
        uint64 policyVersion;
        uint64 stateVersion;
        uint64 updatedAtBlock;
    }

    function getResource(bytes32 resourceId) external view returns (ResourceRecord memory);
}
