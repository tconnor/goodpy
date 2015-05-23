import file_manipulations as f_man
import fits_tools as ftl
import iraf_steps as irf_stp
import GUI_functions as gui
def main():
    irf_stp.initialize_iraf()
    file_list = f_man.get_file_list(searchstr='*.fits')
    obj_list = [ftl.observation_type(ff) for ff in file_list]
    typedict = {}
    for file,obj in zip(file_list,obj_list):
        typedict[file.split('.')[0]] = obj
    f_man.first_movement(file_list,typedict,force_overwrite=False)
    file_list = f_man.get_file_list(searchstr='*.fits')
    for ff in file_list:
        irf_stp.reduce_dimensions(ff)
    irf_stp.bias_correct(file_list)
    f_man.make_and_move(file_list,'ORIG')
    file_list = f_man.prepend_list(file_list,'b')
    quartz_list, calib_list, science_list = f_man.type_list(file_list,typedict,ignore='b')
    irf_stp.normalize_quartzes(quartz_list)
    f_man.make_and_move(quartz_list,'BIAS')
    quartz_list = f_man.prepend_list(quartz_list,'n')
    object_match = gui.find_match(science_list,quartz_list,title="Quartz Match",caption_tail='QTZ Selection')
    irf_stp.quartz_divide(science_list,object_match)
    f_man.move_file_list(science_list,'BIAS')
    science_list = f_man.prepend_list(science_list,'f')
    f_man.make_and_move(quartz_list,'QTZ')
    object_match = gui.find_single_match(science_list,calib_list,title='Arc Match',caption_tail='Arc Selection')
    std_list = gui.select_subgroup(science_list,subunit="Standard Stars")
    print std_list
    print science_list
    #irf_stp.make_lambda_solution
    #    -Identify
    #    -Reidentify
    #    -Fitcoords
    #irf_stp.standard_trace
    #irf_stp.transform(science_list)
    #f_man.make_and_move(calib_list,'CALIB')
    #science_list = f_man.prepend_list(science_list,'t')
    #irf_stp.apall_std()
    #irf_stp.standard()
    #irf_stp.sensfunc()
    #irf_stp.calibrate()
    #irf_stp.background()
    #irf_stp.imcombine()
    





if __name__ == '__main__':
    main()
