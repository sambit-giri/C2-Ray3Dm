import numpy as np 
import os, sys, glob 

def check_sysargv(knob, fall_back, d_type):
    smooth_info = np.array([knob in a for a in sys.argv])
    if np.any(smooth_info): 
        smooth_info = np.array(sys.argv)[smooth_info]
        smooth_info = smooth_info[0].split(knob)[-1]
        smooth = d_type(smooth_info)
    else:
        try:
            smooth = d_type(fall_back)
        except:
            return None
    return smooth 

def find_nearest_greater_number(zlist_data, restart_redshift):
    greater_numbers = [x for x in zlist_data if x >= restart_redshift]
    if not greater_numbers:
        return None  # No greater number found
    nearest_greater_number = min(greater_numbers)
    return nearest_greater_number

n_cells     = check_sysargv('--n_cells=', 250, int)

uv_model    = check_sysargv('--uv_model=', 0, int)

n_timesteps = check_sysargv('--n_timesteps=', 2, int)
n_outputs   = check_sysargv('--n_outputs=', 2, int)

zlist_file  = check_sysargv('--red_file=', 'red.dat', str)
zlist_data  = np.loadtxt(zlist_file)

dens_files = glob.glob('../coarser_densities/nc{}/*n_all.dat'.format(n_cells))
if len(dens_files)==0:
    print('Either the folders are not structured properly or the n_cells={} is incorrect.'.format(n_cells))
    print('n_cells can be provided via --n_cells= knob (e.g. python setup_run.py --n_cells=250)')
    sys.exit()
else:
    dens_redshifts = np.sort(np.array([ff.split('/')[-1].split('n_all')[0] for ff in dens_files]).astype(float))

xfrac_files = glob.glob('results/xfrac3D*')
if len(xfrac_files)==0:
    print('No previous results found.')
    restart          = 0
    restart_redshift = zlist_data[1]
    restart_midpoint = 0
    restart_slice    = 1
    restart_iterdump = 'n'
    print('The created input_run will begin the simulation from z={}'.format(restart_redshift))
else:
    xfrac_redshifts = np.sort(np.array([ff.split('xfrac3D_')[-1].split('.bin')[0] for ff in xfrac_files]).astype(float))
    xfrac_files = np.array([glob.glob('results/xfrac3D_{:.3f}*'.format(zz))[0] for zz in xfrac_redshifts])  
    restart          = 1
    restart_redshift = xfrac_redshifts[0]
    restart_midpoint = int(restart_redshift not in dens_redshifts)
    restart_slice    = np.abs(find_nearest_greater_number(zlist_data, restart_redshift)-zlist_data).argmin()
    iterdump_files   = glob.glob('iterdump*')
    ## compare the iterdumps sizes to confirm completion of I/O
    iterdump_sizes   = np.array([os.path.getsize(ff) for ff in iterdump_files])
    print(iterdump_files, iterdump_sizes)
    iterdump_times   = np.array([os.path.getctime(ff) for ff in iterdump_files])
    last_result_time = os.path.getctime(xfrac_files[0])
    last_result_size = np.array([os.path.getsize(ff) for ff in xfrac_files[:2]])
    print(xfrac_files[:2], last_result_size)
    restart_iterdump = 'n' if last_result_time>iterdump_times.max() else int(iterdump_files[iterdump_times.argmax()].split('iterdump')[-1].split('.bin')[0])
    print('The created input_run will restart run from z={}'.format(restart_redshift))

restart = 'y' if restart else 'n'
restart_midpoint = 'y' if restart_midpoint else 'n'
restart_iterdump = 'n' if not restart_iterdump else restart_iterdump

with open('input_run','w') as f:
	f.write('''{0:}            !restart (y/n)
{1:}         !restart at midpoint (y/n)
{2:}         !from which slice to start/restart
{3:}         !file with redshifts
{4:}         !UV model
{5:}         !number of timesteps per density/source slice
{6:}         !number of outputs per density/source slice
{7:}         !restart from iteration dump
{8:}         !intermediate redshift if such restart
'''.format(restart, restart_midpoint, restart_slice, 'red.dat',
           uv_model, n_timesteps, n_outputs, restart_iterdump,
           restart_redshift))
    
