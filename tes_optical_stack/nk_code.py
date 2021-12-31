import scipy.io
import tes_optical_stack.fuzzydict as fuzzydict
import numpy as np
from scipy.interpolate import interp1d
from functools import partial
import os

def air(vac_lambdas):
    vac_lambdas = np.array(vac_lambdas)
    #print('air', vac_lambdas) #, len(vac_lambdas))
    return np.ones(len(vac_lambdas), dtype=complex) 
air.min = 0
air.max = np.inf
air.nk = np.array([[0, 1, 0], [np.inf, 1, 0]])
air.name = 'air'
#nk['air'] = air
def n(vac_lambdas, n=1):
    vac_lambdas = np.array(vac_lambdas)
    #print('air', vac_lambdas) #, len(vac_lambdas))
    return n*np.ones(len(vac_lambdas), dtype=complex) 
def constant_n(constant):
    fn = partial(n, n=constant)
    fn.min = 0
    fn.max = np.inf
    fn.nk = np.array([[0, constant, 0], [np.inf, constant, 0]])
    fn.name = f'constant {constant}'
    return fn

def load_from_materials_mat():
    """
        load nk data from materials.mat file and use the values to 
        construct a python dictionary of functions that will
        interpolate (linear) the complex index of refraction using
        the tabulated data that is loaded
    """
    p = os.path.dirname(__file__)
    filename = os.path.join(p,'materials.mat')
    d = scipy.io.loadmat(filename)
    materials = d['materials']
    materials = materials.ravel()

    nk_dict={'air': air}
    for idx in range(len(materials)):
        name = str(materials[idx][0]).split("'")[1]
        # print(name)
        if name not in nk_dict.keys():
            # print('add to dictionary')
            nk = materials[idx][1]
            # need to sort by wavlength so interp algorithms work
            nk = nk[np.argsort(nk[:,0])]
            #nk_dict[name] = nk
            fn = interp1d(nk[:,0].astype(np.double), nk[:,1]-1j*nk[:,2], kind='linear')
            fn.min = nk[:,0].min()
            fn.max = nk[:,0].max()
            fn.nk = nk
            fn.name = name
            nk_dict[name] = fn
    return fuzzydict.FuzzyDict(nk_dict)

