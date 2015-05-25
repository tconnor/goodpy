import file_manipulations as f_man
import fits_tools as ftl
import iraf_steps as irf_stp
import GUI_functions as gui
import data_tools as dato
def main():
    irf_stp.initialize_iraf()
    file_list = f_man.get_file_list(searchstr='*.fits')
    obj_list = [ftl.observation_type(ff) for ff in file_list]
    typedict = {}
    for file,obj in zip(file_list,obj_list):
        typedict[file.split('.')[0]] = obj
    f_man.first_movement(file_list,typedict,force_overwrite=False)
    #Sort into different observing modes
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
    arc_list = f_man.find_uniques_from_dict(object_match,science_list)
    arc_fc_dict =  f_man.make_fcname(arc_list)
    arc_coords = dato.get_dx_params(arc_list)
    std_list = gui.select_subgroup(science_list,subunit="Standard Stars")
    non_std = [fits for fits in science_list if fits not in std_list]
    supplement_list = gui.select_subgroup(non_std,subunit="Supplementary Dispersion Frames")
    irf_stp.standard_trace(std_list,supplement_list)
    irf_stp.make_lambda_solution(arc_list,arc_fc_dict)
    irf_stp.transform(science_list,object_match,arc_fc_dict,arc_coords)
    f_man.make_and_move(calib_list,'CALIB')
    f_man.make_and_move(science_list,'NORM')
    science_list = f_man.prepend_list(non_std,'t')
    std_list = f_man.prepend_list(std_list,'t')
    #
    #Break Off Standards -- may be more than one
    #Pick which standard goes with which object
    #irf_stp.apall_std()
    #irf_stp.standard()
    #irf_stp.sensfunc()
    #f_man.make_and_move(std_list,'STD')
    #
    #irf_stp.calibrate()
    #irf_stp.background()
    #irf_stp.imcombine()
    





if __name__ == '__main__':
    main()
