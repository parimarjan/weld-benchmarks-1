# -*- coding: utf-8 -*-
# from benchpress import util
import numpy as np
# import statsnumpy as np
from weldnumpy import weldarray
import time
import argparse

def compare(R, R2):
    
    if isinstance(R2, weldarray):
        R2 = R2.evaluate()

    mistakes = 0
    R = R.flatten()
    R2 = R2.view(np.ndarray).flatten()
    
    assert R.dtype == R2.dtype, 'dtypes must match!'
    
    displayed = 0
    # this loop takes ages to run so just avoiding it.
    for i, r in enumerate(R):
        # if not np.isclose(R[i], R2[i]):
        if R[i] != R2[i]:
            mistakes += 1
            if displayed <= 10:
                print('R[i] : ', R[i])
                print('R2[i]: ', R2[i]) 
                displayed += 1
    if mistakes != 0:
        print('mistakes % = ', mistakes / float(len(R)))
    else:
        print('mistakes = 0')

    assert np.allclose(R, R2)

def run(args, use_weld):
    k = np.float64(args.k)
    stripes = np.float64(args.stripes)
    N = args.n
    phases  = np.arange(0, 2*np.pi, 2*np.pi/args.times)
    image   = np.empty((N, N), dtype=np.float64)
    d       = np.arange(-N/2, N/2, dtype=np.float64)
    if use_weld:
        phases = weldarray(phases)
        image = weldarray(image)
        
    xv, yv = np.meshgrid(d, d)
    if use_weld:
        xv = weldarray(xv)
        yv = weldarray(yv)
    
    start = time.time()
    # TODO: FIXME!!!
    theta  = np.arctan2(yv, xv)

    a = xv**2 + yv**2
    # just to remove 0's from a, and stop numpy from complaining.
    # TODO: Maybe remove this since it was not there in original.
    a += 1.0
    r      = np.log(np.sqrt(a))
    if isinstance(r, weldarray):
        r = r.evaluate()
    
    # TODO: could try to intercept the arange call as well?
    tmp = np.arange(0, np.pi, np.pi/k)
    if isinstance(r, weldarray):
        tmp = weldarray(tmp)
    
    r.view(np.ndarray)[np.isinf(r) == True] = 0

    tcos   = theta * np.cos(tmp)[:, np.newaxis, np.newaxis]
    rsin   = r * np.sin(tmp)[:, np.newaxis, np.newaxis]
    inner  = (tcos - rsin) * stripes
    
    if isinstance(inner, weldarray):
        inner = inner.evaluate()
    
    cinner = np.cos(inner)
    sinner = np.sin(inner)
    
    for i, phase in enumerate(phases):
        print(i)
        tmp2 = cinner * np.cos(phase) - sinner * np.sin(phase)
        if isinstance(tmp2, weldarray):
            tmp2 = tmp2.evaluate()
        image.view(np.ndarray)[:] = np.sum(tmp2.view(np.ndarray), axis=0) + k

        if isinstance(image, weldarray):
            print('evaluating image')
            image = image.evaluate()
    
    end = time.time()
    print('total time = ', end-start)
    return image

def main():
    parser = argparse.ArgumentParser(
        description="give num_els of arrays used for nbody"
    )
    parser.add_argument('-k', "--k", type=float, required=True,
                        help="number of plane waves")
    parser.add_argument('-s', "--stripes", type=float, required=True,
                        help="number of stripes per wave")
    parser.add_argument('-n', "--n", type=int, required=True,
                        help="image size in pixels")
    parser.add_argument('-t', "--times", type=int, required=True,
                        help="number of iterations")
    args = parser.parse_args()

    img1 = run(args, False)
    img2 = run(args, True)
    img2 = img2.evaluate()
    
    assert img1.shape == img2.shape
    assert img1.strides == img2.strides
    compare(img1, img2)
    
    assert np.allclose(img1, img2)

if __name__ == "__main__":
    main()
