import file_manipulations as f_man
import fits_tools as ftl
import iraf_steps as irf_stp
def main():
    file_list = f_man.get_file_list(searchstr='*.fits')
    obj_list = [ftl.observation_type(ff) for ff in file_list]
    typedict = {}
    for file,obj in zip(file_list,obj_list):
        typedict[file.split('.')[0]] = obj
    f_man.first_movement(file_list,typedict,force_overwrite=False)
    file_list = f_man.get_file_list(searchstr='*.fits')
    for file in file_list:
        irf_stp.reduce_dimensions(file)
    quartz_list, calib_list, science_list = f_man.type_list(file_list,typedict)
    
if __name__ == '__main__':
    main()
