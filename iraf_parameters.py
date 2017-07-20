def set_ccdproc(ccdproc):
    #noao>imred>ccdred>ccdproc
    ccdproc.ccdtype = ""
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
    ccdproc.ccdtype = None
    return

def set_apflatten(apflatten):
    apflatten.input = None #'List of images to flatten'
    apflatten.output = None #'List of output flatten images'
    apflatten.apertures = "" #'Apertures'
    apflatten.references = "" #'List of reference images'
    apflatten.interactive = "Yes" #'Run task interactively?'
    apflatten.find = "No" #'Find apertures?'
    apflatten.recenter = "No" #'Recenter apertures?'
    apflatten.resize = "No" #'Resize apertures?'
    apflatten.edit = "Yes" #'Edit apertures?'
    apflatten.trace = "No" #'Trace apertures?'
    apflatten.fittrace = "No" #'Fit traced points interactively?'
    apflatten.flatten = "Yes" #'Flatten spectra?'
    apflatten.fitspec = "Yes" #'Fit normalization spectra interactively?'
    apflatten.line = "INDEF" #'Dispersion line'
    apflatten.nsum = 10 #'Number of dispersion lines to sum or median'
    apflatten.threshold = 10.0 #'Threshold for flattening spectra'
    apflatten.pfit = "fit1d" #'|fit1d|fit2d|',,'Profile fitting type (fit1d|fit2d)'
    apflatten.clean = "No" #'Detect and replace bad pixels?'
    apflatten.saturation = "INDEF" #'Saturation level'
    apflatten.readnoise = 0 #'Read out noise sigma (photons)'
    apflatten.gain = 1 #'Photon gain (photons/data number)'
    apflatten.lsigma = 4.0 #'Lower rejection threshold'
    apflatten.usigma = 4.0 #'Upper rejection threshold'
    apflatten.function = "legendre" #'|chebyshev|legendre|spline1|spline3|',,'Fitting function for normalization spectra'
    apflatten.order = 5 #'Fitting function order'
    apflatten.sample = 4142 #'Sample regions'
    apflatten.naverage = -5 #'Average or median' Positive values are for averages and negative points for medians. 
    apflatten.niterate = 5 #'Number of rejection iterations'
    apflatten.low_reject = 3 #'Lower rejection sigma'
    apflatten.high_reject = 1 #'High upper rejection sigma'
    apflatten.grow = 0 #'Rejection growing radius'
    apflatten.mode = "" #'al'
    return

def set_response(response):
    #noao>twodspec>longslit>response
    response.interac = 'Yes'
    response.naverag = 1
    response.function = 'spline3'
    response.order = 15
    response.low_rej = 0
    response.high_re = 0
    response.niterat = 1
    response.grow = 0
    return

def set_identify_calibration(identify):
    #noao>twodspec>longslit>identify
    identify.section = 'middle line'
    identify.databas = 'database'
    identify.coordli = 'linelist'
    identify.nsum = 10
    identify.match = 50
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
    #noao>twodspec>longslit>reidentify
    reidentify.interac = 'no'
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
    reidentify.thresho = 0
    reidentify.addfeat = 'No'
    reidentify.coordli = 'linelist'
    reidentify.match = 50
    reidentify.maxfeat = 50
    reidentify.minsep = 2
    reidentify.databas = 'database'
    return

def set_fitcoords_calibration(fitcoords):
    #noao>twodspec>longslit>fitcoords
    fitcoords.interac = 'Yes'
    fitcoords.combine = 'Yes'
    fitcoords.databas = 'database'
    fitcoords.functio = 'chebyshev'
    fitcoords.xorder = 3
    fitcoords.yorder = 3
    return

def set_identify_standard(identify):
    #noao>twodspec>longslit>identify
    identify.section = 'middle column'
    identify.databas = 'database'
    identify.coordli = ''
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

def set_reidentify_standard(reidentify):
    #noao>twodspec>longslit>reidentify
    reidentify.interac = 'no'
    reidentify.section = 'middle column'
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
    reidentify.coordli = ''
    reidentify.match = 10
    reidentify.maxfeat = 50
    reidentify.minsep = 2
    reidentify.databas = 'database'
    return

def set_fitcoords_standard(fitcoords):
    #noao>twodspec>longslit>fitcoords
    fitcoords.interac = 'Yes'
    fitcoords.combine = 'Yes'
    fitcoords.databas = 'database'
    fitcoords.functio = 'chebyshev'
    fitcoords.xorder = 3
    fitcoords.yorder = 3
    return

def set_transform(transform):
    #noao>twodspec>longslit>transform
    transform.database = 'database'
    transform.interpt = 'spline3'
    transform.xlog = 'No'
    transform.flux = 'Yes'
    return

def set_apall_std(apall):
    #noao>imred>specred>apall
    apall.format = 'multispec'
    apall.interac = 'Yes'
    apall.find = 'Yes'
    apall.recente = 'Yes'
    apall.resize = 'Yes'
    apall.edit = 'Yes'
    apall.trace = 'Yes'
    apall.fittrac = 'Yes'
    apall.extract = 'Yes'
    apall.extras = 'Yes'
    apall.review = 'Yes'
    apall.nsum = 10
    apall.lower = -70
    apall.upper = 70
    apall.b_funct = 'chebyshev'
    apall.b_order = 1
    apall.b_sampl = '-150:-100,100:150'
    apall.b_naver = -100
    apall.b_niter = 0
    apall.b_low_r = 3
    apall.b_high_ = 3
    apall.b_grow = 0
    apall.width = 5
    apall.radius = 10
    apall.thresho = 0
    apall.nfind = 0
    apall.minsep = 5
    apall.maxsep = 1000
    apall.order = 'increasing'
    apall.shift = 'Yes'
    apall.ylevel = 0.1
    apall.peak = 'Yes'
    apall.bkg = 'Yes'
    apall.r_grow = 0
    apall.avglimi = 'No'
    apall.t_nsum = 10
    apall.t_step = 10
    apall.t_nlost = 3
    apall.t_funct = 'legendre'
    apall.t_order = 2
    apall.t_naver = 1
    apall.t_niter = 0
    apall.t_low_r = 3
    apall.t_high_ = 3
    apall.t_grow = 0
    apall.backgro = 'none'
    apall.skybox = 1
    apall.weights = 'none'
    apall.pfit = 'fit1d'
    apall.clean = 'No'
    apall.readnoi = 0
    apall.gain = 1
    apall.lsigma = 4
    apall.usigma = 4
    apall.nsubaps= 1
    return

def set_standard(standard):
    #noao>imred>specred>standard
    standard.samesta = 'Yes'
    standard.beam_sw = 'No'
    standard.extinct = 'onedstds$ctioextinct.dat'
    standard.caldir = 'onedstds$ctionewcal/'
    standard.airmass = ''
    standard.exptime = ''
    standard.mag = ''
    standard.magband = None
    standard.teff = ''
    return

def set_sensfunc(sensfunc):
    #noao>imred>specred>sensfunc
    sensfunc.ignorea = 'Yes'
    sensfunc.extinct = 'onedstds$ctioextinct.dat'
    sensfunc.newexti = 'extinct.dat'
    sensfunc.function = 'spline3'
    sensfunc.order = 6
    sensfunc.interac = 'Yes'
    return

def set_calibrate(calibrate):
    #noao>imred>specred>calibrate
    calibrate.extinct = 'Yes'
    calibrate.flux = 'Yes'
    calibrate.extinction = 'onedstds$ctioextinct.dat'
    calibrate.airmass = None
    calibrate.exptime = None
    return

def set_background(background):
    #noao>imred>specred>background
    background.axis = 2
    background.interac = 'Yes'
    background.naverag = 1
    background.functio = 'chebyshev'
    background.order = 1
    background.low_rej = 0
    background.high_re = 0
    background.niterat = 3
    background.grow = 0
    return

