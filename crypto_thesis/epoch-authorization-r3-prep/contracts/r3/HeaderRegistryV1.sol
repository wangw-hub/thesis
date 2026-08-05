// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.30;

import "./interfaces/IAuthorizationStateFrozen.sol";

/// @notice Immutable anchors for versioned headers; no secret material is stored.
contract HeaderRegistryV1 {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant HEADER_COMMITTER_ROLE = keccak256("HEADER_COMMITTER_ROLE");

    enum HeaderUpdateKind { INITIAL, HEADER_ONLY, BODY_ROTATION }

    struct HeaderAnchorV1 {
        bytes32 operationId;
        bytes32 resourceId;
        bytes32 policyDigest;
        uint64 epoch;
        uint64 stateVersion;
        uint64 headerVersion;
        uint64 bodyVersion;
        uint64 keyVersion;
        HeaderUpdateKind updateKind;
        bytes32 previousHeaderDigest;
        bytes32 headerDigest;
        bytes32 headerObjectDigest;
        bytes32 bodyObjectDigest;
        address committer;
        uint64 committedAtBlock;
        bool exists;
    }

    IAuthorizationStateFrozen public immutable authorizationState;
    mapping(bytes32 role => mapping(address account => bool)) private _roles;
    mapping(bytes32 operationId => bool) public operationUsed;
    mapping(bytes32 resourceId => HeaderAnchorV1) private _current;
    mapping(bytes32 resourceId => mapping(uint64 headerVersion => HeaderAnchorV1)) private _history;

    error AccessDenied(bytes32 role, address account);
    error ZeroAddress();
    error InvalidAuthorizationState(address account);
    error OperationAlreadyUsed(bytes32 operationId);
    error InvalidDigest();
    error ResourceNotActive(bytes32 resourceId);
    error AuthorizationStateMismatch(bytes32 resourceId);
    error InvalidVersionTransition(bytes32 resourceId);

    event RoleGranted(bytes32 indexed role, address indexed account, address indexed sender);
    event HeaderCommittedV1(
        bytes32 indexed resourceId,
        uint64 indexed headerVersion,
        bytes32 indexed operationId,
        uint64 bodyVersion,
        uint64 keyVersion,
        HeaderUpdateKind updateKind,
        bytes32 headerDigest,
        bytes32 bodyObjectDigest
    );

    constructor(address authorizationStateAddress) {
        if (authorizationStateAddress == address(0)) revert ZeroAddress();
        if (authorizationStateAddress.code.length == 0) {
            revert InvalidAuthorizationState(authorizationStateAddress);
        }
        authorizationState = IAuthorizationStateFrozen(authorizationStateAddress);
        _roles[ADMIN_ROLE][msg.sender] = true;
        emit RoleGranted(ADMIN_ROLE, msg.sender, msg.sender);
    }

    modifier onlyRole(bytes32 role) {
        if (!_roles[role][msg.sender]) revert AccessDenied(role, msg.sender);
        _;
    }

    function hasRole(bytes32 role, address account) external view returns (bool) {
        return _roles[role][account];
    }

    function grantRole(bytes32 role, address account) external onlyRole(ADMIN_ROLE) {
        if (account == address(0)) revert ZeroAddress();
        _roles[role][account] = true;
        emit RoleGranted(role, account, msg.sender);
    }

    function revokeRole(bytes32 role, address account) external onlyRole(ADMIN_ROLE) {
        _roles[role][account] = false;
    }

    function getCurrentAnchor(bytes32 resourceId) external view returns (HeaderAnchorV1 memory) {
        return _current[resourceId];
    }

    function getAnchor(bytes32 resourceId, uint64 headerVersion)
        external view returns (HeaderAnchorV1 memory)
    {
        return _history[resourceId][headerVersion];
    }

    function commitHeaderV1(HeaderAnchorV1 calldata candidate)
        external onlyRole(HEADER_COMMITTER_ROLE)
    {
        if (candidate.operationId == bytes32(0) || candidate.resourceId == bytes32(0)
            || candidate.headerDigest == bytes32(0)
            || candidate.headerObjectDigest == bytes32(0)
            || candidate.bodyObjectDigest == bytes32(0)) revert InvalidDigest();
        if (operationUsed[candidate.operationId]) revert OperationAlreadyUsed(candidate.operationId);
        if (candidate.keyVersion != candidate.bodyVersion) {
            revert InvalidVersionTransition(candidate.resourceId);
        }

        IAuthorizationStateFrozen.ResourceRecord memory authorization =
            authorizationState.getResource(candidate.resourceId);
        if (authorization.status != IAuthorizationStateFrozen.Status.ACTIVE) {
            revert ResourceNotActive(candidate.resourceId);
        }
        if (candidate.policyDigest != authorization.policyDigest
            || candidate.epoch != authorization.epoch
            || candidate.stateVersion != authorization.stateVersion) {
            revert AuthorizationStateMismatch(candidate.resourceId);
        }

        HeaderAnchorV1 storage prior = _current[candidate.resourceId];
        _validateTransition(prior, candidate);

        HeaderAnchorV1 memory committed = candidate;
        committed.committer = msg.sender;
        committed.committedAtBlock = uint64(block.number);
        committed.exists = true;
        _history[candidate.resourceId][candidate.headerVersion] = committed;
        _current[candidate.resourceId] = committed;
        operationUsed[candidate.operationId] = true;

        emit HeaderCommittedV1(
            candidate.resourceId, candidate.headerVersion, candidate.operationId,
            candidate.bodyVersion, candidate.keyVersion, candidate.updateKind,
            candidate.headerDigest, candidate.bodyObjectDigest
        );
    }

    function _validateTransition(
        HeaderAnchorV1 storage prior,
        HeaderAnchorV1 calldata candidate
    ) private view {
        if (!prior.exists) {
            if (candidate.updateKind != HeaderUpdateKind.INITIAL
                || candidate.headerVersion != 1 || candidate.bodyVersion != 1
                || candidate.keyVersion != 1 || candidate.previousHeaderDigest != bytes32(0)) {
                revert InvalidVersionTransition(candidate.resourceId);
            }
            return;
        }
        if (candidate.headerVersion != prior.headerVersion + 1
            || candidate.previousHeaderDigest != prior.headerDigest) {
            revert InvalidVersionTransition(candidate.resourceId);
        }
        if (candidate.updateKind == HeaderUpdateKind.HEADER_ONLY) {
            if (candidate.bodyVersion != prior.bodyVersion
                || candidate.keyVersion != prior.keyVersion
                || candidate.bodyObjectDigest != prior.bodyObjectDigest) {
                revert InvalidVersionTransition(candidate.resourceId);
            }
        } else if (candidate.updateKind == HeaderUpdateKind.BODY_ROTATION) {
            if (candidate.bodyVersion != prior.bodyVersion + 1
                || candidate.keyVersion != prior.keyVersion + 1
                || candidate.bodyObjectDigest == prior.bodyObjectDigest) {
                revert InvalidVersionTransition(candidate.resourceId);
            }
        } else {
            revert InvalidVersionTransition(candidate.resourceId);
        }
    }
}
