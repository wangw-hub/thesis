class IpfsReplicaError(Exception):
    """Base fail-closed IPFS replica error."""


class InvalidCidError(IpfsReplicaError):
    pass


class ReplicaVerificationError(IpfsReplicaError):
    pass


class KuboUnavailableError(IpfsReplicaError):
    pass
