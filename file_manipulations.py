import os
import shutil
import glob

def make_directory(direc,silent=False,force_overwrite=True,notify=False,outmessage='Directory Created',append_dir=False):
    '''Makes a directory at location "direc"
    Arguments--
        silent: If True, will suppress messages to terminal (Default = False)
        force_overwrite: If False, will pass if directory already made (Default = True)
        notify: If True, will print message to terminal (Default = False)
        outmessage: If notify==True, message will be printed to terminal upon completion (Default = 'Directory Created')
        append_dir: If notify==True, include new directory path at end of message (Default = False)'''
    if os.path.isfile(direc):
        isfile = True
    else:
        isfile = False
    if os.path.isdir(direc):
        isdir = True
    else:
        isdir = False
    if force_overwrite:
        if isfile:
            os.remove(direc)
            if not silent: print 'File removed to create directory' 
        elif isdir:
            try:
                os.rmdir(direc)
                if not silent: print 'Old empty directory removed to create directory'
            except OSError:
                shutil.rmtree(direc)
                if not silent: print 'Occupied directory removed to create directory'
        else:
            pass
        os.mkdir(direc)
    else:
        if isfile:
            if not silent: print 'The desired directory already exists as a file'
            if not silent: print 'It is being renamed'
            shutils.move(direc,direc+'_backup_automatically_created')
        if isdir:
            if not silent: print 'Directory already exists' 
        else:
            os.mkdir(direc)
    if notify:
        if append_dir: outmessage = outmessage +' '+ direc 
        print outmessage
    return
        
def get_file_list(searchstr='*.fits'):
    '''Gets a file list from the current directory
    Arguments:
        searchstr: The string to be searched by glob (Default='*.fits')'''
    file_list = glob.glob('*.fits')
    return file_list

def move_file_list(movelist,movedir):
    '''Moves all files in a list to another directory'''
    for f in movelist:
        shutil.move(f,movedir)
    return

def move_file(movefile,movedir):
    shutil.move(movefile,movedir)
    return

def copy_file_list(movelist,movedir):
    '''Copies all files in a list to another directory'''
    for f in movelist:
        shutil.copy2(f,movedir)
    return

def first_movement(file_list,typedict,force_overwrite=False):
    '''Relocates observations to initial folders.
    Parameters
        force_overwrite -- flag to be passed to make_directory'''
    make_directory('RAW',force_overwrite=force_overwrite)
    copy_file_list(file_list,'RAW')
    make_directory('FOCUS',force_overwrite=force_overwrite)
    make_directory('FINDING',force_overwrite=force_overwrite)
    make_directory('FOCUS',force_overwrite=force_overwrite)
    for file in file_list:
        obs = file.split('.')[0]
        if typedict[obs]=='focus':
            move_file(file,'FOCUS')
        elif typedict[obs]=='slit' or typedict[obs]=='img':
            move_file(file,'FINDING')
        elif typedict[obs]=='focus':
            move_file(file,'FOCUS')
        else:
            pass
    return

def type_list(file_list,typedict,ignore=''):
    '''Returns three lists of quartz, calib, and object observations.
    Outputs -- quartz_list, calib_list, science_list'''
    quartz_list, calib_list, science_list = [],[],[]
    for ff in file_list:
        exposure = ff.split('.')[0]
        #This next check sees if the file starts with the ignore string
        #If so, it skips out the ignore string and continues
        if len(ignore) > 0 and exposure.startswith(ignore):
            exposure = exposure[len(ignore):]
        exposure = exposure.replace(ignore,'')
        exp_type = typedict[exposure]
        if exp_type == 'fear':
            calib_list.append(ff)
        elif exp_type =='qtz':
            quartz_list.append(ff)
        elif exp_type == 'obj':
            science_list.append(ff)
        else:
            pass
    return quartz_list, calib_list, science_list

def prepend_list(in_list,prefix):
    for ii in range(len(in_list)):
        in_list[ii] = prefix+ str(in_list[ii])
    return in_list

def make_and_move(move_list,folder_name):
    '''Moves all the files in move_list to folder_name, which is also created.'''
    make_directory(folder_name,silent=False,force_overwrite=True,notify=False,outmessage='Directory Created',append_dir=False)
    move_file_list(move_list,folder_name)
    return

def find_uniques_from_dict(indict,inlist):
    '''Effectively list(set([indict[y] for y in inlist])) but sorted'''
    outlist = []
    for inobj in inlist:
        if indict[inobj] in outlist:
            pass
        else:
            outlist.append(indict[inobj])
    return outlist

def make_fcname(inlist):
    '''Strips Arcs of their extra information to create simple fitcoords name'''
    outdict = {}
    for obj in inlist:
        namelist = obj.split('_')[0].split('.')
        fcname = namelist[0][-4:] + namelist[1]
        outdict[obj] = fcname
    return outdict

def bell():
    for i in range(10):
        print '\a',
    return

def gui_alert():
    print 'An IRAF GUI has been opened and requires your input'
    return
