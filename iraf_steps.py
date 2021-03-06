from pyraf import iraf
import iraf_parameters as irf_prm
import fits_tools as ftl
if ftl.has_pf:
    import background_select as bkg
import GUI_functions as gui

def gui_alert():
    print 'An IRAF GUI has been opened and requires your input'
    
def initialize_iraf():
    iraf.noao(_doprint=0)
    iraf.imred(_doprint=0)
    iraf.ccdred(_doprint=0)
    iraf.specred(_doprint=0)
    iraf.twodspec(_doprint=0)
    iraf.apextract(_doprint=0)
    iraf.longslit(_doprint=0)
    return

def reduce_dimensions(filename):
    iraf.imcopy(filename+'[*,*,1]',filename)
    #iraf.hedit(ccdsec) #What is this supposed to do?
    iraf.hedit(filename,'EPOCH',2000,add=True,verify='No')
    iraf.wcsreset(image=filename,wcs='world')
    return

def bias_correct(file_list,xmin='18',xmax='4111',ymin='350',
                 ymax='1570',bindefault=1):
    irf_prm.set_ccdproc(iraf.ccdproc)
    biassecs = {'BLUE':{1:'[4114:4142,1:1896]',2:'[4114:4142,1:1896]',
                        3:'[4114:4142,1:1896]',4:'[4114:4142,1:1896]'},
                        'RED':{1:'[6:50,1:1896]',2:'[6:50,1:1896]',
                               3:'[6:50,1:1896]',4:'[6:50,1:1896]'}}
         #NEED UPDATED
    #iraf.ccdproc.biassec = biassecs[binsize]
    iraf.ccdproc.trimsec = '['+xmin+':'+xmax+','+ymin+':'+ymax+']'
    for ff in file_list:
        instmode = ftl.get_instrument_mode(ff)
        print 'DEBUG: I believe {} used the {} CCD'.format(ff,instmode)
        if instmode == 'RED':
            iraf.ccdproc.trimsec = '[51:4141,447:1686]'
        else:
            iraf.ccdproc.trimsec = '['+xmin+':'+xmax+','+ymin+':'+ymax+']'
        binsize = ftl.get_binning(ff,bindefault=bindefault)
        iraf.ccdproc.biassec = biassecs[instmode][binsize]
        output = 'b'+ff
        iraf.ccdproc(images=ff,output=output,ccdtype = "")
    return

def artifact_imcombine(inlist,outname):
    imcinpt = ''
    for obj in inlist:
        imcinpt += obj +','
    imcinpt = imcinpt[:-1] #Drop trailing comma
    iraf.imcombine(input=imcinpt,output=outname,sigmas=outname+'_sig',
                   combine='median')
    return

def normalize_artifact(artifact,nartifact):
    print 'When you are prompt to edit aperture, you will be facing a '
    print 'columns cut (usually) in the middle of the image without any'
    print 'aperture. Include a new aperture in the center of the image'
    print 'with "n" and resize the aperture to fit the entire range '
    print '(I use "l" for lower and "u" for upper, in the borders),'
    print 'Hit "q" and the fitting window will appear in place of '
    print 'the aperture selection.'
    irf_prm.set_apflatten(iraf.apflatten)
    iraf.apflatten(input=artifact,output=nartifact)
    
def artifact_create(artifact,theta,output):
    iraf.imarith(operand1=artifact,operand2=theta,op='*',
                 result='tmpartifact.fits')
    iraf.imarith(operand1='tmpartifact.fits',operand2=1-theta,op='+',
                 result=output)
    iraf.imdelete(images='tmpartifact.fits',go_ahead='yes',verify='no')
    return

def correct_artifact(wnartifact,qtz):
    iraf.imarith(operand1=qtz,operand2=wnartifact,op='/',result='a'+qtz)
    return

def normalize_quartzes(quartz_list,dont_norm_list,fix_banding,run_interactive):
    '''Normalize files in quartz_list using noao>twodspec>longslit>response'''
    irf_prm.set_response(iraf.response)
    if run_interactive: inter = 'Yes'
    else: inter = 'No'
    for quartz in quartz_list:
        if quartz in dont_norm_list:
            continue
        iraf.response(calibrat=quartz,normaliz=quartz,response='n'+quartz,
                      interactive=inter)
        if fix_banding:
            ftl.fix_quartz_banding('n'+quartz)
        dont_norm_list.append(quartz)
    return

def quartz_divide(science_list,object_match):
    '''Divide science frames by user-selected quartz frames'''
    for obj in science_list:
        if len(object_match[obj]) > 1:
            qtzinpt = ''
            for qtz in object_match[obj]:
                qtzinpt += qtz +','
            iraf.imcombine(input=qtzinpt,output='tempquartz')
            iraf.imarith(operand1=obj,operand2='tempquartz',op='/',
                         result='f'+obj)
            heditstr = 'Flat field images are '+qtzinpt[:-1]
            iraf.imdelete(images='tempquartz',go_ahead='yes',verify='no')
            if len(heditstr) > 65:
                nfields = int(len(heditstr)/65)#Declare int for py3 compatibility
                for ii in range(nfields+1):
                    writestr = heditstr[(ii*65):(ii+1)*65]
                    iraf.hedit(images='f'+obj,fields='flatcor'+str(ii),
                               value=writestr,add='yes',verify='No')
            else:
                iraf.hedit(images='f'+obj,fields='flatcor',
                           value=heditstr,add='yes',verify='No')
        else:
            iraf.imarith(operand1=obj,operand2=object_match[obj][0],op='/',
                         result='f'+obj)
            heditstr = 'Flat field image is '+object_match[obj][0]
            if len(heditstr) > 65:
                nfields = int(len(heditstr)/65)#Declare int for py3 compatibility
                for ii in range(nfields+1):
                    writestr = heditstr[(ii*65):(ii+1)*65]
                    iraf.hedit(images='f'+obj,fields='flatcor'+str(ii),
                               value=writestr,add='yes',verify='No')
            else:
                iraf.hedit(images='f'+obj,fields='flatcor',
                           value=heditstr,add='yes',verify='No')
    return


def standard_trace(standard_list,supplement_list,outname='star'):
    irf_prm.set_identify_standard(iraf.identify)
    irf_prm.set_reidentify_standard(iraf.reidentify)
    irf_prm.set_fitcoords_standard(iraf.fitcoords)
    all_standards = ''
    for standrd in standard_list:
        iraf.identify(images=standrd)
        iraf.reidentify(reference=standrd,images=standrd)
        all_standards += standrd[:-5]+','
    for supplement in supplement_list:
        iraf.identify(images=supplement)
        iraf.reidentify(reference=supplement,images=supplement)
        all_standards += supplement[:-5]+','
    iraf.fitcoords(images=all_standards,fitname=outname)
    return

def make_lambda_solution(arc_list,fcnamedict,dont_ident_list):
    irf_prm.set_identify_calibration(iraf.identify)
    irf_prm.set_reidentify_calibration(iraf.reidentify)
    irf_prm.set_fitcoords_calibration(iraf.fitcoords)
    
    for arc in arc_list:
        if arc in dont_ident_list:
            continue
        iraf.identify(images=arc)
        iraf.reidentify(reference=arc,images=arc)
        iraf.fitcoords(images=arc[:-5],fitname=fcnamedict[arc])
        dont_ident_list.append(arc)
    return

def make_lambda_solution_auto(arc_list,fcnamedict,dont_ident_list,
                              is_datafile_good,binning=1.):
    irf_prm.set_aidpars_calibration(iraf.aidpars)
    irf_prm.set_autoidentify_calibration(iraf.autoidentify)
    irf_prm.set_identify_calibration(iraf.identify)
    irf_prm.set_reidentify_calibration(iraf.reidentify)
    irf_prm.set_fitcoords_calibration(iraf.fitcoords)
    
    for arc in arc_list:
        if arc in dont_ident_list:
            continue
        first_value_str = ftl.get_value(arc,'CCDSEC')
        first_value = int(first_value_str[1:].split(':')[0])
        binning = ftl.get_binning(arc,bindefault=binning)
        thresh = ftl.get_threshold(arc)
        thresh *= float(iraf.autoidentify.nsum)
        iraf.aidpars.crpix = int(2048. / binning) - first_value
        fit_crval, fit_cdelt = ftl.guess_crval_crdelt(arc,binning=binning)
        while True:
            print iraf.autoidentify.crval
            print iraf.autoidentify.cdelt
            iraf.autoidentify(images=arc,crval=fit_crval,
                              cdelt=fit_cdelt,threshold=thresh)
            print 'database/'+'id'+arc[:-5]
            if not is_datafile_good('database/'+'id'+arc[:-5]):
                try_again = gui.get_boolean('Tweak auto-ident params')
            else:
                try_again = False
            if try_again:
                print "Auto-Ident failed. Tweak the parameters"
                print "and see if you can make it work."
                print "crval = {0}".format(fit_crval)
                print "cdelt = {0}".format(fit_cdelt)
                print "crpix = {0}".format(iraf.aidpars.crpix)
                print "threshold = {0}".format(thresh)
                print "Decreasing threshold seems to work best."
                print "But also consider aidpars.fmatch"
                iraf.epar(iraf.autoidentify)
                thresh = iraf.autoidentify.threshold
                fit_crval = iraf.autoidentify.crval
                fit_cdelt = iraf.autoidentify.cdelt
            else:
                iraf.reidentify(reference=arc,images=arc,threshold=thresh)
                iraf.fitcoords(images=arc[:-5],fitname=fcnamedict[arc])
                dont_ident_list.append(arc)
                break
    return


def transform(science_list,object_match,arc_fc_dict,arc_coords,fcstar='star'):
    '''Transform filename to t+filename using noao>twodspec>longslit>transform'''
    irf_prm.set_transform(iraf.transform)
    for obj in science_list:
        fcarc = arc_fc_dict[object_match[obj]]
        dx_param = arc_coords[object_match[obj]]
        #These should be the same for each observing mode
        #Because then they're all mapped together for
        #Accurate flux calibration and imcombining
        iraf.transform.x1 = dx_param[0]
        iraf.transform.x2 = dx_param[1]
        iraf.transform.dx = dx_param[2]
        iraf.transform(input=obj,output='t'+obj,fitnames=fcstar+','+fcarc)
    return
    
def apall_std(stdlist):
    irf_prm.set_apall_std(iraf.apall)
    for std in stdlist:
        iraf.apall(input='k'+std,output = 'sk'+std,nfind=0,lower=-40,
                   upper=40)#,interactive='no')
    return

def standard(stdlist,std_name,stdidx):
    irf_prm.set_standard(iraf.standard)
    for std in stdlist:
        iraf.standard(input='sk'+std,output='std'+str(stdidx),star_name=std_name)
    return

def sensfunc(stdidx):
    iraf.sensfunc(standards='std'+str(stdidx),sensitivity='sens'+str(stdidx))
    return

def background(objlist,unique=True):
    irf_prm.set_background(iraf.background)
    if ftl.has_pf and unique:
        print 'Please select regions to mask from background determination'
        for bkgobj in objlist:
            mask_regions = bkg.get_mask_regions(bkgobj)
            msk_lo,msk_hi,y_max = mask_regions
            sample = '0:'
            for ii in range(len(msk_lo)):
                sample += '{0:d},{1:d}:'.format(msk_lo[ii],min(y_max,msk_hi[ii]))
            sample += '{0:d}'.format(y_max)
            iraf.background(input=bkgobj,output='k'+bkgobj,interactive='No',
                            sample=sample)
    elif ftl.has_pf:
        print 'Please select regions to mask from background determination'
        mask_regions = bkg.get_mask_regions(objlist[0])
        msk_lo,msk_hi,y_max = mask_regions
        sample = '0:'
        for ii in range(len(msk_lo)):
            sample += '{0:d},{1:d}:'.format(msk_lo[ii],min(y_max,msk_hi[ii]))
        sample += '{0:d}'.format(y_max)
        for bkgobj in objlist:
            iraf.background(input=bkgobj,output='k'+bkgobj,interactive='No',
                            sample=sample)
    else:
        for bkgobj in objlist:
            iraf.background(input=bkgobj,output='k'+bkgobj,interactive='Yes',
                            sample='*')
    return


def flux_calibrate(objlist,stdidx):
    irf_prm.set_calibrate(iraf.specred.calibrate)
    for clbobj in objlist:
        iraf.specred.calibrate(input='k'+clbobj,output='lk'+clbobj,
                               airmass=None,exptime=None,
                               sensitivity='sens'+str(stdidx))
    return

def apall_sci(objlist):
    irf_prm.set_apall_science(iraf.apall)
    for sciobj in objlist:
        iraf.apall(input='lk'+sciobj,output = 'alk'+sciobj,nfind=0)
    return

def scombine(objlist,outname):
    scinpt = ''
    for obj in objlist:
        scinpt += 'alk'+obj+','
    iraf.scombine(input=scinpt,output=outname,weight='exposure',
                  combine='median')
    return

def imcombine(inlist,outname):
    imcinpt = ''
    for obj in inlist:
        imcinpt += 'lk'+obj +','
    iraf.imcombine(input=imcinpt,output=outname,sigmas=outname+'_sig',
                   combine='median')
    return
