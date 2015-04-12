import numpy as np
from scipy.sparse import diags, eye
from scipy.sparse.linalg import inv
from scipy.linalg import inv as inv2

def nextPow2(value):
    """
    Return the power of 2 immediately superior to this value
    """
    p = 1
    while p < value:
        p <<= 1 # shift one bit until we're good
    return p

def detrend(values):
  """
  From "An advanced detrending method with application to HRV analysis." ,T arvainen MP, Ranta-Aho PO, Karjalainen PA., 2002
  Get a 1D numpy array, return detrended array
  """
  T = len(values)
  lamb = 10
  I = eye(T)
  # instead of using Matlab speye/ones/spdiags, use scipy sparse.diags on the right list
  L = [1,-2,1]+[0]*(T-2-3)
  D2 = diags(L, range(len(L)), shape=(len(L), len(L)+2))
  return ((I-inv(I + (lamb**2)*D2.H*D2))*values)

def detrend2(values):
  """
  alternate version, see http://stackoverflow.com/questions/21693613/is-it-possible-to-compute-an-inverse-of-sparse-matrix-in-python-as-fast-as-in-ma
  """
  T = len(values)
  lamb = 10
  I = eye(T)
  # instead of using Matlab speye/ones/spdiags, use scipy sparse.diags on the right list
  L = [1,-2,1]+[0]*(T-2-3)
  D2 = diags(L, range(len(L)), shape=(len(L), len(L)+2))
  A = I + (lamb**2)*D2.H*D2
  lu = splu(A)
  invo = lu.solve(I.todense())
  # same format as detrend()
  return np.asarray(((I-invo)*np.matrix(values).H).H)[0]

def detrend3(values):
  """
  yet another one, may be closer to detrend()
  """
  T = len(values)
  lamb = 10
  I = eye(T)
  # instead of using Matlab speye/ones/spdiags, use scipy sparse.diags on the right list
  L = [1,-2,1]+[0]*(T-2-3)
  D2 = diags(L, range(len(L)), shape=(len(L), len(L)+2))
  A = I + (lamb**2)*D2.H*D2
  # same format as detrend()
  return np.asarray(((I- inv2(A.todense()))  * np.matrix(values).H).H)[0]

