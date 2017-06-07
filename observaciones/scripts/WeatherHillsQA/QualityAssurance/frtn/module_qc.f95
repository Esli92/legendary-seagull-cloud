!--- compile with pgf90 -c -Mfreeform module_qc.f
!---
!--- module_qc.f:  performs QC checks on meteorological observations, 
!--- modeled after Shafer et al. (2000) J. of Atmos. and Oceanic Tech.  
!--- Version 2.0, jbaars, UW.
!---
!-----------------------------------------------------------------------------

      module qc

!      use constants
!      use dirtools

      implicit none
 
!-----------------------------------------------------------------------------
!--- Parameters and Constants
!-----------------------------------------------------------------------------
      integer, parameter :: nqcflags   = 9   ! total number of qc flags
      integer, parameter :: passflag   = 0   ! "pass" qc value.
      integer, parameter :: suspflag   = 1   ! "suspect" qc value.
      integer, parameter :: warnflag   = 2   ! "warning" qc value.
      integer, parameter :: failflag   = 3   ! "failed" qc value.
      integer, parameter :: notestflag = 8   ! "not-tested" qc value.
      integer, parameter :: mflag      = 9   ! "missing" qc value.      

      character(len=1), parameter :: passflag_ch   = '0' ! "pass" qc val.
      character(len=1), parameter :: suspflag_ch   = '1' ! "suspect" qc val.
      character(len=1), parameter :: warnflag_ch   = '2' ! "warning" qc val.
      character(len=1), parameter :: failflag_ch   = '3' ! "failed" qc val.
      character(len=1), parameter :: notestflag_ch = '8' ! "not-tested" qc val.
      character(len=1), parameter :: mflag_ch      = '9' ! "missing" qc val.  

      integer, parameter :: irangeflag   = 1 ! index for range test qc flag.
      integer, parameter :: istepflag    = 2 ! index for step test qc flag.
      integer, parameter :: ipersistflag = 3 ! index for persistence test flag.
      integer, parameter :: ispatialflag = 4 ! index for spatial test qc flag.

      real, parameter :: mvc    = -888888.0  ! missing value constant.
      real, parameter :: obsmvc = -888888.0
      real, parameter :: trace  = -666666.0

      integer, parameter :: ispd = 1 !moze to jakies indeksy? gdize co jest?
      integer, parameter :: idir = 1
      integer, parameter :: iu = 1
      integer, parameter :: iv = 1
      integer, parameter :: it = 1      ! index temp
      integer, parameter :: itd = 1     ! index temp dew
      
      contains 
        
!-----------------------------------------------------------------------------
!--- Range Test
!-----------------------------------------------------------------------------
      subroutine range_check(obs, stnnets, var, ivar, qc_flag)

         real,             dimension(:,:,:),   intent(IN)    :: obs
         character(len=*), dimension(:),       intent(IN)    :: stnnets(:)
         character(len=*),                     intent(IN)    :: var
         integer,                              intent(IN)    :: ivar
         integer,          dimension(:,:,:,:), intent(INOUT) :: qc_flag

         real    :: minrange, maxrange
         integer :: nstnnets, ndts
         integer :: d, s, level, iqcflag
         integer :: debug, firsttime

         !--- tolerance for dew point being > temperature.
         logical         :: do_td_gt_t_test
         real, parameter :: td_gt_t_tol = 2.0

         intrinsic maxval, minval, size

         !--- settings for run.
         debug     = 1               ! sets debug level (sets what to print)
         iqcflag   = irangeflag      ! array index of range test.
         ndts      = size(obs(:,1,ivar))  ! # of hours in obs.
         nstnnets  = size(stnnets)   ! # of stnnets.
         firsttime = 1               ! first time through loop indicator.
         level     = failflag        ! all out-of-range values get "fail."

         do_td_gt_t_test = .FALSE.

         !--- set ranges for each variable.
         select case (var)
         case('t', 'temp', 'td', 'dewp') !--- temperatures
            minrange = 225
            maxrange = 323
            do_td_gt_t_test = .TRUE.
         case('tmax', 'tmin')
            minrange = 225
            maxrange = 323
         case('gust')               !--- wind gusts
            minrange = 0
            maxrange = 70
         case('mixr')               !--- mixing ratio
            minrange = 0
            maxrange = 25
         case('rh')                 !--- relative humidity
            minrange = 0.
            maxrange = 105.
         case('pcp6')              !--- precipitation 6-hr [mm]
            minrange = 0
            maxrange = 256
         case('pcp24')              !--- precipitation 24-hr [mm]
            minrange = 0
            maxrange = 508
         case('slp','sfp')          !--- sea level pressure [Pa]
            minrange = 80000.
            maxrange = 107840.
         case('spd','wsp')          !--- wind speed
            minrange = 0
            maxrange = 60
         case('dir','wdir')         !--- wind direction
            minrange = 0
            maxrange = 360
         end select

         do d = 1, ndts
            do s = 1, nstnnets

               !--- Cannot do range test if value is missing.
               if (obs(d,s,ivar) .eq. mvc) then
                  ! value is a fill value, set qc_flag to missing.
                  qc_flag(d,s,ivar,iqcflag) = mflag
                  cycle
               end if

               if (obs(d,s,ivar) .lt. minrange .or. &
                   obs(d,s,ivar) .gt. maxrange) then

                  !--- Don't flag traces for precip!
                  !if (index(var, 'pcp')) then
                  if (index(var, 'pcp') .gt. 0) then
                     if (obs(d,s,ivar) .eq. trace) then
                        qc_flag(d,s,ivar,iqcflag) = passflag
                     else
                        qc_flag(d,s,ivar,iqcflag) = level
                     end if
                  else
                     qc_flag(d,s,ivar,iqcflag) = level
                  end if
                  if (debug .eq. 1 .and. &
                      qc_flag(d,s,ivar,iqcflag) .eq. level) then 
                     if (firsttime .eq. 1) then 
                        print *,''
                        print *,'Station    obs val'
                        print *,'-------    -------'
                        firsttime = 0
                     end if
 10                  format(3x, A8, 3x, F16.8)
                     write (*,10), stnnets(s), obs(d,s,ivar)
                  end if
               else

                  !--- value passes range check.
                  qc_flag(d,s,ivar,iqcflag) = passflag

                  !--- if this is temperature or dew point, make sure dew point
                  !--- is not greater than temperature (by 'td_gt_t_tol').
                  if ( do_td_gt_t_test .eqv. .TRUE.) then
                     if ( obs(d,s,itd) .ne. mvc .and. &
                          obs(d,s,it)  .ne. mvc ) then
                        if ( (obs(d,s,itd) - obs(d,s,it)) > td_gt_t_tol) then
                           qc_flag(d,s,it, iqcflag) = 2
                           qc_flag(d,s,itd,iqcflag) = 2
                        end if
                     end if
                  end if

               end if

            end do
         end do

      end subroutine range_check

!-----------------------------------------------------------------------------
!--- Step Test
!-----------------------------------------------------------------------------

      subroutine step_check(obs, stnnets, stn_moves, var, ivar, qc_flag)

         !--- Perform "delta test" which, for each station checks each hour
         !--- in a day, checks for jumps between consecutive observations
         !--- that exceed a given threshold.
         !--- 
         !--- obs          data array with dimensions hours and stations. 
         !--- stnnets      character array of stnnet station names.
         !--- stn_moves    integer array telling if station moves (1=moves).
         !--- var          character string name of the variable.
         !--- ivar         array index of d for the variable in question.
         !--- qc_flag      array of incoming/outgoing quality control flags.

         real,             dimension(:,:,:),   intent(IN)    :: obs
         character(len=*), dimension(:),       intent(IN)    :: stnnets(:)
         integer,                              intent(IN)    :: stn_moves(:)
         character(len=*),                     intent(IN)    :: var
         integer,                              intent(IN)    :: ivar
         integer,          dimension(:,:,:,:), intent(INOUT) :: qc_flag

         integer :: nstnnets, ndts
         integer :: d, s
         integer :: debug, firsttime, var_is_dir, iqcflag
         integer :: level1, level2
         real    :: step1, step2, step_3pt
         integer :: too_many_spikes, spikes_found

         intrinsic maxval,minval,size

         !--- set constants.
         debug      = 0              ! sets debug level (sets what to print)
         iqcflag    = istepflag      ! array index of step test.
         ndts       = size(obs(:,1,ivar))   ! # of hours in d.
         nstnnets   = size(stnnets)  ! # of stations in ndts
         firsttime  = 1              ! first time through loop indicator.
         level1     = suspflag       ! qc "suspect" level for this test.
         level2     = warnflag       ! qc "warning" level for this test.

         !--- if too_many_spikes (hours around which a spike is found) or 
         !--- more are found, flag all ndts worth.
         too_many_spikes = 2; 

         !--- set two maximum absolute steps allowable for each variable,
         !--- one for "suspect" flag and one for "warning" flag.
         select case (var)
         case('t', 'temp', 'tmax', 'tmin', 'td', 'dewp') !--- temperatures
            step1 = 10.0
            step2 = 15.0
            step_3pt = 8.0
         case('gust')                          !--- wind gust
            step1 = 40.0
            step2 = 50.0
         case('rh')                            !--- relative humidity
            step1 = 60.0
            step2 = 80.0
         case('mixr')                          !--- mixing ratio
            step1 =  7.0
            step2 = 10.0
         case('pcpn1')                         !--- precipitation 1-hr
            step1 = 1.0
            step2 = 2.0
         case('slp','sfp')                     !--- sea level pressure
            step1 = 1500.0
            step2 = 2000.0
            step_3pt = 1000.0
         case('spd','wsp')                     !--- wind speed
            step1 = 25.0
            step2 = 35.0
            step_3pt = 15.0
         case('dir','wdir')                    !--- wind direction
            step1 = 361.
            step2 = 361.
         end select

         STNS: do s = 1, nstnnets

            spikes_found = 0

            !--- if station moves, can't fairly do step test on it.
            if (stn_moves(s) .eq. 1) then
               qc_flag(:, s, ivar, iqcflag) = notestflag
               cycle STNS
            end if

            do d = 1, ndts

               !--- no values to compare against in hour 1.
               if (d .eq. 1) then
                  qc_flag(d,s,ivar,iqcflag) = notestflag
               else
                  !--- assuming range check has been performed.  If previous
                  !--- value is mvc (but current value isn't mvc), can't do 
                  !--- step test; assign an notestflag to qcflag.
                  if (qc_flag(d-1,s,ivar,irangeflag) .eq. failflag .or. &
                      qc_flag(d-1,s,ivar,irangeflag) .eq. mflag    .or. &
                      qc_flag(d  ,s,ivar,irangeflag) .eq. failflag .or. &
                      qc_flag(d  ,s,ivar,irangeflag) .eq. mflag) then
                     qc_flag(d,s,ivar,iqcflag) = notestflag
                  else if (qc_flag(d,s,ivar,istepflag) .eq. level1 .or. &
                           qc_flag(d,s,ivar,istepflag) .eq. level2) then
                    !-- do nothing... must have been flagged by 3pt test...
                  else if (abs(obs(d,s,ivar) - obs(d-1,s,ivar)) .gt. step1 &
                     .and. abs(obs(d,s,ivar) - obs(d-1,s,ivar)) .lt. step2)then
                     !--- flag both current time and previous time with
                     !--- "warning" flag.
                     spikes_found = spikes_found + 1
                     qc_flag(d-1,s,ivar,iqcflag) = level1
                     qc_flag(d  ,s,ivar,iqcflag) = level1
                  else if (abs(obs(d,s,ivar) - obs(d-1,s,ivar)) .ge. step2)then
                     !--- flag both current time and previous time with
                     !--- "warning" flag.
                     spikes_found = spikes_found + 1
                     qc_flag(d-1,s,ivar,iqcflag) = level2
                     qc_flag(d  ,s,ivar,iqcflag) = level2
                  else
                     qc_flag(d,s,ivar,iqcflag) = passflag
                  end if

                  !--- New test which looks for smaller spike in wind speed 
                  !--- that is a one hour jump that come back down immediately.
                  if ( (trim(var) .eq. 'spd' .or. &
                        trim(var) .eq. 't'   .or. &
                        trim(var) .eq. 'td'  .or. &
                        trim(var) .eq. 'slp') .and. &
                        d .ne. ndts) then
                     if (qc_flag(d-1,s,ivar,irangeflag) .eq. failflag .or. &
                         qc_flag(d-1,s,ivar,irangeflag) .eq. mflag    .or. &
                         qc_flag(d  ,s,ivar,irangeflag) .eq. failflag .or. &
                         qc_flag(d  ,s,ivar,irangeflag) .eq. mflag    .or. &
                         qc_flag(d+1,s,ivar,irangeflag) .eq. failflag .or. &
                         qc_flag(d+1,s,ivar,irangeflag) .eq. mflag) then
                       !-- do nothing if any of the 3 pts in question are 
                       !-- missing or out of range.
                     else if &
                        (abs(obs(d,s,ivar) - obs(d-1,s,ivar)) .gt. step_3pt &
                        .and. &
                        abs(obs(d,s,ivar) - obs(d+1,s,ivar)) .gt. step_3pt) &
                        then
                        !-- Don't recount this spike if it was already 
                        !-- counted above.
                        if (qc_flag(d,s,ivar,iqcflag) .ne. level1 .and. &
                            qc_flag(d,s,ivar,iqcflag) .ne. level2) then
                           spikes_found = spikes_found + 1
                        end if
                        !-- flag current, previous, and next time with
                        !-- "suspect" flag (lower level flag as this is a
                        !-- new test).
                        qc_flag(d+1,s,ivar,iqcflag) = level1
                        qc_flag(d-1,s,ivar,iqcflag) = level1
                        qc_flag(d  ,s,ivar,iqcflag) = level1
                     end if
                  end if
               end if

               if (debug .eq. 1) then
                  if (firsttime .eq. 1) then 
                     print *,''
                     print *,'Station    hr    obs val  prev val qc_flag' 
                     print *,'-------    --    -------  -------- -------'
                     firsttime = 0
                  end if
 10               format(1x, A8, 3x, i2, 3x, F12.3, 2x, F12.3, 2X, i1)
                  if (qc_flag(d,s,ivar, iqcflag) .eq. 2) then
                     write (*,10), stnnets(s), d, obs(d,s,ivar), &
                        obs(d-1,s,ivar), qc_flag(d,s,ivar,iqcflag)
                  end if
               end if
            end do    !--- end ndts loop...

            !--- if we found >= too_many_spikes, flag the entire day.
            if (spikes_found .ge. too_many_spikes) then
               do d = 1, ndts
                  if (qc_flag(d,s,ivar,iqcflag) .ne. notestflag) then
                     qc_flag(d,s,ivar,iqcflag) = level2
                  end if
               end do
            end if

         end do STNS  !--- end stnnets loop...

      end subroutine step_check

!-----------------------------------------------------------------------------
!--- Persistence Test
!-----------------------------------------------------------------------------

      subroutine persistence_check(obs, stnnets, var, ivar, qc_flag)

         !--- For each station, for a day of data, calculate mean and std
         !--- deviation.  Compare std deviation to set values and if it's too
         !--- small, flag entire day as suspect (1) or warning (2).  Also
         !--- check the difference between subsequent obs and flag if this
         !--- difference is too small.

         real,             dimension(:,:,:),   intent(IN)    :: obs
         character(len=*), dimension(:),       intent(IN)    :: stnnets
         character(len=*),                     intent(IN)    :: var
         integer,                              intent(IN)    :: ivar
         integer,          dimension(:,:,:,:), intent(INOUT) :: qc_flag

         real,    allocatable, dimension(:) :: val
         integer, allocatable, dimension(:) :: vali

         integer :: nstnnets, ndts, min_nobs, level
         integer :: d, s, iqcflag, vcount, deltacount
         integer :: debug, firsttime
         real    :: pdelta, maxdelta
         real    :: mean, sd

         intrinsic maxval,minval,size

         !--- set constants.
         debug     = 0              ! sets debug level (sets what to print)
         iqcflag   = ipersistflag   ! array index of persist test.
         ndts      = size(obs(:,1,ivar))   ! # of dts in obs.
         nstnnets     = size(stnnets)  ! # of stations.
         firsttime = 1              ! first time through loop indicator.
         min_nobs  = 8              ! minimum number of good obs to do 
                                    ! 24-hr std deviation test.
         level     = warnflag       ! qc warning level for this test.

         !--- set "persistence delta" for each variable.
         select case (var)
         case('td', 'dewp')         !--- dew point temperature
            pdelta = 0.1
         case('gust')        !--- wind gust
            pdelta = 0.0
         case('rh')          !--- relative humidity
            pdelta = 0.1
         case('mixr')        !--- mixing ratio
            pdelta = 0.1
         case('pcpn1')       !--- precipitation 1-hr
            pdelta = mvc
         case('slp','sfp')   !--- sea level pressure (in Pa).
            pdelta = 10.0
         case('t', 'temp')   !--- temperature
            pdelta = 0.1
         case('tmax')        !--- max temperature
            pdelta = 0.1
         case('tmin')        !--- min temperature
            pdelta = 0.1
         case('spd','wsp')   !--- wind speed
            pdelta = 0.0
         case('dir','wdir')  !--- wind direction
            pdelta = 0.1
         end select

         !--- For each station, determine # of good obs (individually) 
         !--- for standard deviation and maxdelta portions of the 
         !--- persistence test.  Get maxdelta while we're at it too.
         allocate( vali (ndts))
         allocate( val  (ndts))

         !--- Loop through each station.
         do s = 1, nstnnets

            vcount     = 0
            deltacount = 0
            vali       = mvc
            val        = mvc
            maxdelta   = mvc

            !--- Loop through each dt gathering all non-missing/flagged 
            !--- obs and their indices into 'val' and 'vali' respectively.
            !--- Also determine the 'maxdelta' between successive non-
            !--- missing/flagged obs.
            do d = 1, ndts

               !--- get 'maxdelta' between successive non-missing obs.
               if (d .gt. 1) then
                  !--- assuming range check has been performed.  If previous
                  !--- or current value is mvc (but current value isn't mvc), 
                  !--- don't get a delta.
                  if (qc_flag(d-1,s,ivar,irangeflag) .eq. failflag .or. &
                      qc_flag(d-1,s,ivar,irangeflag) .eq. mflag    .or. &
                      qc_flag(d,  s,ivar,irangeflag) .eq. failflag .or. &
                      qc_flag(d,  s,ivar,irangeflag) .eq. mflag    .or. &
                      obs(d,  s,ivar) .eq. mvc .and. &
                      obs(d-1,s,ivar) .eq. mvc ) then
                      !--- do nothing to maxdelta.
                  else if ( abs(obs(d,s,ivar) - obs(d-1,s,ivar)) .gt. &
                            maxdelta) then

                     !--- both the current and previous values are ok,
                     !--- so get a delta value between them.
                     deltacount = deltacount + 1
                     maxdelta = abs(obs(d,s,ivar) - obs(d-1,s,ivar))

                  end if
               end if

               !--- can't do persistence test if value is missing or 
               !--- out of range.  If value is ok, store it.
               if (qc_flag(d,s,ivar,irangeflag) .eq. failflag   .or. &
                   qc_flag(d,s,ivar,irangeflag) .eq. notestflag .or. &
                   qc_flag(d,s,ivar,irangeflag) .eq. mflag      .or. &
                   obs(d,s,ivar) .eq. mvc) then
                  qc_flag(d,s,ivar,iqcflag) = notestflag
               else
                  !--- count only if value was seen to be ok.
                  vcount       = vcount + 1
                  vali(vcount) = d
                  val(vcount)  = obs(d,s,ivar)
               end if

            end do

            !--- Only do standard deviation portion of persistence test 
            !--- if there's more than 'min_obs' number of non-missing obs.
            if (vcount .ge. min_nobs) then

               !--- get standard deviation of values in val.
               mean = SUM(val(1:vcount) / vcount)
               sd   = SQRT(SUM((val(1:vcount) - mean)**2) / vcount)

               !--- if the maxdelta between any successive obs is too small or
               !--- if stdev is too small, flag all non-missing (vali) values.
               if ( sd .le. pdelta ) then
                  qc_flag(vali(1:vcount),s,ivar,iqcflag) = level
               else
                  !--- Make sure not to stomp on previous persistence tests!
                  where (qc_flag(vali(1:vcount),s,ivar,iqcflag) .ne. level)
                     qc_flag(vali(1:vcount),s,ivar,iqcflag) = passflag
                  end where
               end if

            end if

            !--- Only do maxdelta portion of persistence test if there's 
            !--- more than 'min_obs' number of deltas found ('deltacount')
            !--- for calculating a 'maxdelta'.
            if (deltacount .ge. min_nobs) then
               if ( maxdelta .ne. mvc .and. maxdelta .lt. pdelta ) then
                  !--- Don't flag RH if it's 99-100% (saturated).
                  if (var .eq. 'rh') then
                     if (val(1) .lt. 99.0) then
                        qc_flag(vali(1:vcount),s,ivar,iqcflag) = level
                     end if
                  else
                     qc_flag(vali(1:vcount),s,ivar,iqcflag) = level
                  end if
               else
                  !--- Make sure not to stomp on previous persistence tests!
                  where (qc_flag(vali(1:vcount),s,ivar,iqcflag) .ne. level)
                     qc_flag(vali(1:vcount),s,ivar,iqcflag) = passflag
                  end where
               end if
            end if

            !--- If there wasn't enough good obs to do this the standard
            !--- deviation or maxdelta persistence tests, set flags to
            !--- indeterminate.
            if (vcount .lt. min_nobs .and. deltacount .lt. min_nobs) then
               !--- Make sure not to stomp on previous persistence tests!
               where (qc_flag(vali(1:vcount),s,ivar,iqcflag) .ne. level .and. &
                      qc_flag(vali(1:vcount),s,ivar,iqcflag) .ne. passflag)
                  qc_flag(vali(1:vcount),s,ivar,iqcflag) = notestflag
               end where
            end if

         end do

      end subroutine persistence_check

!-----------------------------------------------------------------------------
!--- Spatial Test
!-----------------------------------------------------------------------------

      subroutine spatial_check(obs, stnnets, lat, lon, elev, var, ivar, &
         qc_flag)

      !--- spatial_check does does a spatial QC test using a simple
      !--- neighbor check whereby it looks at stations within a radius and
      !--- elevation band and checks if at least one value is near the
      !--- value in question.  If not, it tries a bigger radius and checks
      !--- again, and if not again, the value is flagged.
      !---
      !--- obs        data array with dimensions hrs, variables, stations, 
      !--- stnnets    character array of station names and netids
      !--- lat        station latitude for each station in d array.
      !--- lon        station longitude for each station in d array.
      !--- elev       station elevation for each station in d array.
      !--- var        character string name of the variable
      !--- ivar       array index of d for the variable in question
      !--- qc_flag    array of incoming/outgoing quality control flags.

      !-- changing values of d for zeroing traces -- can't define 'IN' intent.
      real,             dimension(:,:,:)                  :: obs
      character(len=*), dimension(:),       intent(IN)    :: stnnets
      real,             dimension(:,:),     intent(IN)    :: lat
      real,             dimension(:,:),     intent(IN)    :: lon
      real,             dimension(:,:),     intent(IN)    :: elev
      character(len=*),                     intent(IN)    :: var
      integer,                              intent(IN)    :: ivar
      integer,          dimension(:,:,:,:), intent(INOUT) :: qc_flag

      integer :: d, s, ss, nstnnets, ndts, level1, level2
      integer :: min_stations, debug, val2i
      integer :: found_onesm1, found_onesm2, found_onebg1
      integer :: countemsm, countembg, countemall
      real    :: max_elev_diff, elev_diff, maxvdiff1, maxvdiff2
      real    :: dist, roism, roibg, latdiff, londiff, obsdiff
      real    :: mindiffsm, mindiffbg

      character(len=2), allocatable, dimension(:) :: netids

      real, allocatable, dimension(:) :: valsm, valbg
      real, allocatable, dimension(:) :: val2sm, val2bg

      intrinsic maxval,minval,size

      !--- Settings appropriate for all variables.
      debug         = 0                ! sets debug level (sets what to print)
      nstnnets      = size(stnnets)    ! get # of stations in obs.
      ndts          = size(obs(:,1,1)) ! # of hours in obs.
      roism         = 100.0            ! smaller radius of influence.
      roibg         = 150.0            ! bigger radius of influence.
      min_stations  = 2                ! min # of stns needed for testing.
      level1        = suspflag         ! "suspect" flag.
      level2        = warnflag         ! "warning" flag.
      latdiff       = 3.0
      londiff       = 3.0
      
      !--- pull netids out of the stnnets.
      allocate(netids(nstnnets))
      netids = stnnets(:)(7:8)

      !--- Variable-specific settings.
      select case (var)
         case('slp', 'sfp')                   !--- pressure
            maxvdiff1     =  750.0 ! max diff for simple neighbor test.
            maxvdiff2     = 1000.0 ! max diff for simple neighbor test.
            max_elev_diff = 1000.0 ! max elev diff between stations in roi.
            val2i         = int(mvc)
         case('t', 'td', 'temp', 'tmax', 'tmin', 'dewp') !--- temperatures
            maxvdiff1     = 5.556 ! max diff for simple neighbor test (10degF).
            maxvdiff2     = 8.333 ! max diff for simple neighbor test (15degF).
            max_elev_diff = 150.0 ! max elev diff between stations in roi.
            val2i         = int(mvc)
         case('spd', 'wsp')                   !--- wind speed
            maxvdiff1     = 7.65 ! mx spd diff for simple neighbor test (15kts)
            maxvdiff2     = 10.2 ! mx spd diff for simple neighbor test (20kts)
            max_elev_diff = 250.0 ! max elev diff between stations in roi.
            val2i         = int(mvc)
         case('dir', 'wdir')                  !--- wind direction
            maxvdiff1     = 360.0 ! max spd diff 1 for simple neighbor test.
            maxvdiff2     = 360.0 ! max spd diff 2 for simple neighbor test.
            max_elev_diff = 250.0 ! max elev diff between stations in roi.
            val2i         = int(mvc) !ispd
         case('rh')                           !--- relative humidity
            maxvdiff1     = 75.0  ! max diff 1 for simple neighbor test.
            maxvdiff2     = 85.0  ! max diff 2 for simple neighbor test.
            max_elev_diff = 250.0 ! max elev diff between stations in roi.
            val2i         = int(mvc)
         case('pcp6')                         !--- 6-hr precip
            maxvdiff1     = 76.2  ! max diff 1 (mm; eq 3 inches).
            maxvdiff2     = 101.6 ! max diff 2 (mm; eq 4 inches).
            max_elev_diff = 500.0 ! max elev diff between stations in roi.
            val2i         = int(mvc)
         case('pcp24')                        !--- 24-hr precip.
            maxvdiff1     = 152.4 ! max diff 1 (mm; eq 6 inches).
            maxvdiff2     = 203.2 ! max diff 2 (mm; eq 8 inches).
            max_elev_diff = 500.0 ! max elev diff between stations in roi.
            val2i         = int(mvc)
      end select

      allocate( valsm  (nstnnets) )
      allocate( val2sm (nstnnets) )
      allocate( valbg  (nstnnets) )
      allocate( val2bg (nstnnets) )

      !--- If variable is precip, look for traces make them 0.0 (not 
      !--- permanently as these data values don't get sent back out).
      !if (index(var, 'pcp')) then
      if (index(var, 'pcp') .gt. 0) then
         do d = 1, ndts
            do s = 1, nstnnets
               if (obs(d,s,ivar) .eq. trace) then
                  obs(d,s,ivar) = 0.0
               end if
            end do
         end do
      end if

      !--- Cliff's simple similar neighbor test.
      do d = 1, ndts

         if (debug .ne. 0) then 
            print *,'dt: ', d
         end if

         do s = 1, nstnnets

            !--- Skip this station/obs if it's mvc, or elevation is 
            !--- missing, or if it's a buoy, coastal or ship obs (but not
            !--- for s.l.pressure).
            if (obs(d,s,ivar) .eq. mvc .or. &
                elev(d,s)     .eq. mvc .or. &
                qc_flag(d,s,ivar,irangeflag) .eq. failflag) then
               qc_flag(d,s,ivar,ispatialflag) = notestflag
            elseif ((var .ne. 'slp')     .and. &
                    (netids(s) .eq. 'BF' .or. &
                     netids(s) .eq. 'CM' .or. &
                     netids(s) .eq. 'SS') ) then
                qc_flag(d,s,ivar,ispatialflag) = notestflag
            else
               found_onesm1 = 0
               found_onesm2 = 0
               found_onebg1 = 0
               countembg = 0
               countemsm = 0
               !--- for each station, check it versus every other station 
               !--- (except itself).  First time through get # of stations 
               !--- within radius of influence to determine if we can do
               !--- this test.
               do ss = 1, nstnnets

                  !--- skip station for any of the following reasons:  same
                  !--- station as 's' (ss.eq.s), it's not within a lat/lon box
                  !--- defined by latdiff/long diff, the value is mvc, 
                  !--- the value has been flagged in other tests, or the 
                  !--- elevation data is mvc.
                  if ( obs(d,ss,ivar) .eq. mvc ) cycle
                  if ( elev(d,ss)     .eq. mvc ) cycle
                  if ( lat(d,ss)      .eq. mvc ) cycle 
                  if ( lon(d,ss)      .eq. mvc ) cycle 
                  if ( abs(lat(d,ss) - lat(d,s) )   .gt. latdiff) cycle
                  if ( abs(lon(d,ss) - lon(d,s) )   .gt. londiff) cycle
                  if ( abs(elev(d,ss) - elev(d,s) ) .gt. max_elev_diff) cycle 
                  if ( qc_flag(d,ss,ivar,irangeflag)   .eq. failflag )  cycle
                  if ( qc_flag(d,ss,ivar,istepflag)    .eq. suspflag )  cycle
                  if ( qc_flag(d,ss,ivar,istepflag)    .eq. warnflag )  cycle
                  if ( qc_flag(d,ss,ivar,ipersistflag) .eq. suspflag )  cycle
                  if ( qc_flag(d,ss,ivar,ipersistflag) .eq. warnflag )  cycle
                  if ( ss .eq. s )  cycle

                  call distance(lat(d,s),lon(d,s), lat(d,ss),lon(d,ss), dist)

                  obsdiff = abs(obs(d,ss,ivar) - obs(d,s,ivar))

                  if (dist .lt. roism) then
                     countemsm = countemsm + 1
                     valsm(countemsm) = obsdiff
                     if (val2i .ne. int(mvc)) then
                        val2sm(countemsm) = obs(d,ss,val2i)
                     end if
                  elseif (dist .lt. roibg) then
                     countembg = countembg + 1
                     valbg(countembg) = obsdiff
                     if (val2i .ne. int(mvc)) then
                        val2bg(countemsm) = obs(d,ss,val2i)
                     end if
                  end if

               end do

               !--- If any obs found in roi was <= maxvdiff1, it's a
               !--- pass.  If none found <= maxvdiff1, but one 
               !--- is >= maxvdiff1 & < maxvdiff2, it's a "suspect."  
               !--- Otherwise it's a "warning."  Look in big roi too.
               if (countemsm .ge. min_stations) then 

                  mindiffsm = minval(valsm(1:countemsm))

                  if (mindiffsm .le. maxvdiff1) then
                     qc_flag(d,s,ivar,ispatialflag) = passflag               
                  else if (mindiffsm .gt. maxvdiff1 .and. &
                           mindiffsm .le. maxvdiff2) then
                     qc_flag(d,s,ivar,ispatialflag) = level1
                  else
                     qc_flag(d,s,ivar,ispatialflag) = level2
                  end if
               elseif (countemsm .lt. min_stations .and. &
                       countembg .ge. min_stations) then

                  mindiffbg = minval(valbg(1:countembg))

                  if (mindiffbg .le. maxvdiff2) then
                     qc_flag(d,s,ivar,ispatialflag) = passflag
                  else
                     qc_flag(d,s,ivar,ispatialflag) = level1
                  end if
               else
                  !--- not enough obs in either roi to do test.
                  qc_flag(d,s,ivar,ispatialflag) = notestflag
               end if

            end if
         end do   !--- stations do loop.
      end do      !--- dates do loop.

      end subroutine spatial_check

!-----------------------------------------------------------------------------
!--- Spatial Test for Wind Direction
!-----------------------------------------------------------------------------

      subroutine spatial_check_dir(obs, dts, stnnets, lat, lon, elev, &
         var, ivar, &
         qc_flag, roi_data_file)

      !--- spatial_check_dir does does a spatial QC test on wind direction
      !--- by gathering the closest 'min_stations' stations within a 
      !--- radius 'roi' and calculating a vector average spd and dir from 
      !--- those stations, and if the dir from the station in question is 
      !--- more than 'dir_diff' degrees from the vector average, the 
      !--- station's dir is flagged.
      !---
      !--- obs        data array with dimensions hrs, variables, stations, 
      !--- stnnets    character array of station names and netids
      !--- lat        station latitude for each station in d array.
      !--- lon        station longitude for each station in d array.
      !--- elev       station elevation for each station in d array.
      !--- var        character string name of the variable
      !--- ivar       array index of d for the variable in question
      !--- qc_flag    array of incoming/outgoing quality control flags.

      !-- changing values of d for zeroing traces -- can't define 'IN' intent.
      real,              dimension(:,:,:)                  :: obs
      character(len=10), dimension(:),       intent(IN)    :: dts
      character(len=*),  dimension(:),       intent(IN)    :: stnnets
      real,              dimension(:,:),     intent(IN)    :: lat
      real,              dimension(:,:),     intent(IN)    :: lon
      real,              dimension(:,:),     intent(IN)    :: elev
      character(len=*),                      intent(IN)    :: var
      integer,                               intent(IN)    :: ivar
      integer,           dimension(:,:,:,:), intent(INOUT) :: qc_flag
      character(len=*) ,                     intent(IN)    :: roi_data_file

      integer :: d, i, n, s, ss, nstnnets, ndts
      integer :: min_stations, debug, level1, level2
      integer :: found_one, countem_sm, countem_bg
      integer :: print_roi_data
      real    :: max_elev_diff, elev_diff, maxvdiff1, maxvdiff2
      real    :: dist, roi_sm, roi_bg, latdiff, londiff, dir_diff
      real    :: dir_thresh, spd_thresh, spd_thresh_roi, min_diff

      character(len=10) :: dt_c

      character(len=2), allocatable, dimension(:) :: netids

      real,             allocatable, dimension(:) :: roi_dist
      real,             allocatable, dimension(:) :: roi_spd
      real,             allocatable, dimension(:) :: roi_dir
      real,             allocatable, dimension(:) :: roi_lat
      real,             allocatable, dimension(:) :: roi_lon
      real,             allocatable, dimension(:) :: roi_elev
      character(len=8), allocatable, dimension(:) :: roi_stnnets

      real,    allocatable, dimension(:) :: dist_sort
      integer, allocatable, dimension(:) :: isort

      intrinsic maxval,minval,size

      !--- Settings appropriate for all variables.
      debug          = 0                ! sets debug level (sets what to print)
      print_roi_data = 1
      nstnnets       = size(stnnets)    ! get # of stations in obs.
      ndts           = size(obs(:,1,1)) ! # of hours in obs.
      min_stations   = 5                ! min # of stns needed for testing.
      roi_sm         = 50               ! small radius for dir qc test.
      roi_bg         = 75               ! big radius for dir qc test.
      dir_thresh     = 85               ! diff in dir required for flagging.
      spd_thresh     = 2.5722           ! spd_thresh for station in question.
      spd_thresh_roi = 0.5144           ! spd_thresh for stations in roi.
      level1         = suspflag         ! "suspect" flag.
      level2         = warnflag         ! "warning" flag.
      latdiff        = 3.0              ! to speed up station finding...
      londiff        = 3.0              ! to speed up station finding...
      max_elev_diff  = 99999999.0       ! for now, allow any elevations.

      !--- pull netids out of the stnnets.
      allocate(netids(nstnnets))
      netids = stnnets(:)(7:8)

      allocate( roi_dist    (nstnnets) )
      allocate( roi_spd     (nstnnets) )
      allocate( roi_dir     (nstnnets) )
      allocate( roi_stnnets (nstnnets) )
      allocate( roi_lat     (nstnnets) )
      allocate( roi_lon     (nstnnets) )
      allocate( roi_elev    (nstnnets) )

      !--- Loop through each date.
      do d = 1, ndts

         dt_c = dts(d)

         !--- Loop through each station.
         do s = 1, nstnnets

            !--- Skip this station/obs if it's mvc, or if the speed is
            !--- below 'spd_thresh'.  Since as of 1/16/2007 many obs
            !--- have bad elevation data, NOT skipping if this is missing
            !--- (probably change this when station elevation data gets
            !--- fixed by Dave Carey).
            if (obs(d,s,ispd) .lt. spd_thresh .or. &
                obs(d,s,ispd) .eq. mvc .or. &
                obs(d,s,idir) .eq. mvc .or. &
                obs(d,s,iu)   .eq. mvc .or. &
                obs(d,s,iv)   .eq. mvc .or. &
                qc_flag(d,s,ispd,irangeflag) .eq. failflag .or. &
                qc_flag(d,s,idir,irangeflag) .eq. failflag) then
               qc_flag(d,s,ivar,ispatialflag) = notestflag
               cycle
            end if

            found_one = 0
            countem_sm   = 0
            countem_bg   = 0
            !--- for each station, check it versus every other station 
            !--- (except itself).  First time through get # of stations 
            !--- within radius of influence to determine if we can do
            !--- this test.
            do ss = 1, nstnnets

               !--- skip station for any of the following reasons:  same
               !--- station as 's' (ss.eq.s), it's not within a lat/lon box
               !--- defined by latdiff/long diff, the value is mvc, 
               !--- the value has been flagged in other tests, or the 
               !--- elevation data is mvc.
               if ( abs(lat(d,ss) - lat(d,s) ) .gt. latdiff) cycle
               if ( abs(lon(d,ss) - lon(d,s) ) .gt. londiff) cycle
               if ( obs(d,ss,ispd) .eq. mvc ) cycle
               if ( obs(d,ss,idir) .eq. mvc ) cycle
               if ( obs(d,ss,iu)   .eq. mvc ) cycle
               if ( obs(d,ss,iv)   .eq. mvc ) cycle
               if ( lat(d,ss)      .eq. mvc ) cycle 
               if ( lon(d,ss)      .eq. mvc ) cycle 
               if ( obs(d,ss,ispd) .lt. spd_thresh_roi ) cycle
               if ( abs(elev(d,ss) - elev(d,s) ) .gt. max_elev_diff) cycle 
               if ( qc_flag(d,ss,ivar,irangeflag)   .eq. failflag )  cycle
               if ( qc_flag(d,ss,ivar,istepflag)    .eq. suspflag )  cycle
               if ( qc_flag(d,ss,ivar,istepflag)    .eq. warnflag )  cycle
               if ( qc_flag(d,ss,ivar,ipersistflag) .eq. suspflag )  cycle
               if ( qc_flag(d,ss,ivar,ipersistflag) .eq. warnflag )  cycle
               if ( ss .eq. s )  cycle

               call distance(lat(d,s),lon(d,s), lat(d,ss),lon(d,ss), dist)

               !--- Only add up number of stations in small roi, and keep
               !--- around values in big roi.
               if (dist .le. roi_sm) then
                  countem_sm = countem_sm + 1
               end if
               if (dist .le. roi_bg) then
                  countem_bg = countem_bg + 1
                  roi_dist(countem_bg) = dist
                  roi_spd(countem_bg) = obs(d,ss,ispd)
                  roi_dir(countem_bg) = obs(d,ss,idir)
                  roi_stnnets(countem_bg) = stnnets(ss)
                  roi_lat(countem_bg) = lat(d,ss)
                  roi_lon(countem_bg) = lon(d,ss)
                  roi_elev(countem_bg) = elev(d,ss)
               end if

            end do

            !--- if there's enough good stations in small roi, expand to big
            !--- roi and use data from it.
            if (countem_sm .ge. min_stations .and. &
                countem_bg .ge. min_stations) then 

               !--- calculate the minimum difference between the direction
               !--- in question and the obs in the roi.
               min_diff = 9999.0
               do i = 1, countem_bg
!                  call ndir_diff(dir_diff, roi_dir(i), obs(d,s,idir))
                  if (dir_diff .lt. min_diff) then
                     min_diff = dir_diff
                  end if
               end do

               !--- if vector average speed as well as the station in 
               !--- question's speed is high enough and the direction is
               !--- different enough from the vector average, flag it.
               if (min_diff .gt. dir_thresh) then
                  qc_flag(d,s,ivar,ispatialflag) = warnflag

                  !--- if set, print out station and roi stations data.
 17               format(i1,',', a10, ',', a8, ',', 4(f12.3,','), f12.3)
                  if (print_roi_data .eq. 1) then
                     open(unit=100, file=trim(roi_data_file), &
                        position="append")
                     write(100,17) 1, dt_c, &
                        stnnets(s),elev(d,s),lat(d,s),&
                        lon(d,s), obs(d,s,idir), obs(d,s,ispd)
                     do i = 1, countem_bg
                        write(100,17) 0, dt_c, &
                           roi_stnnets(i), roi_elev(i), &
                           roi_lat(i), roi_lon(i), &
                           roi_dir(i), roi_spd(i)
                     end do
                     close(100)
                  end if
               end if

            else

               !--- not enough obs in roi to do test.
               qc_flag(d,s,ivar,ispatialflag) = notestflag

            end if

         end do   !--- stations do loop.
      end do      !--- dates do loop.

      end subroutine spatial_check_dir

!-----------------------------------------------------------------------------
!--- Distance subroutine
!-----------------------------------------------------------------------------

      subroutine distance(lat1, lon1, lat2, lon2, d)

         real, intent(IN)   :: lat1, lon1, lat2, lon2
         real, intent(OUT)  :: d

         real               :: lat1_r, lon1_r, lat2_r, lon2_r
         real               :: pi, theta, theta_r, dist, dist_temp

         intrinsic acos, atan2, cos, sin, sqrt

         pi = atan2(0.0, -1.0)

         theta = lon1 - lon2

         lat1_r = lat1 * (pi/180.)
         lon1_r = lon1 * (pi/180.)
         lat2_r = lat2 * (pi/180.)
         lon2_r = lon2 * (pi/180.)
         theta_r = theta * (pi/180.)

         dist = acos(sin(lat1_r) * sin(lat2_r) + cos(lat1_r) * cos(lat2_r) *&
            cos(theta_r))

         dist_temp = (dist * (180./pi)) * 60 * 1.1515

         !--- only returning in km units for now.
         d = dist_temp * 1.609344

      end subroutine distance

      
      end module qc 
