// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.30;

interface IAuthorizationState {
    enum Status { NONE, ACTIVE, SUSPENDED, REVOKED }

    struct ResourceRecord {
        address owner;
        bytes32 policyDigest;
        uint64 epoch;
        Status status;
        uint64 policyVersion;
        uint64 updatedAtBlock;
    }

    struct UserRecord {
        address account;
        bytes32 userKeyId;
        Status status;
        uint64 userVersion;
        uint64 updatedAtBlock;
    }

    function getResource(bytes32 resourceId) external view returns (ResourceRecord memory);
    function getUser(bytes32 userId) external view returns (UserRecord memory);
}
