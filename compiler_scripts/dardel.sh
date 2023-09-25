module swap PrgEnv-cray PrgEnv-gnu

# For the makefile located in the parent directory
# Clean the previous build (assuming make_ifort is used)
# make -C ../ -f make_ifort clean
# Build the code (assuming make_ifort is used)
# make -C ../ -f make_ifort C2Ray_3D_cubep3m_periodic_omp_mpi

# Clean the previous build (assuming make_gfortran is used)
make -C ../ -f make_gfortran clean
# Build the code (assuming make_gfortran is used)
make -C ../ -f make_gfortran C2Ray_3D_cubep3m_periodic_omp_mpi