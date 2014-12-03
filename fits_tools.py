import pyfits as pf

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
        type = 'slit'
        return type
    else:
        type = 'obj'
        return type

def fix_header(inhead):
    '''Corrects SOAR headers that include '?' ('\xb0') in Header'''
    contin = True
    ii = 0
    while contin:
        try:
            inhead.comments[ii] = inhead.comments[ii].replace('\xb0','')
            ii +=1
        except IndexError:
            contin = False
    return inhead

def cut_dimension(fitsfile,fix_header=True):
    '''Reduces a FITS file data from N dimensions to N-1
    arguments-
    fix_header -- Apply header correction to fix '?'s in header comments (default = True) '''
    hdulist = pf.open(fitsfile,mode='update')
    if fix_header: hdulist[0].header = fix_header(hdulist[0].header)
    hdulist[0].data = hdulist[0].data[0]
    hdulist.flush()
    hdulist.close()
    return
