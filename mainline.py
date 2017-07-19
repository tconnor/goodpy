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

def main():


    #Step 1: Separate by file type and Trim/Bias Correct
    t0 = time()
    irf_stp.initialize_iraf()
    file_list = f_man.get_file_list(searchstr='*.fits')
    obj_list = [ftl.observation_type(ff) for ff in file_list]
    typedict = {}
    for file,obj in zip(file_list,obj_list):
        typedict[file.split('.')[0]] = obj
    typedict = gui.establish_type(file_list,typedict,['focus','img','fear','qtz','obj'])
    print typedict
    f_man.first_movement(file_list,typedict,force_overwrite=False)
    f_man.bell() #Alert user
    #Sort into different observing modes
    file_list = f_man.get_file_list(searchstr='*.fits')
    for ff in file_list:
        irf_stp.reduce_dimensions(ff)
    f_man.bell() #Alert user
    #There should be a way to check the bias.
    irf_stp.bias_correct(file_list)
    f_man.make_and_move(file_list,'ORIG')



    #Step 2: Flatfield 
    file_list = f_man.prepend_list(file_list,'b')
    quartz_list, calib_list, science_list = f_man.type_list(file_list,typedict,ignore='b')
    f_man.bell() #Alert user
    irf_stp.normalize_quartzes(quartz_list)
    f_man.make_and_move(quartz_list,'BIAS')
    quartz_list = f_man.prepend_list(quartz_list,'n')
    object_match = gui.find_match(science_list,quartz_list,title="Quartz Match",caption_tail=' QTZ Selection')
    irf_stp.quartz_divide(science_list,object_match)
    f_man.move_file_list(science_list,'BIAS')
    science_list = f_man.prepend_list(science_list,'f')
    f_man.make_and_move(quartz_list,'QTZ')

    #Step 3: Transform to uniform wavelength grid
    #This is where arc_coords should be established
    object_match = gui.find_single_match(science_list,calib_list,title='Arc Match',caption_tail=' Arc Selection')
    guesses = ftl.guess_dxvals(science_list[0])
    arc_list = f_man.find_uniques_from_dict(object_match,science_list)
    arc_fc_dict =  f_man.make_fcname(arc_list)
    std_list = gui.select_subgroup(science_list,subunit="Standard Stars")
    non_std = [fits for fits in science_list if fits not in std_list]
    supplement_list = gui.select_subgroup(non_std,subunit="Supplementary Dispersion Frames")
    irf_stp.standard_trace(std_list,supplement_list)
    irf_stp.make_lambda_solution(arc_list,arc_fc_dict)
    guesses = ftl.guess_dxvals(science_list[0])
    dx_vals = gui.user_float_inputs(['x1','x2','dx'],guesses)
    arc_coords = dato.get_dx_params(arc_list,use_fixed=True,x1=dx_vals[0],x2=dx_vals[1],dx=dx_vals[2])
    irf_stp.transform(science_list,object_match,arc_fc_dict,arc_coords)
    f_man.bell() #Alert user


    #Step 4: Make Standard star maps
    f_man.make_and_move(calib_list,'CALIB')
    f_man.make_and_move(science_list,'NORM')
    science_list = f_man.prepend_list(non_std,'t')
    std_list = f_man.prepend_list(std_list,'t')
    super_std = gui.break_apart(std_list,title='Standard Selection',caption='Select individual standard stars')
    std_options = dato.std_options()
    calib_stars = []
    for stdl in super_std:
        stdidx = super_std.index(stdl)
        irf_stp.apall_std(stdl)
        std_name = gui.find_single_match([stdl[0]],std_options,title='Star Name',caption_tail=' Star Name')[stdl[0]]
        irf_stp.standard(stdl,std_name,stdidx)
        calib_stars.append(std_name)
        irf_stp.sensfunc(stdidx)
    f_man.make_and_move(std_list,'TRANS')
    f_man.prepend_list(std_list,'s')
    f_man.make_and_move(std_list,'STD')


    #Step 5: Flux calibrate, BKG subtract
    super_science = gui.break_apart(science_list,title='Object Selection',caption='Select individual objects')
    first_science = [obj[0] for obj in super_science]
    standard_match = gui.find_single_match(first_science,calib_stars,title='Standard Match',caption_tail='Standard Selection')
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
    
    #Display total time to complete
    t1 = time()
    tmin = int( np.floor( (t1 - t0) / 60.) )
    tsec = (t1 - t0) % 60
    print 'Time: {0:2d}:{1:05.2f}'.format(tmin,tsec)





if __name__ == '__main__':
    main()
