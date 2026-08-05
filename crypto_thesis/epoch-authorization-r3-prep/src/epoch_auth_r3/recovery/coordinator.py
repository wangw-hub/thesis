from __future__ import annotations

from enum import StrEnum

from .reconciler import FullReconcilerV1


class RecoveryMode(StrEnum):
    RECONCILE_RESOURCE = "RECONCILE_RESOURCE"
    RECONCILE_OPERATION = "RECONCILE_OPERATION"
    RECONCILE_EVENT = "RECONCILE_EVENT"
    RECONCILE_ALL_BOUNDED = "RECONCILE_ALL_BOUNDED"


class RecoveryCoordinator:
    def __init__(self, reconciler: FullReconcilerV1):
        self.reconciler = reconciler
        self.material_release_enabled = False

    def reconcile_resource(self, evidence):
        self.material_release_enabled = False
        result = self.reconciler.classify(evidence)
        self.material_release_enabled = result.material_release_allowed
        return result

    def reconcile_all_bounded(self, evidence, *, limit=100):
        self.material_release_enabled = False
        results = self.reconciler.reconcile_all_bounded(evidence, limit=limit)
        self.material_release_enabled = bool(results) and all(
            item.material_release_allowed for item in results
        )
        return results
