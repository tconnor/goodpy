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

