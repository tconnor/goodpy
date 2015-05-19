import file_manipulations as f_man
import fits_tools as ftl
import iraf_steps as irf_stp
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
    #science_list = f_man.prepend_list(science_list,'f')
    #get the arc images needed
    #irf_stp.identify
    #irf_stp.make_lambda_solution
    #f_man.make_and_move(calib_list,'CALIB')
    #irf_stp.standard_trace
    #irf_stp.transform(science_list)
    #science_list = f_man.prepend_list(science_list,'t')

if __name__ == '__main__':
    main()
