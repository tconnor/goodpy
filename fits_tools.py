try:
    import pyfits as pf
    has_pf = True
except ImportError:
    try:
        import astropy.io.fits as pf
        has_pf = True
    except ImportError:
        has_pf = False
        print ' Operating under the assumption that neither astropy nor pyfits are installed'
import goodman_functions as gdmn

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

def guess_mode(filelist,g_ang_tol = 0.2,c_ang_tol=0.2):
    '''Runs through all of the files. Tries to guess if they were
    obtained in different modes'''
    first = True
    for filename in filelist:
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
            file_modes = {filename:0}
            nmodes = 1
            first = False
        else:
            matched = False
            for mode_choice in range(nmodes):
                del_grat = np.abs(grt_ang - modes[mode_choice][2])
                del_cam = np.abs(cam_ang - modes[mode_choice][1])
                if (del_grat < g_ang_tol and del_cam < c_ang_tol
                    and grating == modes[mode_choice][0]):
                    file_modes[filename] = mode_choice
                    matched = True
                    break
            if not matched:
                modes[0+nmodes] = [grating, cam_ang, grt_ang]
                file_modes[filename] = nmodes + 0
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
        trimmed = header_val.replace(' = ','!^!^!').replace(' / ','!^!^!').split('!^!^!')
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
        trimmed = header_val.replace(' = ','!^!^!').replace(' / ','!^!^!').split('!^!^!')
        if len(trimmed) < 3:
            continue
        elif trimmed[1].strip() == paramname:
            return trimmed[2].strip()
        else:
            pass
    return 'NullReturn'

def get_value_pyraf(filename,paramname):
    '''Using Pyraf methods, return the comment for a paramname.
    If parameter is not in header, returns string 'NullReturn'.'''
    header_long = iraf.imheader(filename,lo=True,Stdout=True)
    for header_val in header_long:
        trimmed = header_val.replace(' = ','!^!^!').replace(' / ','!^!^!').split('!^!^!')
        if len(trimmed) < 3:
            continue
        elif trimmed[1].strip() == paramname:
            return trimmed[1].strip()
        else:
            pass
    return 'NullReturn'

