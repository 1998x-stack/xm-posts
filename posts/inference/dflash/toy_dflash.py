"""Deterministic teaching invariants, not model inference."""
from math import isclose

def greedy_commit(draft, target):
    if len(target) != len(draft) + 1:
        raise ValueError("need g+1 target predictions")
    n = 0
    for d, t in zip(draft, target):
        if d != t:
            break
        n += 1
    return draft[:n] + [target[n]]

def visible(anchor, block, key_position=None, key_block=None):
    if key_block is not None:
        return key_block == block
    return key_position is not None and key_position < anchor

def expected_commit(g, alpha):
    if g < 0 or not 0 <= alpha <= 1:
        raise ValueError("invalid budget or acceptance")
    return sum(alpha**k for k in range(g+1))

def corrected_mass(p, q):
    if len(p) != len(q) or not p or min(p+q)<0 or not isclose(sum(p),1) or not isclose(sum(q),1):
        raise ValueError("invalid categorical distributions")
    return [min(x,y)+max(0,x-y) for x,y in zip(p,q)]

def self_test():
    assert greedy_commit([1,2,9,4],[1,2,3,4,5]) == [1,2,3]
    assert greedy_commit([1,2],[1,2,3]) == [1,2,3]
    assert greedy_commit([9],[1,2]) == [1]
    assert visible(3,0,key_position=2)
    assert not visible(3,0,key_position=3)
    assert visible(3,0,key_block=0)
    assert not visible(3,0,key_block=1)
    assert isclose(expected_commit(4,.8),3.3616)
    assert expected_commit(4,0)==1
    assert expected_commit(4,1)==5
    assert all(isclose(x,y) for x,y in zip(corrected_mass([.5,.3,.2],[.2,.7,.1]),[.5,.3,.2]))

if __name__ == "__main__":
    self_test()
    print("DFlash toy invariants passed")
