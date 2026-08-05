# CompositeStateDecoderV1

`CompositeStateDecoderV1` accepts only the exact frozen ABI tuple shapes, checks every field type, bytes32 width, address syntax, and non-negative integer, and returns named immutable records. Invalid or extra/missing fields fail closed. Callers no longer use bare ABI tuple indices.
