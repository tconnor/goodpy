#!/usr/bin/env python
import sys
import os
if 'PYRAF_BETA_STATUS' in os.environ:
    if os.environ.get('PYRAF_BETA_STATUS') == '1':
        pass
    else:
        print 'Enabling PYRAF_BETA_STATUS -- adjust code if not desired'
        os.environ['PYRAF_BETA_STATUS'] = '1'
else:
    print 'PYRAF_BETA_STATUS not set; consider adding it to your .rc file'
    print 'Using `setenv PYRAF_BETA_STATUS 1`'
    os.environ['PYRAF_BETA_STATUS'] = '1'
import file_manipulations as f_man
import fits_tools as ftl
import iraf_steps as irf_stp
import GUI_functions as gui
import data_tools as dato
from time import time
import logfile as lgf
try: import goodpy_params as pm
except ImportError:
    lgf.dump()
    import goodpy_params as pm

def main():
    '''Runs through GoodPy step-by step, producing bias-subtracted,
    flat-fielded, wavelength calibrated, flux calibrated (modulo
    having a good standard star), background subtracted 2D images.

    To save the end-user time, if something fails -- or if the user
    manually aborts -- they can resume from where they were using a
    parameter file. For more information on this, see logfile.py.
    Because of this, variables are stored in the pm. namespace, and
    written to the parameter file every time they are changed. Any
    variable not stored in pm. will potentially be changed upon a
    rerun. This is bad; if the user wants to change that variable,
    they should do so in the parameter file itself.'''

    t0 = time()
    irf_stp.initialize_iraf()

    try:
        if not pm.step_one_a: run_step_one_a()
    except KeyboardInterrupt:
        lgf.step_one_a_error(pm)
    try:
        if not pm.step_one_b: run_step_one_b()
    except KeyboardInterrupt:
        lgf.step_one_b_error(pm)
        
    try:
        if not pm.step_two_a: run_step_two_a()
    except KeyboardInterrupt:
        lgf.step_two_a_error(pm)
    try:
        if not pm.step_two_b: run_step_two_b()
    except KeyboardInterrupt:
        lgf.step_two_b_error(pm)
    
    try:
        if not pm.step_three: run_step_three()
    except KeyboardInterrupt:
        lgf.step_three_error(pm)

    try:
        if not pm.step_four: run_step_four()
    except KeyboardInterrupt:
        lgf.step_four_error(pm)

    try:
        if not pm.step_five: run_step_five()
    except KeyboardInterrupt:
        lgf.step_five_error(pm)

    
    #Display total time to complete
    t1 = time()
    tmin = int((t1 - t0) / 60.) #int() also floor()s.
    tsec = (t1 - t0) % 60
    print 'Time: {0:02d}:{1:05.2f}'.format(tmin,tsec)




        
def run_step_one_a():
    '''Separates by file type and, if needed, sorts by mode.'''
    
    #Get everything set up, see what we're working with
    pm.file_list = f_man.get_file_list(searchstr='*.fits')
    f_man.red_ccd_fix(pm.file_list)
    pm.file_list = f_man.get_file_list(searchstr='*.fits')
    lgf.write_param('file_list',pm.file_list,p_type='list')

    #Determine a type for each file, with user oversight
    pm.obj_list = [ftl.observation_type(ff) for ff in pm.file_list]
    lgf.write_param('obj_list',pm.obj_list,p_type='list')
    pm.typedict = {}
    for file,obj in zip(pm.file_list,pm.obj_list):
        pm.typedict[file.split('.')[0]] = obj
    pm.typedict = gui.establish_type(pm.file_list,pm.typedict,
                                     ['focus','img','fear','qtz','obj'])
    print pm.typedict
    lgf.write_param('typedict',pm.typedict,p_type='dict')

    #Sort everything into bins
    f_man.first_movement(pm.file_list,pm.typedict,force_overwrite=False)
    f_man.bell() #Alert user
    need_modes = gui.get_boolean('Are there multiple observing modes?')
    if need_modes:
        [tmp_a,tmp_b,tmp_c] = f_man.type_list(pm.file_list,pm.typedict)
        pm.file_list = sorted(tmp_a + tmp_b + tmp_c)
        file_modes, nmodes = ftl.guess_mode(pm.file_list)
        nmodes_user = gui.user_int_input(guess=1,title='Number of Modes')
        if nmodes_user > nmodes:
            print 'Could not automatically detect all modes. User input needed.'
            nmodes = nmodes_user + 0
        elif nmodes > nmodes_user:
            print 'Found more modes than expected. Confirm all choices.'
        else:
            print 'Same number of modes detected. Please confirm all choices.'
        print file_modes
        modes_dict = gui.establish_type(pm.file_list,file_modes,range(nmodes))
        print modes_dict
        for mode in range(nmodes):
            f_man.sort_modes(modes_dict,pm.file_list,
                             pm.obj_list,pm.typedict,mode)

        sys.exit('Modes Separated. Resume reduction'+
                ' in individual directories')
    lgf.write_param('step_one_a',True,p_type='boolean')
    print 'Step 1a Completed'
    return

def run_step_one_b():
    '''Runs basic reductions including bias correct on all images'''
    pm.file_list = f_man.get_file_list(searchstr='*.fits')
    lgf.write_param('file_list',pm.file_list,p_type='list')
    if not hasattr(pm,'dimensions_reduced'):
        for ff in pm.file_list:
            irf_stp.reduce_dimensions(ff)
        lgf.write_param('dimensions_reduced',True,p_type='boolean')
        f_man.bell() #Alert user
    #There should be a way to check the bias.
    irf_stp.bias_correct(pm.file_list)
    f_man.make_and_move(pm.file_list,'ORIG')
    lgf.write_param('step_one_b',True,p_type='boolean')
    print 'Step 1b Completed'
    return

def run_step_two_a():
    '''Gives user the chance to correct the QUARTZ artifact'''
    pm.file_list = f_man.prepend_list(pm.file_list,'b')
    [pm.quartz_list, pm.calib_list,
      pm.science_list] = f_man.type_list(pm.file_list,
                                         pm.typedict,ignore='b')
    f_man.bell() #Alert user

    pm.art_cor = gui.get_boolean('Are you correcting for the QTZ artifact?')
    while pm.art_cor:
        subunit = "Quartz Artifact Frames"
        artifact_list = gui.select_subgroup(pm.quartz_list,
                                            subunit=subunit)
        if len(artifact_list) == 0:
            print 'No Artifact frames; skipping'
            break

        art_slit = [ftl.get_value(aart,'Slit') for aart in artifact_list]
        pm.quartz_list = f_man.separate_artifact_quartz(artifact_list,
                                                        pm.quartz_list)
        qtz_slit = [ftl.get_value(qqtz,'Slit') for qqtz in pm.quartz_list]
        artifacted_quartzes = []
        
        for slit in set(slits):
            art_sub = []
            qtz_sub = []
            for aa in range(len(artifact_list)):
                if art_slit[aa] == slit:
                    art_sub.append(artifact_list[aa])
            for aa in range(len(pm.quartz_list)):
                if qtz_slit[aa] == slit:
                    qtz_sub.append(pm.quartz_list[aa])
            if len(art_sub) == 0 or len(qtz_sub) == 0:
                continue #Don't qtz correct if there's no need
        
            elif len(art_sub) > 1:
                #if artifact already exists, remove it.
                artifact='qtz_artifact.fits'
                if f_man.check_for_file(artifact):
                    print artifact+' already exists.'
                    print "We're deleting it to prevent iraf conflict."
                    f_man.check_and_clear(artifact)
                irf_stp.artifact_imcombine(art_sub,artifact)
            else:
                artifact = art_sub[0]
            nartifact = 'nartifact.fits'
            f_man.check_and_clear(nartifact)
            irf_stp.normalize_artifact(artifact,nartifact)
            
            wnartifact = 'wnartifact.fits'
            f_man.check_and_clear(wnartifact)
            one_theta, thetas = ftl.get_theta(nartifact,qtz_sub)
            if one_theta:
                theta = thetas[0]
                irf_stp.artifact_create(nartifact,theta,wnartifact)
                for qtz_file in qtz_sub:
                    irf_stp.correct_artifact(wnartifact,qtz_file)
            else:
                for ii in range(len(qtz_sub)):
                    f_man.check_and_clear(wnartifact)
                    theta = thetas[ii]
                    irf_stp.artifact_create(nartifact,theta,wnartifact)
                    irf_stp.correct_artifact(wnartifact,qtz_sub[ii])

            artifacted_quartzes.extend(qtz_sub)
            
        f_man.make_and_move(artifact_list+
                            [artifact,nartifact,wnartifact],'ARTIFACT')
        f_man.make_and_move(artifacted_quartzes,'BIAS')
        tmp_qtz_list = pm.quartz_list + []
        for qtz in pm.quartz_list:
            if qtz in artifacted_quartzes:
                tmp_qtz_list.append('a'+qtz)
            else:
                tmp_qtz.append(qtz)
        pm.quartz_list = tmp_qtz + []
        #pm.quartz_list = f_man.prepend_list(pm.quartz_list,'a')
        
        break

    lgf.write_param('file_list',pm.file_list,p_type='list')
    lgf.write_param('quartz_list',pm.quartz_list,p_type='list')
    lgf.write_param('calib_list',pm.calib_list,p_type='list')
    lgf.write_param('science_list',pm.science_list,p_type='list')
    lgf.write_param('art_cor',pm.art_cor,p_type='boolean')
    lgf.write_param('step_two_a',True,p_type='boolean')
    print 'Step 2a Completed'
    return


def run_step_two_b():    
    '''Normalize the quartes'''
    if not hasattr(pm,'already_normalized'):
        dont_norm = []
    else:
        dont_norm = pm.already_normalized
    if not hasattr(pm,'fix_quartz_banding'):
        checkstring = 'Are you fixing the banding in Quartz frames?'
        if not ftl.has_pf:
            pm.fix_quartz_banding = False
        else:
            pm.fix_quartz_banding = gui.get_boolean(checkstring)
    run_interactive = gui.get_boolean('Normalize Quartzes Interactively?')
    irf_stp.normalize_quartzes(pm.quartz_list,dont_norm,pm.fix_quartz_banding,
                               run_interactive)
    lgf.write_param('already_normalized',pm.quartz_list,p_type='list')
    
    if pm.art_cor:
        f_man.make_and_move(pm.quartz_list,'ARCQTZ')
    else:
        f_man.make_and_move(pm.quartz_list,'BIAS')            
    pm.quartz_list = f_man.prepend_list(pm.quartz_list,'n')
    if pm.fix_quartz_banding:
        f_man.make_and_move(pm.quartz_list,'BNDQTZ')
        pm.quartz_list = f_man.prepend_list(pm.quartz_list,'w')
    qtzmatch_presels = dato.guess_qtz_matches(pm.science_list,
                                              pm.quartz_list)
    object_match = gui.find_match(pm.science_list,pm.quartz_list,
                                  title="Quartz Match",
                                  caption_tail=' QTZ Selection',
                                  prepick=True,presels=qtzmatch_presels)
    irf_stp.quartz_divide(pm.science_list,object_match)
    f_man.move_file_list(pm.science_list,'BIAS')
    pm.science_list = f_man.prepend_list(pm.science_list,'f')
    f_man.make_and_move(pm.quartz_list,'QTZ')

    lgf.write_param('science_list',pm.science_list,p_type='list')
    lgf.write_param('step_two_b',True,p_type='boolean')

    print 'Step 2b Completed'
    return

def run_step_three():
    '''Transform to uniform wavelength grid'''
    if not f_man.check_for_file('linelist'):
        f_man.write_linelist('linelist')
    if not hasattr(pm,'arcs_identified'):
        pm.arcs_identified=False
    if not hasattr(pm,'standard_traced'):
        pm.standard_traced=False

    if not pm.arcs_identified:
        pm.object_match = gui.find_single_match(pm.science_list,
                                                pm.calib_list,
                                                title='Arc Match',
                                                caption_tail=' Arc Selection')
        guesses = ftl.guess_dxvals(pm.science_list[0])
        pm.arc_list = f_man.find_uniques_from_dict(pm.object_match,
                                                   pm.science_list)
        pm.arc_fc_dict =  f_man.make_fcname(pm.arc_list)
        pm.std_list = gui.select_subgroup(pm.science_list,
                                    subunit="Standard Stars")
        pm.non_std = [fits for fits in pm.science_list if
                      fits not in pm.std_list]
        subunit = "Supplementary Dispersion Frames"
        pm.supplement_list = gui.select_subgroup(pm.non_std,subunit=subunit)
        lgf.write_param('object_match',pm.object_match,p_type='dict')
        lgf.write_param('arc_list',pm.arc_list,p_type='list')
        lgf.write_param('arc_fc_dict',pm.arc_fc_dict,p_type='dict')
        lgf.write_param('std_list',pm.std_list,p_type='list')
        lgf.write_param('non_std',pm.non_std,p_type='list')
        lgf.write_param('supplement_list',pm.supplement_list,p_type='list')
        lgf.write_param('arcs_identified',True,p_type='boolean')
                                                
    if not pm.standard_traced:
        irf_stp.standard_trace(pm.std_list,pm.supplement_list)
        lgf.write_param('standard_traced',True,p_type='boolean')

    if not hasattr(pm,'already_identified'):
        dont_ident = []
    else:
        dont_ident = pm.already_identified

    irf_stp.make_lambda_solution_auto(pm.arc_list,pm.arc_fc_dict,dont_ident,
                                      f_man.is_datafile_good)
    lgf.write_param('already_identified',pm.arc_list,p_type='list')
    
    guesses = ftl.guess_dxvals(pm.science_list[0])
    dx_vals = gui.user_float_inputs(['x1','x2','dx'],guesses)
    arc_coords = dato.get_dx_params(pm.arc_list,use_fixed=True,
                                    x1=dx_vals[0],x2=dx_vals[1],
                                    dx=dx_vals[2])
    irf_stp.transform(pm.science_list,pm.object_match,pm.arc_fc_dict,arc_coords)
    f_man.bell() #Alert user
    lgf.write_param('step_three',True,p_type='boolean')
    f_man.make_and_move(pm.calib_list,'CALIB')
    f_man.make_and_move(pm.science_list,'NORM')
    pm.science_list = f_man.prepend_list(pm.non_std,'t')
    pm.std_list = f_man.prepend_list(pm.std_list,'t')
    lgf.write_param('science_list',pm.science_list,p_type='list')
    lgf.write_param('std_list',pm.std_list,p_type='list')
    print 'Step 3 Completed'
    return

def run_step_four():
    '''Make Standard star maps'''
    print 'Select each standard star'
    print 'by selecting all of the observations for each standard star'
    print 'star-by-star.'
    caption = 'Select individual standard stars'
    pm.super_std = gui.break_apart(pm.std_list,title='Standard Selection',
                                caption=caption)
    std_options = dato.std_options()
    pm.calib_stars = []
    for stdl in pm.super_std:
        stdidx = pm.super_std.index(stdl)
        irf_stp.background(stdl)
        irf_stp.apall_std(stdl)
        std_name = gui.find_single_match([stdl[0]],std_options,
                                         caption_tail=' Star Name',
                                         title='Star Name')[stdl[0]]
        irf_stp.standard(stdl,std_name,stdidx)
        if std_name not in pm.calib_stars:
            pm.calib_stars.append(std_name)
        else:
            str_idx = 2
            while True:
                atmpt = std_name +'_'+ str(str_idx)
                if atmpt not in pm.calib_stars:
                    pm.calib_stars.append(atmpt)
                    break
                str_idx +=1
        irf_stp.sensfunc(stdidx)
    f_man.make_and_move(pm.std_list,'TRANS')
    f_man.prepend_list(pm.std_list,'k')
    f_man.make_and_move(pm.std_list,'BKGSTD')
    f_man.prepend_list(pm.std_list,'s')
    f_man.make_and_move(pm.std_list,'STD')
    
    lgf.write_param('science_list',pm.science_list,p_type='list')
    lgf.write_param('std_list',pm.std_list,p_type='list')
    lgf.write_param('calib_stars',pm.calib_stars,p_type='list')
    lgf.write_param('step_four',True,p_type='boolean')
    print 'Step 4 Completed'
    return

def run_step_five():
    '''Flux calibrate and BKG subtract science images'''
    super_science = gui.break_apart(pm.science_list,title='Object Selection',
                                    caption='Select individual objects')
    first_science = [obj[0] for obj in super_science]
    caption_tail = 'Standard Selection'
    standard_match = gui.find_single_match(first_science,pm.calib_stars,
                                           title='Standard Match',
                                           caption_tail=caption_tail)
    if not hasattr(pm,'already_calibrated'):
        pm.already_calibrated = []
    pm.extr1d = gui.get_boolean('Perform 1-D extractions?')

    for obj in super_science:
        if obj in pm.already_calibrated:
            continue
        stdidx = pm.calib_stars.index(standard_match[obj[0]])
        irf_stp.background(obj,unique=False)
        irf_stp.flux_calibrate(obj,stdidx)
        if pm.extr1d:
            irf_stp.apall_sci(obj)
            soutname = 's_'+obj[0].split('.')[1]
            irf_stp.scombine(obj,soutname)
        outname = obj[0].split('.')[1]
        irf_stp.imcombine(obj,outname)

    f_man.make_and_move(pm.science_list,'TRANS')
    f_man.prepend_list(pm.science_list,'k')
    f_man.make_and_move(pm.science_list,'BKG')
    f_man.prepend_list(pm.science_list,'l')
    f_man.make_and_move(pm.science_list,'FLUX')
    if pm.extr1d:
        aperturelist = ['a'+flnm for flnm in pm.science_list]
        f_man.make_and_move(aperturelist,'APEX')

    lgf.write_param('step_five',True,p_type='boolean')
    print 'Step 5 Completed'
    return






if __name__ == '__main__':
    main()
