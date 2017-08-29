import numpy as np

def approximate_lambda(grating,g_ang,c_ang,soffset=0.0):
    '''Takes a grating, grating angle, and camera angle, and returns the
    limits and center of the image in nm.
    Inputs: soffset: slit offset from CF (Default=0.0)'''
    alpha = g_ang + soffset
    beta = c_ang - g_ang
    c_lam = ((1000000. / grating) * (np.sin(np.radians(alpha))
                                     + np.sin(np.radians(beta))))
    b_lam = ((1000000. / grating) * (np.sin(np.radians(alpha))
                                     + np.sin(np.radians(beta-4.656))))
    r_lam = ((1000000. / grating) * (np.sin(np.radians(alpha))
                                     + np.sin(np.radians(beta+4.656))))
    return b_lam,c_lam,r_lam

def pix_to_lambda(pix,grating,g_ang,c_ang,soffset=0.0,binning=1.):
    '''Takes a grating, grating angle, and camera angle, and returns the
    wavelength of a pixel in nm.
   Inputs: soffset1: slit offset from CF (Default=0.0)
   Binning: The binning of the spectrum. (Default = 1.)'''
    alpha = g_ang + soffset
    beta = c_ang - g_ang
    lam = ((1000000. / grating)
           * (np.sin(np.radians(alpha))
              + np.sin(np.radians(beta)
                       + np.arctan((pix * binning - 2048.)
                                   * (0.015 / 377.2)))))
    return lam

def lambda_to_pix(lmbda,grating,g_ang,c_ang,soffset=0.0,binning=1.):
    '''Takes a grating, grating angle, and camera angle, and returns the
    wavelength of a pixel in nm.
    Inputs: soffset1: slit offset from CF (Default=0.0)
    Binning: The binning of the spectrum. (Default = 1.)'''
    alpha = g_ang + soffset
    beta = c_ang - g_ang
    term_a = lmbda * grating / 1000000. - np.sin(np.radians(alpha))
    term_b = np.arcsin(term_a) - np.radians(beta)
    term_c = np.tan(term_b) * 377.2 / 0.015
    pix = (term_c + 2048.) / binning
    return pix
