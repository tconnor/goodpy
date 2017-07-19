import tempfile

def dump(filename = 'goodpy_params.py'):
    outf = open(filename,'w')
    outf.write('#GoodPy Parameter File \n')
    outf.write('step_one_a = False \n')
    outf.write('step_one_b = False \n')
    outf.write('step_two = False \n')
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
