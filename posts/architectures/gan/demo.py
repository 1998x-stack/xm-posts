"""Finite categorical GAN: inspect its best-response discriminator and JS objective."""
from math import log

REAL = (0.6, 0.3, 0.1)
START = (0.15, 0.2, 0.65)

def generated(t):
    if not 0 <= t <= 1:
        raise ValueError("t outside [0,1]")
    return tuple((1-t)*q+t*p for p,q in zip(REAL, START))

def optimal_discriminator(p, q):
    assert len(p) == len(q) and abs(sum(p)-1)<1e-12 and abs(sum(q)-1)<1e-12
    return tuple(a/(a+b) if a+b else .5 for a,b in zip(p,q))

def kl(p, q):
    return sum(a*log(a/b) for a,b in zip(p,q) if a)

def jsd(p, q):
    m = tuple((a+b)/2 for a,b in zip(p,q))
    return (kl(p,m)+kl(q,m))/2

def game_value(p, q):
    d = optimal_discriminator(p,q)
    return sum(a*log(v)+b*log(1-v) for a,b,v in zip(p,q,d) if a and b)

if __name__ == "__main__":
    for t in (0,.5,1):
        q = generated(t)
        d = optimal_discriminator(REAL,q)
        value = game_value(REAL,q)
        assert abs(value - (-log(4)+2*jsd(REAL,q))) < 1e-12
        print(t, q, d, jsd(REAL,q))
