import numpy as np
import numpy.linalg as linalg
mu = np.array([0.0427,0.0015,0.0285])
sigma = np.array([[0.100**2,0.0018,0.0011],[0.0018,0.1044**2,0.0026],[0.0011,0.0026,0.1411**2]])
l = len(mu)
A = np.zeros((l+2,l+2),dtype=float)
o = np.ones((l,),dtype=float)

# define matrix A
A[0:l,0:l] = sigma*2.0
A[0:l,l] = np.transpose(mu)
A[l,0:l] = mu
A[0:l,l+1] = np.transpose(o)
A[l+1,0:l] = o

# define matrix b
b = np.zeros((l+2,),dtype=float)
b[l] = 0.0427
b[l+1] = 1.0

x = np.dot(linalg.inv(A),b)
