// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.30;

import "./AccessRoles.sol";

/// @notice Consensus-ordered public authorization state. No secrets are stored.
contract AuthorizationState is AccessRoles {
    enum Status {
        NONE,
        ACTIVE,
        SUSPENDED,
        REVOKED
    }

    struct ResourceRecord {
        address owner;
        bytes32 policyDigest;
        uint64 epoch;
        Status status;
        uint64 policyVersion;
        uint64 stateVersion;
        uint64 updatedAtBlock;
    }

    struct UserRecord {
        address account;
        bytes32 userKeyId;
        Status status;
        uint64 userVersion;
        uint64 updatedAtBlock;
    }

    mapping(bytes32 resourceId => ResourceRecord) private _resources;
    mapping(bytes32 userId => UserRecord) private _users;
    mapping(bytes32 keyId => bytes32 userId) private _keyOwners;

    error AlreadyExists(bytes32 id);
    error NotFound(bytes32 id);
    error InvalidDigest();
    error InvalidTransition(Status from, Status to);
    error DuplicateKey(bytes32 keyId);
    error NotResourceOwner(address expected, address actual);

    event ResourceRegistered(
        bytes32 indexed resourceId,
        address indexed owner,
        bytes32 policyDigest,
        uint64 epoch,
        uint64 policyVersion
    );
    event PolicyUpdated(
        bytes32 indexed resourceId,
        bytes32 oldDigest,
        bytes32 newDigest,
        uint64 epoch,
        uint64 policyVersion
    );
    event EpochAdvanced(bytes32 indexed resourceId, uint64 oldEpoch, uint64 newEpoch, bytes32 reasonHash);
    event ResourceStatusChanged(bytes32 indexed resourceId, Status oldStatus, Status newStatus, uint64 epoch);
    event UserRegistered(bytes32 indexed userId, address indexed account, bytes32 userKeyId, uint64 userVersion);
    event UserKeyRotated(bytes32 indexed userId, bytes32 oldKeyId, bytes32 newKeyId, uint64 userVersion);
    event UserStatusChanged(bytes32 indexed userId, Status oldStatus, Status newStatus, uint64 userVersion);

    function registerResource(
        bytes32 resourceId,
        address owner,
        bytes32 policyDigest
    ) external onlyRole(OWNER_ROLE) {
        if (_resources[resourceId].status != Status.NONE) revert AlreadyExists(resourceId);
        if (owner == address(0)) revert ZeroAddress();
        if (policyDigest == bytes32(0)) revert InvalidDigest();
        ResourceRecord memory record = ResourceRecord(
            owner,
            policyDigest,
            1,
            Status.ACTIVE,
            1,
            1,
            uint64(block.number)
        );
        _resources[resourceId] = record;
        emit ResourceRegistered(resourceId, owner, policyDigest, 1, 1);
    }

    function updatePolicy(bytes32 resourceId, bytes32 policyDigest) external {
        ResourceRecord storage record = _resource(resourceId);
        _requireOwnerOrRole(record.owner, OWNER_ROLE);
        if (record.status == Status.REVOKED) revert InvalidTransition(Status.REVOKED, Status.ACTIVE);
        if (policyDigest == bytes32(0)) revert InvalidDigest();
        bytes32 oldDigest = record.policyDigest;
        record.policyDigest = policyDigest;
        record.policyVersion += 1;
        record.epoch += 1;
        record.stateVersion += 1;
        record.updatedAtBlock = uint64(block.number);
        emit PolicyUpdated(resourceId, oldDigest, policyDigest, record.epoch, record.policyVersion);
    }

    function advanceEpoch(bytes32 resourceId, bytes32 reasonHash) external {
        if (!hasRole(AUTHORIZER_ROLE, msg.sender) && !hasRole(REVOCATION_ROLE, msg.sender)) {
            revert AccessDenied(AUTHORIZER_ROLE, msg.sender);
        }
        ResourceRecord storage record = _resource(resourceId);
        if (record.status == Status.REVOKED) revert InvalidTransition(Status.REVOKED, Status.REVOKED);
        uint64 oldEpoch = record.epoch;
        record.epoch += 1;
        record.stateVersion += 1;
        record.updatedAtBlock = uint64(block.number);
        emit EpochAdvanced(resourceId, oldEpoch, record.epoch, reasonHash);
    }

    function suspendResource(bytes32 resourceId) external onlyRole(REVOCATION_ROLE) {
        _setResourceStatus(resourceId, Status.SUSPENDED);
    }

    function activateResource(bytes32 resourceId) external onlyRole(REVOCATION_ROLE) {
        _setResourceStatus(resourceId, Status.ACTIVE);
    }

    function revokeResource(bytes32 resourceId) external onlyRole(REVOCATION_ROLE) {
        _setResourceStatus(resourceId, Status.REVOKED);
    }

    function getResource(bytes32 resourceId) external view returns (ResourceRecord memory) {
        ResourceRecord memory record = _resources[resourceId];
        if (record.status == Status.NONE) revert NotFound(resourceId);
        return record;
    }

    function registerUser(
        bytes32 userId,
        address account,
        bytes32 userKeyId
    ) external onlyRole(ADMIN_ROLE) {
        if (_users[userId].status != Status.NONE) revert AlreadyExists(userId);
        if (account == address(0)) revert ZeroAddress();
        if (userKeyId == bytes32(0)) revert InvalidDigest();
        if (_keyOwners[userKeyId] != bytes32(0)) revert DuplicateKey(userKeyId);
        _users[userId] = UserRecord(account, userKeyId, Status.ACTIVE, 1, uint64(block.number));
        _keyOwners[userKeyId] = userId;
        emit UserRegistered(userId, account, userKeyId, 1);
    }

    function rotateUserKey(bytes32 userId, bytes32 newKeyId) external {
        UserRecord storage record = _user(userId);
        if (msg.sender != record.account && !hasRole(ADMIN_ROLE, msg.sender)) {
            revert AccessDenied(ADMIN_ROLE, msg.sender);
        }
        if (record.status == Status.REVOKED) revert InvalidTransition(Status.REVOKED, Status.REVOKED);
        if (newKeyId == bytes32(0)) revert InvalidDigest();
        if (_keyOwners[newKeyId] != bytes32(0)) revert DuplicateKey(newKeyId);
        bytes32 oldKeyId = record.userKeyId;
        delete _keyOwners[oldKeyId];
        _keyOwners[newKeyId] = userId;
        record.userKeyId = newKeyId;
        record.userVersion += 1;
        record.updatedAtBlock = uint64(block.number);
        emit UserKeyRotated(userId, oldKeyId, newKeyId, record.userVersion);
    }

    function suspendUser(bytes32 userId) external onlyRole(REVOCATION_ROLE) {
        _setUserStatus(userId, Status.SUSPENDED);
    }

    function activateUser(bytes32 userId) external onlyRole(REVOCATION_ROLE) {
        _setUserStatus(userId, Status.ACTIVE);
    }

    function revokeUser(bytes32 userId) external onlyRole(REVOCATION_ROLE) {
        _setUserStatus(userId, Status.REVOKED);
    }

    function getUser(bytes32 userId) external view returns (UserRecord memory) {
        UserRecord memory record = _users[userId];
        if (record.status == Status.NONE) revert NotFound(userId);
        return record;
    }

    function _resource(bytes32 resourceId) private view returns (ResourceRecord storage record) {
        record = _resources[resourceId];
        if (record.status == Status.NONE) revert NotFound(resourceId);
    }

    function _user(bytes32 userId) private view returns (UserRecord storage record) {
        record = _users[userId];
        if (record.status == Status.NONE) revert NotFound(userId);
    }

    function _requireOwnerOrRole(address owner, bytes32 role) private view {
        if (msg.sender != owner && !hasRole(role, msg.sender)) {
            revert NotResourceOwner(owner, msg.sender);
        }
    }

    function _setResourceStatus(bytes32 resourceId, Status target) private {
        ResourceRecord storage record = _resource(resourceId);
        Status oldStatus = record.status;
        bool legal = (oldStatus == Status.ACTIVE && (target == Status.SUSPENDED || target == Status.REVOKED))
            || (oldStatus == Status.SUSPENDED && (target == Status.ACTIVE || target == Status.REVOKED));
        if (!legal) revert InvalidTransition(oldStatus, target);
        record.status = target;
        record.epoch += 1;
        record.stateVersion += 1;
        record.updatedAtBlock = uint64(block.number);
        emit ResourceStatusChanged(resourceId, oldStatus, target, record.epoch);
    }

    function _setUserStatus(bytes32 userId, Status target) private {
        UserRecord storage record = _user(userId);
        Status oldStatus = record.status;
        bool legal = (oldStatus == Status.ACTIVE && (target == Status.SUSPENDED || target == Status.REVOKED))
            || (oldStatus == Status.SUSPENDED && (target == Status.ACTIVE || target == Status.REVOKED));
        if (!legal) revert InvalidTransition(oldStatus, target);
        record.status = target;
        record.userVersion += 1;
        record.updatedAtBlock = uint64(block.number);
        emit UserStatusChanged(userId, oldStatus, target, record.userVersion);
    }
}
