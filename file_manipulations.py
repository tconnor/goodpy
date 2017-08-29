import os
import shutil
import glob
import logfile as lgf

def make_directory(direc,silent=False,force_overwrite=True,notify=False,
                   outmessage='Directory Created',append_dir=False):
    '''Makes a directory at location "direc"
    Arguments--
        silent: If True, will suppress messages to
                terminal (Default = False)
        force_overwrite: If False, will pass if directory already made
                         (Default = True)
        notify: If True, will print message to terminal (Default = False)
        outmessage: If notify==True, message will be printed to terminal
                    upon completion (Default = 'Directory Created')
        append_dir: If notify==True, include new directory path at end
                    of message (Default = False)'''
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
                if not silent:
                    print 'Old empty directory removed to create directory'
            except OSError:
                shutil.rmtree(direc)
                if not silent:
                    print 'Occupied directory removed to create directory'
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


def red_ccd_fix(filelist):
    '''Changes file names from XXXX_filename to XXXX.filename
    This was a change made when switching to the Red CCD and
    it's easier to just have them all in the same format.'''
    tick = 0
    for ff in filelist:
        if ff[:4].isdigit() and ff[4]=='_':
            if tick == 0:
                print 'Red CCD file format detected'
                print 'Files are being renamed for ',
                print 'goodpy compatability'
                tick = 1
            fnew = ff[:4]+'.'+ff[5:]
            shutil.move(ff,fnew)
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
    make_directory(folder_name,silent=False,force_overwrite=True,notify=False,
                   outmessage='Directory Created',append_dir=False)
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

def sort_modes(modes_dict,file_list,obj_list,typedict,mode):
    out_file_list = []
    out_obj_list = []
    out_type_dict = {}
    for flnm in file_list:
        shrt = flnm.split('.')[0]
        if modes_dict[shrt] != mode:
            continue
        out_file_list.append(flnm)
        out_obj_list.append(typedict[shrt])
        out_type_dict[shrt] = typedict[shrt]
    direc= '{}_Mode'.format(mode)
    if len(out_file_list) >= 1:
        #This check is necessary in case the guess finds a mode but
        #the user says there isn't one. This prevents a crash
        make_and_move(out_file_list,direc)
        lgf.dump_mode(direc,out_file_list,out_obj_list,out_type_dict)
    return

def separate_artifact_quartz(artifact_list,quartz_list):
    outlist = []
    for qtz in quartz_list:
        if qtz not in artifact_list:
            outlist.append(qtz)
        else:
            pass
    return outlist
    
def check_for_file(filename):
  
    if os.path.isdir(filename):
        #This isn't good; it's a directory!
        return True #No better way to handle this...

    if os.path.isfile(filename):
        return True

    else:
        return False

def check_and_clear(filename):
    '''Checks to see if a file exists; if so, it removes it'''
    if os.path.isdir(filename):
        #This isn't good; it's a directory!
        return #No better way to handle this...

    if os.path.isfile(filename):
        os.remove(filename)
        return
    
    else:
        return

def find_and_clear(search_string):
    file_list = glob.glob(search_string)
    for ff in file_list:
        os.remove(ff)
    return

def write_linelist(outfile,lamp='fear'):
    outfile = open(outfile,'w')
    if lamp == 'fear':
        lines = ['4045.8130','4158.5903','4259.3618','4277.5283','4325.7617',
                 '4348.0640','4383.5444','4404.7500','4426.0010','4481.8105',
                 '4545.0518','4579.3496','4589.8979','4609.5674','4657.9014',
                 '4847.8095','4879.8635','4889.0422','4965.0795','5015.6779',
                 '5141.7827','5162.2846','5187.7462','5495.8738','5558.7020',
                 '5606.7330','5650.7043','5739.6210','5875.6210','5912.0853',
                 '6032.1274','6114.9239','6172.2778','6416.3071','6677.2817',
                 '6752.8335','6871.2891','6965.4307','7030.2514','7067.2181',
                 '7147.0416','7272.9359','7383.9805','7503.8691','7514.6519',
                 '7635.1060','7948.1763','8264.5225','8408.2100','8424.6475']
    for line in lines:
        outfile.write(line)
        outfile.write('\n')
    outfile.close()
