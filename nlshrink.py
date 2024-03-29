import numpy as np

def pav(y):
    """
    PAV uses the pair adjacent violators method to produce a monotonic
    smoothing of y
    translated from matlab by Sean Collins (2006) as part of the EMAP toolbox
    """
    y = np.asarray(y)
    assert y.ndim == 1
    n_samples = len(y)
    v = y.copy()
    lvls = np.arange(n_samples)
    lvlsets = np.c_[lvls, lvls]
    flag = 1
    while flag:
        deriv = np.diff(v)
        if np.all(deriv >= 0):
            break

        viol = np.where(deriv < 0)[0]
        start = lvlsets[viol[0], 0]
        last = lvlsets[viol[0] + 1, 1]
        s = 0
        n = last - start + 1
        for i in range(start, last + 1):
            s += v[i]

        val = s / n
        for i in range(start, last + 1):
            v[i] = val
            lvlsets[i, 0] = start
            lvlsets[i, 1] = last
    return v

def NLSHRINK(x):
    p,n = x.shape

    C = np.dot(x,x.T)/n

    l,v = np.linalg.eigh(C)
    l,v = l[np.argsort(l)],v[:,np.argsort(l)]

    l = l[max([1,p-n+1])-1:p]
    L = np.tile(l,(min([p,n]),1)).T

    h = n**(-0.35)

    Lt = (4*(L**2)*(h**2) - (L-L.T)**2)

    ftilde = np.mean(np.sqrt(np.clip(Lt,0,np.inf))/(2*np.pi*(L.T**2)*(h**2)),axis=1)

    Hftilde = np.mean((np.sign(L - L.T) * np.sqrt(np.clip( (L-L.T)**2 -4*(L.T**2)*(h**2), 0 ,np.inf))-L+L.T)/
            (2*np.pi*(L.T**2)*(h**2)),axis=1)

    if p<=n:
        dtilde = l/((np.pi*(p/float(n))*l*ftilde)**2 + (1- (p/float(n)) -np.pi*(p/float(n))*l*Hftilde)**2)

    else:
        Hftilde0 = (1 - np.sqrt(1-4*h**2))/(2*np.pi*h**2)*np.mean(1./l)
        dtilde0 = 1./(np.pi*(p-n)/float(n)*Hftilde0)
        dtilde1 = l/(np.pi**2 * l**2*( ftilde**2+ Hftilde**2))
        dtilde = np.concatenate(([dtilde0]*(p-n),dtilde1))

    dhat = pav(dtilde)

    sigmahat = np.dot(v,(np.tile(dhat,(p,1)).T*v.T))
    return sigmahat

