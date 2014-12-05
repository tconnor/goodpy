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

def set_identify_calibration(identify):
    identify.section = 'middle line'
    identify.databas = 'database'
    identify.coordli = 'linelist'
    identify.nsum = 5
    identify.match = 10
    identify.maxfeat = 50
    identify.zwidth = 100
    identify.ftype = 'emission'
    identify.fwidth = 15
    identify.cradius = 5
    identify.thresho = 10
    identify.minsep = 2
    identify.function = 'spline3'
    identify.order = 3
    identify.niterat = 0
    identify.low_rej = 3
    identify.high_re = 3
    identify.grow = 0
    return

def set_reidentify_calibration(reidentify):
    reidentify.interac = 'No'
    reidentify.section = 'middle line'
    reidentify.newaps = 'Yes'
    reidentify.overrid = 'Yes'
    reidentify.refit = 'Yes'
    reidentify.trace = 'Yes'
    reidentify.step = 50
    reidentify.nsum = 5
    reidentify.shift = 0
    reidentify.search = 0
    reidentify.nlost = 10
    reidentify.cradius = 5
    reidentify.thresho = 10
    reidentify.addfeat = 'No'
    reidentify.coordli = 'linelist'
    reidentify.match = 10
    reidentify.maxfeat = 50
    reidentify.minsep = 2
    reidentify.databas = 'database'
    return

def set_fitcoords_calibration(fitcoords):
    fitcoords.interac = 'Yes'
    fitcoords.combine = 'Yes'
    fitcoords.databas = 'database'
    fitcoords.functio = 'chebyshev'
    fitcoords.xorder = 3
    fitcoords.yorder = 3
    return

def set_calibrate(calibrate):
    #noao>imred>specred>calibrate
    calibrate.extinct = 'Yes'
    calibrate.flux = 'Yes'
    calibrate.extinction = 'ondstsds$ctioextinct.dat'
    return
