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

    #Step 1: Separate by file type and Trim/Bias Correct
    if not pm.step_one_a:

        #Get everything set up, see what we're working with
        irf_stp.initialize_iraf()
        pm.file_list = f_man.get_file_list(searchstr='*.fits')
        lgf.write_param('file_list',pm.file_list,p_type='list')

        #Determine a type for each file, with user oversight
        pm.obj_list = [ftl.observation_type(ff) for ff in pm.file_list]
        lgf.write_param('obj_list',pm.obj_list,p_type='list')
        pm.typedict = {}
        for file,obj in zip(pm.file_list,pm.obj_list):
            pm.typedict[file.split('.')[0]] = obj
        pm.typedict = gui.establish_type(pm.file_list,typedict,
                                         ['focus','img','fear','qtz','obj'])
        print pm.typedict
        lgf.write_param('typedict',pm.typedict,p_type='dict')

        #Sort everything into bins
        f_man.first_movement(pm.file_list,pm.typedict,force_overwrite=False)
        f_man.bell() #Alert user
        need_modes = gui.get_boolean('Are there multiple observing modes?')
        if need_modes:
            file_modes, nmodes = ftl.guess_mode(pm.filelist)
            nmodes_user = user_int_input(guess,title='Number of Modes')
            if nmodes_user > nmodes:
                print 'Could not automatically detect all modes. User input needed.'
                nmodes = nmodes_user + 0
            elif nmodes > nmodes_user:
                print 'Found more modes than expected. Confirm all choices.'
            else:
                print 'Same number of modes detected. Please confirm all choices.'
            #gui.establish_type(pm.file_list,typedict,
            #                             range(nmodes))
            #
            #Sort into different observing modes
            #If needed to do this, dump new param files to each and abort
            pass
        lgf.write_param('step_one_a',True,p_type='boolean')

    if not pm.step_one_b:
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


    #Step 2: Flatfield 
    if not pm.step_two:
        pm.file_list = f_man.prepend_list(pm.file_list,'b')
        [quartz_list, calib_list,
          science_list] = f_man.type_list(pm.file_list,pm.typedict,ignore='b')
        f_man.bell() #Alert user
        irf_stp.normalize_quartzes(quartz_list)
        f_man.make_and_move(quartz_list,'BIAS')
        quartz_list = f_man.prepend_list(quartz_list,'n')
        object_match = gui.find_match(science_list,quartz_list,
                                      title="Quartz Match",
                                      caption_tail=' QTZ Selection')
        irf_stp.quartz_divide(science_list,object_match)
        f_man.move_file_list(science_list,'BIAS')
        science_list = f_man.prepend_list(science_list,'f')
        f_man.make_and_move(quartz_list,'QTZ')
        lgf.write_param('step_two',True,p_type='boolean')

    #Step 3: Transform to uniform wavelength grid
    #This is where arc_coords should be established
    if not pm.step_three:
        object_match = gui.find_single_match(science_list,
                                             calib_list,
                                             title='Arc Match',
                                             caption_tail=' Arc Selection')
        guesses = ftl.guess_dxvals(science_list[0])
        arc_list = f_man.find_uniques_from_dict(object_match,science_list)
        arc_fc_dict =  f_man.make_fcname(arc_list)
        std_list = gui.select_subgroup(science_list,
                                       subunit="Standard Stars")
        non_std = [fits for fits in science_list if fits not in std_list]
        subunit = "Supplementary Dispersion Frames"
        supplement_list = gui.select_subgroup(non_std,subunit=subunit)
        irf_stp.standard_trace(std_list,supplement_list)
        irf_stp.make_lambda_solution(arc_list,arc_fc_dict)
        guesses = ftl.guess_dxvals(science_list[0])
        dx_vals = gui.user_float_inputs(['x1','x2','dx'],guesses)
        arc_coords = dato.get_dx_params(arc_list,use_fixed=True,
                                        x1=dx_vals[0],x2=dx_vals[1],
                                        dx=dx_vals[2])
        irf_stp.transform(science_list,object_match,arc_fc_dict,arc_coords)
        f_man.bell() #Alert user
        lgf.write_param('step_three',True,p_type='boolean')


    #Step 4: Make Standard star maps
    if not pm.step_four:
        f_man.make_and_move(calib_list,'CALIB')
        f_man.make_and_move(science_list,'NORM')
        science_list = f_man.prepend_list(non_std,'t')
        std_list = f_man.prepend_list(std_list,'t')
        caption = 'Select individual standard stars'
        super_std = gui.break_apart(std_list,title='Standard Selection',
                                    caption=caption)
        std_options = dato.std_options()
        calib_stars = []
        for stdl in super_std:
            stdidx = super_std.index(stdl)
            irf_stp.apall_std(stdl)
            std_name = gui.find_single_match([stdl[0]],std_options,
                                             caption_tail=' Star Name',
                                             title='Star Name')[stdl[0]]
            irf_stp.standard(stdl,std_name,stdidx)
            calib_stars.append(std_name)
            irf_stp.sensfunc(stdidx)
        f_man.make_and_move(std_list,'TRANS')
        f_man.prepend_list(std_list,'s')
        f_man.make_and_move(std_list,'STD')
        lgf.write_param('step_four',True,p_type='boolean')


    #Step 5: Flux calibrate, BKG subtract
    if not pm.step_five:
        super_science = gui.break_apart(science_list,title='Object Selection',
                                        caption='Select individual objects')
        first_science = [obj[0] for obj in super_science]
        caption_tail = 'Standard Selection'
        standard_match = gui.find_single_match(first_science,calib_stars,
                                               title='Standard Match',
                                               caption_tail=caption_tail)
        for obj in super_science:
            stdidx = calib_stars.index(standard_match[obj[0]])
            irf_stp.flux_calibrate(obj,stdidx)
            irf_stp.background(obj)
            outname = obj[0].split('.')[1]
            irf_stp.imcombine(obj,outname)
        f_man.make_and_move(science_list,'TRANS')
        f_man.prepend_list(science_list,'l')
        f_man.make_and_move(science_list,'FLUX')
        f_man.prepend_list(science_list,'s')
        f_man.make_and_move(science_list,'BKG')

        lgf.write_param('step_five',True,p_type='boolean')


    #Display total time to complete
    t1 = time()
    tmin = int( np.floor( (t1 - t0) / 60.) )
    tsec = (t1 - t0) % 60
    print 'Time: {0:2d}:{1:05.2f}'.format(tmin,tsec)



if __name__ == '__main__':
    main()
