def set_ccdproc(ccdproc):
    ccdproc.noproc = 'No'
    ccdproc.fixpix = 'No'
    ccdproc.overscan = 'Yes'
    ccdproc.trim = 'Yes'
    ccdproc.zerocor = 'No'
    ccdproc.darkcor = 'No'
    ccdproc.flatcor = 'No'
    ccdproc.illumco = 'No'
    ccdproc.fringec = 'No'
    ccdproc.readcor = 'No'
    ccdproc.scancor = 'No'
    ccdproc.readaxi = 'line'
    ccdproc.interac = 'No'
    ccdproc.function = 'legendre'
    ccdproc.order = 1
    ccdproc.naverage = 1
    ccdproc.niterate = 1
    ccdproc.low_rej = 3
    ccdproc.high_re = 3
    ccdproc.grow = 0
    return

def set_response(response):
    response.interac = 'Yes'
    response.naverag = 1
    response.function = 'spline3'
    response.order = 6
    response.low_rej = 0
    response.high_re = 0
    response.niterat = 1
    response.grow = 0
    return
