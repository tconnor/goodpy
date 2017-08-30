import tempfile
import sys
import file_manipulations as f_man

def dump(filename = 'goodpy_params.py'):
    outf = open(filename,'w')
    outf.write('#GoodPy Parameter File \n')
    outf.write('step_one_a = False \n')
    outf.write('step_one_b = False \n')
    outf.write('step_two_a = False \n')
    outf.write('step_two_b = False \n')
    outf.write('step_three = False \n')
    outf.write('step_four = False \n')
    outf.write('step_five = False \n')
    outf.close()
    return

def dump_mode(direc,file_list,obj_list,type_dict):
    dump(filename='{0}/goodpy_params.py'.format(direc))
    write_param('file_list',file_list,p_type='list',
                outname='{0}/goodpy_params.py'.format(direc))
    write_param('obj_list',obj_list,p_type='list',
                outname='{0}/goodpy_params.py'.format(direc))
    write_param('type_dict',type_dict,p_type='dict',
                outname='{0}/goodpy_params.py'.format(direc))
    write_param('step_one_a','True',p_type='boolean',
                outname='{0}/goodpy_params.py'.format(direc))
    return

def write_param(param_name,param_vals,
                p_type='string',comment='',
                outname='goodpy_params.py'):
    if comment == '':
        comment = param_name
    p_type = p_type.lower() #Idiot Proofing
    i = open(outname,'r')
    t = tempfile.NamedTemporaryFile(mode='r+')
    for line in i:
        if '#' not in line:
            t.write(line)
        else:
            incomment = line.split('#')[1].strip()
            if incomment != comment:
                t.write(line)
            else:
                pass
    
    t.write('{0} = '.format(param_name))
    if p_type == 'string':
        t.write('{0} '.format(param_vals))
    if p_type == 'boolean':
        if param_vals: t.write('True ')
        else: t.write('False ')
    if p_type == 'list':
        if len(param_vals) == 0:
            t.write('[]')
        elif len(param_vals) == 1:
            t.write('[')
            pvls = param_vals[0]
            if type(pvls) == type('string'):
                t.write('"{0}"]'.format(pvls))
            else:
                t.write('{0}]'.format(pvls))
        else:
            t.write('[')
            for pvls in param_vals[:-1]:
                if type(pvls) == type('string'):
                    t.write('"{0}",'.format(pvls))
                else:
                    t.write('{0},'.format(pvls))
            if type(pvls) == type('string'):
                t.write('"{0}"]'.format(param_vals[-1]))
            else:
                t.write('{0}]'.format(param_vals[-1]))

    if p_type == 'dict':
        pkeys = param_vals.keys()
        if len(pkeys) == 0:
            t.write('{}')
        else:
            t.write('{')
            for pkey in pkeys[:-1]:
                if type(pkey) == type('string'):
                    t.write('"{0}":'.format(pkey))
                else:
                    t.write('{0}:'.format(pkey))
                if type(param_vals[pkey]) == type('string'):
                    t.write('"{0}",'.format(param_vals[pkey]))
                else:
                    t.write('{0},'.format(param_vals[pkey])) 
            t.write('"{0}":"{1}"'.format(pkeys[-1],param_vals[pkeys[-1]]))
            t.write('} ')
    t.write('# {0} \n'.format(comment))
    i.close() #Close input file
    t.seek(0) #Rewind temporary file to beginning
    o = open(outname, "w")  #Reopen input file writable

    #Overwriting original file with temporary file contents          
    for line in t:
        o.write(line)  

    t.close() #Close temporary file, will cause it to be deleted


def step_one_a_error(pm):
    print 'User Abort Detected in Step 1a'
    sys.exit('Due to the short nature of step one,'+
             ' nothing is being written to the log file.')

def step_one_b_error(pm):
    print 'User Abort Detected in Step 1b'
    for ff in pm.filelist:
        f_man.check_and_clear('b'+ff)
    f_man.find_and_clear('tmp*fits')
    sys.exit('Bias corrected images and any temp images removed')

def step_two_a_error(pm):
    print 'User Abort Detected in Step 2a'
    sys.exit('Due to the short nature of step 2a,'+
             ' nothing is being written to the log file.')

def step_two_b_error(pm):
    localvars = sys.exc_info()[2].tb_next.tb_next.tb_frame.f_locals
    print 'User Abort Detected in Step 2b'
    print localvars
    if 'dont_norm_list' in localvars:
        dont_norm = localvars['dont_norm_list']
        write_param('already_normalized',dont_norm,p_type='list')
        print 'Quartz files already normalized written to param file as ',
        print 'already_normalized'
        print 'These will be skipped on next pass'
    for ff in pm.science_list:
        f_man.check_and_clear('f'+ff)
    f_man.check_and_clear('tempquartz.fits')
    sys.exit('Clearing any flat-fielded images already made.')

def step_three_error(pm):
    print 'User Abort Detected in Step 3'
    localvars = sys.exc_info()[2].tb_next.tb_frame.f_locals
    if 'dont_ident_list' in localvars:
        dont_ident = localvars['dont_ident_list']
        write_param('already_identified',dont_ident,p_type='list')
        print 'Arc files already identified written to param file as ',
        print 'already_identified'
        print 'These will be skipped on next pass'
    for ff in pm.science_list:
        f_man.check_and_clear('t'+ff)

    sys.exit('Clearing any already transformed images already made')

def step_four_error(pm):
    print 'User Abort Detected in Step 4'
    for ff in pm.std_list:
        f_man.check_and_clear('s'+ff)
    for stdl in pm.super_std:
        stdidx = pm.super_std.index(stdl)
        f_man.check_and_clear('std'+str(stdidx))
        f_man.check_and_clear('sens'+str(stdidx))
    sys.exit('Clearing any standard star or sensfunc images alrady made')

def step_five_error(pm):
    print 'User Abort Detected in Step 5'
    write_param('already_calibrated',pm.already_calibrated,p_type='list')
    print 'Science files already calibrated written to param file as ',
    print 'already_calibrated'
    print 'These will be skipped on next pass'

    sys.exit('No files deleted on cleanup')
