# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Filip Wasilewski <http://filipwasilewski.pl/>
# See COPYING for license details.

# $Id: multidim.py 154 2010-03-13 13:18:59Z filipw $

"""
2D Discrete Wavelet Transform and Inverse Discrete Wavelet Transform.
"""

__all__ = ['dwt2', 'idwt2', 'swt2', 'dwtn']

from itertools import izip, cycle

from _pywt import Wavelet, MODES
from _pywt import dwt, idwt, swt, downcoef
from numerix import transpose, array, as_float_array, default_dtype, apply_along_axis


def dwt2(data, wavelet, mode='sym'):
    """
    2D Discrete Wavelet Transform.

    data    - 2D array with input data
    wavelet - wavelet to use (Wavelet object or name string)
    mode    - signal extension mode, see MODES

    Returns approximaion and three details 2D coefficients arrays.

    The result form four 2D coefficients arrays organized in tuples:

        (approximation,
                (horizontal details,
                vertical details,
                diagonal details)
        )

    which sometimes is also interpreted as layed out in one 2D array
    of coefficients, where:

                                -----------------
                                |       |       |
                                | A(LL) | H(LH) |
                                |       |       |
        (A, (H, V, D))  <--->   -----------------
                                |       |       |
                                | V(HL) | D(HH) |
                                |       |       |
                                -----------------
    """

    data = as_float_array(data)
    if len(data.shape) != 2:
        raise ValueError("Expected 2D data array")

    if not isinstance(wavelet, Wavelet):
        wavelet = Wavelet(wavelet)

    mode = MODES.from_object(mode)

    # filter rows
    H, L = [], []
    append_L = L.append; append_H = H.append
    for row in data:
        cA, cD = dwt(row, wavelet, mode)
        append_L(cA)
        append_H(cD)
    del data

    # filter columns
    H = transpose(H)
    L = transpose(L)

    LL, LH = [], []
    append_LL = LL.append; append_LH = LH.append
    for row in L:
        cA, cD = dwt(array(row, default_dtype), wavelet, mode)
        append_LL(cA)
        append_LH(cD)
    del L

    HL, HH = [], []
    append_HL = HL.append; append_HH = HH.append
    for row in H:
        cA, cD = dwt(array(row, default_dtype), wavelet, mode)
        append_HL(cA)
        append_HH(cD)
    del H

    # build result structure
    #     (approx.,        (horizontal,    vertical,       diagonal))
    ret = (transpose(LL), (transpose(LH), transpose(HL), transpose(HH)))

    return ret

def idwt2(coeffs, wavelet, mode='sym'):
    """
    2D Inverse Discrete Wavelet Transform. Reconstruct data from coefficients
    arrays.

    coeffs  - four 2D coefficients arrays arranged as follows (in the same way
              as dwt2 output -- see dwt2 description for details):

        (approximation,
                (horizontal details,
                vertical details,
                diagonal details)
        )

    wavelet - wavelet to use (Wavelet object or name string)
    mode    - signal extension mode, see MODES
    """

    if len(coeffs) != 2 or len(coeffs[1]) != 3:
        raise ValueError("Invalid coeffs param")

    # L -low-pass data, H - high-pass data
    LL, (LH, HL, HH) = coeffs

    if not LL is None: LL = transpose(LL)
    if not LH is None: LH = transpose(LH)
    if not HL is None: HL = transpose(HL)
    if not HH is None: HH = transpose(HH)

    all_none = True
    for arr in (LL, LH, HL, HH):
        if arr is not None:
            all_none = False
            if len(arr.shape) != 2:
                raise TypeError("All input coefficients arrays must be 2D.")
    del arr
    if all_none:
        raise ValueError("At least one input coefficients array must not be None.")

    if not isinstance(wavelet, Wavelet):
        wavelet = Wavelet(wavelet)

    mode = MODES.from_object(mode)

    # idwt columns
    L = []; append_L = L.append
    if LL is None and LH is None:
        L = None
    else:
        if LL is None: LL = cycle([None]) # IDWT can handle None input values - equals to zero-array
        if LH is None: LH = cycle([None]) # IDWT can handle None input values - equals to zero-array
        for rowL, rowH in izip(LL, LH):
            append_L(idwt(rowL, rowH, wavelet, mode, 1))
    del LL, LH

    H = []
    append_H = H.append
    if HL is None and HH is None:
        H = None
    else:
        if HL is None: HL = cycle([None]) # IDWT can handle None input values - equals to zero-array
        if HH is None: HH = cycle([None]) # IDWT can handle None input values - equals to zero-array
        for rowL, rowH in izip(HL, HH):
            append_H(idwt(rowL, rowH, wavelet, mode, 1))
    del HL, HH

    if L is not None:
        L = transpose(L)
    if H is not None:
        H = transpose(H)

    # idwt rows
    data = []
    append_data = data.append
    if L is None: L = cycle([None]) # IDWT can handle None input values - equals to zero-array
    if H is None: H = cycle([None]) # IDWT can handle None input values - equals to zero-array
    for rowL, rowH in izip(L, H):
        append_data(idwt(rowL, rowH, wavelet, mode, 1))

    return array(data, default_dtype)


def _downcoef(data, wavelet, mode, type):
   """Adapts pywt.downcoef call for apply_along_axis"""
   return downcoef(type, data, wavelet, mode, level=1)

def dwtn(data, wavelet, mode='sym'):
    """
    Single-level n-dimensional Discrete Wavelet Transform.

    data     - n-dimensional array
    wavelet - wavelet to use (Wavelet object or name string)
    mode    - signal extension mode, see MODES

    Results are arranged in a dictionary, where key specifies
    the transform type on each dimension and value is a n-dimensional
    coefficients array.
    
    For example, for a 2D case the result will look something like this:
        {
            'aa': <coeffs>  # A(LL) - approx. on 1st dim, approx. on 2nd dim
            'ad': <coeffs>  # H(LH) - approx. on 1st dim, det. on 2nd dim
            'da': <coeffs>  # V(HL) - det. on 1st dim, approx. on 2nd dim
            'dd': <coeffs>  # D(HH) - det. on 1st dim, det. on 2nd dim
        }
    """
    import warnings
    warnings.warn("Name of this function and result format may change in the future.",
                  UserWarning)

    data = as_float_array(data)
    dim = len(data.shape)
    coeffs = [('', data)]
    for axis in range(dim):
        new_coeffs = []
        for subband, x in coeffs:
            new_coeffs.extend([
                (subband+'a', apply_along_axis(_downcoef, axis,
                                               x, wavelet, mode, 'a')),
                (subband+'d', apply_along_axis(_downcoef, axis,
                                               x, wavelet, mode, 'd'))
            ])
        coeffs = new_coeffs
    return dict(coeffs)


def swt2(data, wavelet, level, start_level=0):
    """
    2D Stationary Wavelet Transform.

    data    - 2D array with input data
    wavelet - wavelet to use (Wavelet object or name string)
    level   - how many decomposition steps to perform
    start_level - the level at which the decomposition will start

    Returns list of approximation and details coefficients:

        [
            (cA_n,
                (cH_n, cV_n, cD_n)
            ),
            (cA_n+1,
                (cH_n+1, cV_n+1, cD_n+1)
            ),
            ...,
            (cA_n+level,
                (cH_n+level, cV_n+level, cD_n+level)
            )
        ]

    where cA is approximation, cH is horizontal details, cV is
    vertical details, cD is diagonal details and n is start_level.
    """

    data = as_float_array(data)
    if len(data.shape) != 2:
        raise ValueError("Expected 2D data array")

    if not isinstance(wavelet, Wavelet):
        wavelet = Wavelet(wavelet)

    ret = []
    for i in range(start_level, start_level+level):
        # filter rows
        H, L = [], []
        append_L = L.append; append_H = H.append
        for row in data:
            cA, cD = swt(row, wavelet, level=1, start_level=i)[0]
            append_L(cA)
            append_H(cD)
        del data

        # filter columns
        H = transpose(H)
        L = transpose(L)

        LL, LH = [], []
        append_LL = LL.append; append_LH = LH.append
        for row in L:
            cA, cD = swt(array(row, default_dtype), wavelet, level=1, start_level=i)[0]
            append_LL(cA)
            append_LH(cD)
        del L

        HL, HH = [], []
        append_HL = HL.append; append_HH = HH.append
        for row in H:
            cA, cD = swt(array(row, default_dtype), wavelet, level=1, start_level=i)[0]
            append_HL(cA)
            append_HH(cD)
        del H

        # build result structure
        #     (approx.,        (horizontal,    vertical,       diagonal))
        approx = transpose(LL)
        ret.append((approx, (transpose(LH), transpose(HL), transpose(HH))))

        data = approx # for next iteration

    return ret
