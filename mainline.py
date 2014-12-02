import file_manipulations as f_man
import fits_tools as ftl
def main():
    file_list = f_man.get_file_list(searchstr='*.fits')
    obj_list = [ftl.observation_type(ff) for ff in file_list]
    f_man.make_directory('RAW',force_overwrite=False)
    f_man.copy_list(file_list,'RAW')
    f_man.make_directory('FOCUS',force_overwrite=False)
    for file,obj in zip(file_list,obj_list):
        if obj=='focus':
            f_man.move_file(file,'FOCUS')

    f_man.make_directory('FINDING',force_overwrite=False)
    for file,obj in zip(file_list,obj_list):
        if obj=='slit' or obj=='img':
            f_man.move_file(file,'FINDING')
    f_man.make_directory('FOCUS',force_overwrite=False)
    for file,obj in zip(file_list,obj_list):
        if obj=='focus':
            f_man.move_file(file,'FOCUS')

    pass

if __name__ == '__main__':
    main()
