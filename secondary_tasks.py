from pyraf import iraf

def find_param_with_comment(filename,comment):
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
