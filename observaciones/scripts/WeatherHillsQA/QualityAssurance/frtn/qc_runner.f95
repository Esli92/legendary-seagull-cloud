program reader
use qc

implicit none

integer :: n_times, n_stations, n_vars, i
character(len=10), dimension(:), allocatable :: stations, vars
real, dimension(:,:), allocatable :: longs, lats, elevs
real, dimension(:,:,:), allocatable :: values
integer, dimension(:,:,:,:), allocatable :: qc_flags
integer, dimension(:), allocatable :: stn_moves

character(len=36) :: arg  
call getarg(1, arg)	

open(19, file=arg // '_input.txt', action='read')

read (19, *) n_times, n_stations, n_vars
allocate(stations(n_stations), vars(n_vars), longs(n_times, n_stations), lats(n_times, n_stations), elevs(n_times, n_stations), & 
values(n_times, n_stations, n_vars), qc_flags(n_times, n_stations, n_vars, 4), stn_moves(n_stations))
qc_flags = -1
stn_moves = 0

read(19, *) stations, vars, longs, lats, elevs, values

close(19)

!print *, 'qc'
!print *, values

!print *, 'Range check'
do i = 1, n_vars
   call range_check(values, stations, vars(i), i, qc_flags) 
end do
!print *, qc_flags(:,:,:,1)


!print *, 'Step check'
do i = 1, n_vars
   call step_check(values, stations, stn_moves, vars(i), i, qc_flags) 
end do
!print *, qc_flags(:,:,:,2)


!print *, 'Persistence check'
do i = 1, n_vars
   call persistence_check(values, stations, vars(i), i, qc_flags) 
end do
!print *, qc_flags(:,:,:,3)


!print *, 'Spatial check'
do i = 1, n_vars
   call spatial_check(values, stations, lats, longs, elevs, vars(i), i, qc_flags) 
end do
!call spatial_check_dir(values, stations, lats, longs, elevs, 'wdir', 3, qc_flags)
!print *, qc_flags(:,:,:,4)


open(17, file=arg // '_result.txt', action='write')
write(17, *) qc_flags
close(17)


deallocate (stations, vars, longs, lats, elevs, values, qc_flags, stn_moves)
end program reader
