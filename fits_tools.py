import numpy as np
try:
    import pyfits as pf
    has_pf = True
except ImportError:
    try:
        import astropy.io.fits as pf
        has_pf = True
    except ImportError:
        has_pf = False
        print 'Operating under the assumption that neither astropy',
        print ' nor pyfits are installed'
import goodman_functions as gdmn
import scipy.ndimage.filters as filters

def observation_type(filename):
    splitname = filename.split('.')
    foo = splitname.pop(0)
    foo = splitname.pop(-1)
    splitname = ''.join(splitname).lower()
    if 'focus' in splitname:
        type = 'focus'
        return type
    if 'fear' in splitname:
        type = 'fear'
        return type
    if 'qtz' in splitname:
        type = 'qtz'
        return type
    if 'img' in splitname:
        type = 'img'
        return type
    if 'slit' in splitname:
        type = 'img'
        return type
    else:
        type = 'obj'
        return type


def guess_dxvals(filename):
    if has_pf:
        with pf.open(filename,mode='readonly') as hdulist:
            grating = hdulist[0].header['GRATING']
            cam_ang = hdulist[0].header['CAM_ANG']
            grt_ang = hdulist[0].header['GRT_ANG']
    else:
        grating = get_value_pyraf(filename,'GRATING')
        cam_ang = get_value_pyraf(filename,'CAM_ANG')
        grt_ang = get_value_pyraf(filename,'GRT_ANG')
    grating_dict = {'600':0.65,'400':1.0,'300':1.33,'1200':0.333}
    dx = 1.0
    grate_val = 400
    for grting in grating_dict:
        if grting in grating:
            dx = grating_dict[grting]
            grate_val = float(grting)
            
    x1,xcent,x2 = gdmn.approximate_lambda(grate_val,grt_ang,cam_ang)
    x1 *= 10. #nm to Angstroms
    x2 *= 10. #nm to Angstroms
    return x1,x2,dx

def guess_crval_crdelt(filename,binning=1.):
    grating = get_value(filename,'GRATING')
    cam_ang = get_value(filename,'CAM_ANG')
    grt_ang = get_value(filename,'GRT_ANG')
    grating_dict = {'600':0.65,'400':1.0,'300':1.33,'1200':0.333}
    dx = 1.0
    grate_val = 400
    for grting in grating_dict:
        if grting in grating:
            dx = grating_dict[grting]
            grate_val = float(grting)
    cpix = 2048. / binning
    crval = gdmn.pix_to_lambda(cpix,grate_val,grt_ang,cam_ang,binning=binning)
    crval *= 10. #Angstroms from nm
    return crval,dx

def get_binning(filename,bindefault=1):
    '''Get the binning size from the header of filename'''
    comm = get_comment(filename,'PARAM18')
    if comm == '1 / Serial Binning,Pixels':
        binsize = get_value(filename,'PARAM18')
    else:
        prm_com = '1 / Serial Binning,Pixels'
        param_name = find_param_with_comment(filename,prm_com)
        if param_name == 'NullReturn':
            binsize=bindefault
        else:
            binsize = get_value(filename,param_name)
    return int(binsize)


def guess_mode(filelist,g_ang_tol = 0.2,c_ang_tol=0.2):
    '''Runs through all of the files. Tries to guess if they were
    obtained in different modes'''
    first = True
    for filename in filelist:
        shortname = filename.split('.')[0]
        if has_pf:
            with pf.open(filename,mode='readonly') as hdulist:
                grating = hdulist[0].header['GRATING']
                cam_ang = hdulist[0].header['CAM_ANG']
                grt_ang = hdulist[0].header['GRT_ANG']
        else:
            grating = get_value_pyraf(filename,'GRATING')
            cam_ang = get_value_pyraf(filename,'CAM_ANG')
            grt_ang = get_value_pyraf(filename,'GRT_ANG')
        if first:
            modes = {0:[grating,cam_ang,grt_ang]}
            file_modes = {shortname:0}
            nmodes = 1
            first = False
        else:
            matched = False
            for mode_choice in range(nmodes):
                del_grat = np.abs(grt_ang - modes[mode_choice][2])
                del_cam = np.abs(cam_ang - modes[mode_choice][1])
                if (del_grat < g_ang_tol and del_cam < c_ang_tol
                    and grating == modes[mode_choice][0]):
                    file_modes[shortname] = mode_choice
                    matched = True
                    break
            if not matched:
                modes[0+nmodes] = [grating, cam_ang, grt_ang]
                file_modes[shortname] = nmodes + 0
                nmodes +=1
    return file_modes, nmodes
                                             
def fits_head_observation_type(filename):
    if has_pf:
        with pf.open(filename,mode='readonly') as hdulist:
            slit = hdulist[0].header['SLIT']
            grating = hdulist[0].header['GRATING']
            obstype = hdulist[0].header['OBSTYPE']
    else:
        slit = get_value_pyraf(filename,'SLIT')
        grating = get_value_pyraf(filename,'GRATING')
        obstype = get_value_pyraf(filename,'OBSTYPE')
    if obstype == 'FLAT':
        return 'qtz'
    elif obstype == 'COMP':
        if slit == '0.46" long slit':
            return 'focus'
        else:
            return 'fear'
    elif grating != '<NO GRATING>':
        return 'obj'
    else:
        #There is no header distinction between SLIT and IMG
        return 'img'


def find_param_with_comment(filename,comment):
    if has_pf:
        return find_param_with_comment_pyfits(filename,comment)
    else:
        return find_param_with_comment_pyraf(filename,comment)


def find_param_with_comment_pyfits(filename,comment):
    with pf.open(filename,mode='readonly') as hdulist:
        hdr = hdulist[0].header
        for ii in range(len(hdr.comments)):
            if hdr.comments[ii] == comment:
                return hdr.cards[ii][0]
            else:
                pass
        return 'NullReturn'
    
def find_param_with_comment_pyraf(filename,comment):
    '''Using Pyraf methods, return the param name that has a specified comment.
    If no match, the string 'NullReturn' is returned'''
    header_long = iraf.imheader(filename,lo=True,Stdout=True)
    for header_val in header_long:
        trimmed = header_val.replace(' = ',
                                     '!^!^!').replace(' / ',
                                                      '!^!^!').split('!^!^!')
        if len(trimmed) < 3:
            continue
        elif trimmed[2] == comment:
            return trimmed[0]
        else:
            pass
    return 'NullReturn'


def get_comment(filename,paramname):
    if has_pf:
        return get_comment_pyfits(filename,paramname)
    else:
        return get_comment_pyraf(filename,paramname)


def get_comment_pyfits(filename,paramname):
    with pf.open(filename,mode='readonly') as hdulist:
        try:
            out = hdulist[0].header.comments[paramname]
        except KeyError:
            out = 'NullReturn'
    return out

def get_comment_pyraf(filename,paramname):
    '''Using Pyraf methods, return the comment for a paramname.
    If parameter is not in header, returns string 'NullReturn'.'''
    header_long = iraf.imheader(filename,lo=True,Stdout=True)
    for header_val in header_long:
        trimmed = header_val.replace(' = ',
                                     '!^!^!').replace(' / ',
                                                      '!^!^!').split('!^!^!')
        if len(trimmed) < 3:
            continue
        elif trimmed[1].strip() == paramname:
            return trimmed[2].strip()
        else:
            pass
    return 'NullReturn'

def get_value_pyraf(filename,paramname):
    '''Using Pyraf methods, return the value for a paramname.
    If parameter is not in header, returns string 'NullReturn'.'''
    return iraf.hselect(filename,paramname,'yes')

def get_value_pyfits(filename,paramname):
    with pf.open(filename,mode='readonly') as hdulist:
        return hdulist[0].header[paramname]

def get_value(filename,paramname):
    if has_pf:
        return get_value_pyfits(filename,paramname)
    else:
        return get_value_pyraf(filename,paramname)
    
def get_theta(wnartifact,quartzlist):
    exptimes,gains = [],[]
    for filename in quartzlist:
        exptime = get_value(filename,'EXPTIME')
        gain = get_value(filename,'GAIN')
        gains.append(gain)
        exptimes.append(exptime)
    if has_pf:
        with pf.open(wnartifact,mode='readonly') as hdulist:
                exptime = hdulist[0].header['EXPTIME']
    else:
        exptime = get_value_pyraf(wnartifact,'EXPTIME')
    thetas = [exp / exptime / gn for exp,gn in zip(exptimes,gains)]
    if len(set(thetas)) == 1:
        #All have the same Theta, only have to make one wn image
        return True, thetas
    else:
        #Different settings, so different wn images
        return False, thetas

def fix_quartz_banding(qtzfile,gsize_1 = 3, gsize_2 = 120):
    '''Remove banding pattern from quartz lamps. Experimental.

    On quartz lamp images, at least those taken with the blue camera
    a 'waves of grain' like patter appears. This is not present in science
    data. To correct for this, the medium-sized physical structure is divided
    out of the quartz image. This is done by dividing a gaussian smoothed
    version of the image out and multiplying in a gaussian smoothed image; the
    kernel size of the first is gsize_1, and should be much smaller than gsize_2,
    the kernel size of the second. Saves the result to w+qtzfile.'''
    if qtzfile[-5:] != '.fits':
        qtzfile += '.fits'
    print 'Applying the banding correction to {}'.format(qtzfile)
    data = pf.open(qtzfile)[0].data
    smallscale = filters.gaussian_filter(data,gsize_1)
    largescale = filters.gaussian_filter(data,gsize_2)
    #outdata = (data / smallscale) * largescale
    outdata = largescale
    pf.writeto('w'+qtzfile,outdata,clobber=True)
    return

def get_threshold(arc,sigclip=1):
    '''Computes a threshold parameter for {auto/re/}identify'''
    if has_pf:
        data = pf.open(arc)[0].data
        mn = np.median(data[:,500:600])
        sg = np.std(data[:,500:600])
    else:
        stats = iraf.imstat(arc+'[*,500:600]',Stdout=1).split()[2]
        mn = float(stats[2])
        sg = float(stats[3])
    return sigclip * sg

        
