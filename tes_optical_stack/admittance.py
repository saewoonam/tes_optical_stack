#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 14:19:48 2021

@author: nams
"""
import numpy as np
import scipy.constants
# from functools import cache
from functools import lru_cache

import tes_optical_stack.nk_code as nk_code
nk = nk_code.load_from_materials_mat()


z0 = np.sqrt(scipy.constants.mu_0 / scipy.constants.epsilon_0)

def prop_matrix(n, t, wavelength):
    m = np.zeros([2,2], dtype=complex)
    delta = 2*np.pi*n * t /wavelength
    m[0,0] = np.cos(delta)
    m[1,1] = np.cos(delta)
    m[0,1] = 1j * z0 / n * np.sin(delta)
    m[1,0] = 1j * n / z0 * np.sin(delta)
    return m

def Power(v):
    E = v[0]
    H = v[1]
    P = (E * H.conjugate()).real / 2
    return P

def stack(n_list, t_list, wavelength):
    n_a = n_list[0]  # incoming media index of refraction
    n_b = n_list[-1]  # outgoing media index of refraction

    v = np.array([[1], [n_b/z0]], dtype=complex)  # vector at the end of the stack
    P_tr = Power(v)  # calculate Poynting vector power
    # poynting = [P_tr]  # construct array poynting vector power at each interface
    #print('P_tr', P_tr)
    poynting = np.zeros(max(len(t_list)-1, 1))
    poynting[-1] = P_tr
    for idx in range(len(t_list)-2, 0, -1):
        #print(idx, n_list[idx], t_list[idx])
        m = prop_matrix(n_list[idx], t_list[idx], wavelength)
        v = np.dot(m, v)
        #v = np.einsum('ij, jk -> ik', m, v)
        poynting[idx-1] = Power(v)
        #print(idx, Power(v),len(poynting), poynting )
        #poynting.append(Power(v))

    E = v[0]
    H = v[1]
    # convert to forward and backward E-fileds
    E_p = (E + z0/n_a * H) / 2
    E_m = (E - z0/n_a * H) / 2
    
    # Calculate power incident and reflected using E_p and E_m
    #P = (E * H.conjugate()).real / 2
    P_inc = np.real((abs(E_p)**2 )/2 * n_a / z0)
    P_ref = np.real((abs(E_m)**2 )/2 * n_a / z0)
    # normalize poynting vector powers to incoming power
    poynting = poynting / P_inc
    results = {'R': P_ref/P_inc, 'T':P_tr/P_inc, 'poynting':poynting}
    #return P_tr/P_inc, P_ref/P_inc, (1-(P_ref+P_tr)/P_inc), poynting #, v[0], v[1]
    return results

def poynting(v):
    return np.real(v[:, 0, 0]*np.conj(v[:,1,0])/2)

#@cache
@lru_cache(maxsize=10)
def build_stack_nk(stack_description, vac_lambdas):
    # build matrix of indices of refraction
    #  each row is a different wavelength
    #  each column is a different layer
    #  arguments should be tuples so that it can cache

    global nk
    stack_nk = None
    for name in stack_description:
        # print(nk[name].name, nk[name].min, nk[name].max)
        current = nk[name](vac_lambdas)
        if stack_nk is None:
            stack_nk = current
        else:
            stack_nk = np.column_stack([stack_nk, current])
    return stack_nk

def stack_v2(stack_description, t_list, vac_lambdas):
    if isinstance(vac_lambdas, (list, np.ndarray)):
        vac_lambdas = np.array(vac_lambdas)
    else:
        vac_lambdas = np.array([vac_lambdas])
    t_list = np.array(t_list)

    stack_nk = build_stack_nk(tuple(stack_description), tuple(vac_lambdas))

    n_a = stack_nk[:,0]
    n_b = stack_nk[:,-1]
    n = stack_nk[:,1:-1]
    # print('n:\r\n',n)
    #  calculate propagation matrix for each layer
    P = np.zeros((len(vac_lambdas), len(stack_description)-2, 2, 2), dtype=complex)
    delta = 2 * np.pi * stack_nk[:,1:-1] / vac_lambdas[:,None] * t_list[1:-1]
    
    P[:,:,0, 0] = np.cos(delta)
    P[:,:,1, 1] = np.cos(delta)
    P[:,:,0, 1] = 1j * z0 / n * np.sin(delta)
    P[:,:,1, 0] = 1j * n / z0 * np.sin(delta)
    
    # calculate output fields
    v = np.ones((len(vac_lambdas), 2, 1), dtype=complex)
    v[:,-1,0] = n_b/z0

    # calculate power out
    p = poynting(v)
    # calculate new E and H for each layer + power flow
    idx = 0
    while idx<P.shape[1]:
        idx +=1
        v = np.einsum('ijk, ikl -> ijl', P[:, -idx, :, :], v)
        p = np.column_stack([poynting(v), p])
    
    # calculate matrix to convert E and H vector to E+ and E- vector
    M = np.ones( (len(vac_lambdas), 2, 2), dtype=complex)
    M[:,0, 1] = z0/n_a
    M[:,1, 1] = -z0/n_a
    M = M/2
    # print(M,v)
    Epm = np.einsum('ijk, ikl -> ijl', M, v)
    # print(M,v, Epm)
    Ppm = np.real(np.abs(Epm)**2 /2 /z0 * n_a[:, None, None])
    
    # Normalize poynting vector to incoming power
    p = p / Ppm[:,0,0][:,None]
    # Calculate absorption in each layer
    A = -np.diff(p)
    # Round numbers close to zero to zero
    A[np.isclose(A,0)] = 0

    Ppm = Ppm / Ppm[:,0,0][:, None, None]
    RT = np.column_stack([Ppm[:,1,0], p[:,-1]])
    RAT = np.column_stack([Ppm[:,1,0], A, p[:,-1]])
    # results = {'v':v, 'P':P, 'delta':delta, 'Ppm':Ppm, 'Epm':Epm,
    results = {
            'stack_nk':stack_nk, 'vac_lambdas':vac_lambdas,
            #'p':p, 'A':A, 'RT': RT,
            'RAT': RAT,
            }
    #return stack_nk, n_a, n_b, v, P, delta
    return results

