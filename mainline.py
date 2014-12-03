import file_manipulations as f_man
import fits_tools as ftl
def main():
    file_list = f_man.get_file_list(searchstr='*.fits')
    obj_list = [ftl.observation_type(ff) for ff in file_list]
    typedict = {}
    for file,obj in zip(file_list,obj_list):
        typedict[file.split('.')[0]] = obj
    f_man.first_movement(file_list,typedict,force_overwrite=False)

if __name__ == '__main__':
    main()
