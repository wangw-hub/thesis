# CompositeState root cause

The failed runner accessed an ABI tuple by incorrect positional indices. The frozen HeaderRegistry return is a 16-field tuple; the erroneous comparison mixed a bytes value with an integer, producing `TypeError`. This was a client decoding defect, not an AuthorizationState, HeaderRegistry, ABI, or chain defect.
