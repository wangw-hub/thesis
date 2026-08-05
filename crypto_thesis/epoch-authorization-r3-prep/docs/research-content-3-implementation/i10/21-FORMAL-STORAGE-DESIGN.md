# Formal Storage Design

A future formal storage class uses an independent LocalObjectStore root and an independent loopback Kubo repository/API, with no public bootstrap or peers. Object identity is digest/CID-bound; replica state is a factor, not a hidden retry. Body plaintext and CK are excluded from evidence. No formal Kubo or object store was created.
