from math import atan2, acos, cos, sin

nqcflags = 9  # total number of qc flags
passflag = 0  # "pass" qc value.
suspflag = 1  # "suspect" qc value.
warnflag = 2  # "warning" qc value.
failflag = 3  # "failed" qc value.
notestflag = 8  # "not-tested" qc value.
mflag = 9  # "missing" qc value.

irangeflag = 0  # index for range test qc flag.
istepflag = 1  # index for step test qc flag.
ipersistflag = 2  # index for persistence test flag.
ispatialflag = 3  # index for spatial test qc flag.

mvc = -888888.0
obsmvc = -888888.0
trace = -666666.0

ispd = 1
idir = 1
iu = 1
iv = 1


def range_check(obs, nstnnets, var, ivar, qc_flag):

    iqcflag = irangeflag
    ndts = len(obs[:, 0, ivar])  # nr of hours in d.

    allowed_range = {
        'temp': (225, 323),
        'dew': (225, 323),
        'wind_dir': (0, 360),
        'wind_speed': (0, 60),
        'wind_gust': (0, 70),
        'pressure': (80000, 107840),  # Pa, not hPa!
        'rel_hum': (0, 105),

        # let's keep the values for variables we don't have (yet?)
        'mixr': (0, 25),
        'pcp6': (0, 256),
        'pcp24': (0, 508)
    }

    try:
        minrange, maxrange = allowed_range[var]
    except KeyError:
        raise ValueError('Cannot recognize variable type')

    for d in range(ndts):  # timestamps
        for s in range(nstnnets):  # stations
            if obs[d, s, ivar] == mvc:
                qc_flag[d, s, ivar, iqcflag] = mflag
                continue

            if obs[d, s, ivar] < minrange or obs[d, s, ivar] > maxrange:
                # Don't flag traces for precip!
                qc_flag[d, s, ivar, iqcflag] = passflag if var == 'pcp' and obs == trace else failflag
            else:
                qc_flag[d, s, ivar, iqcflag] = passflag


def test_temp_vs_dew(obs, nstnnets, var, ivar, qc_flag):
    # If there is both temp and tdew and after we made all the tests.
    td_gt_t_tol = 2.0  # tolerance for dew point being > temperature.
    iqcflag = irangeflag  # array index of range test.
    ndts = len(obs[:, 0, ivar])  # nr of hours in d.

    it = 0  # index temp
    itd = 0  # index temp dew

    for d in range(ndts):  # timestamps
        for s in range(nstnnets):  # stations
            if qc_flag[d, s, ivar, iqcflag] == passflag:
                # !--- if this is temperature or dew point, make sure dew point
                # !--- is not greater than temperature (by 'td_gt_t_tol').
                if var in ['t', 'temp', 'td', 'dewp']:

                    if obs[d, s, itd] != mvc and obs[d, s, it] != mvc and obs[d, s, itd] - obs[d, s, it] > td_gt_t_tol:
                        qc_flag[d, s, it, iqcflag] = 2
                        qc_flag[d, s, itd, iqcflag] = 2  # why hardcoded 2? warnflag


def step_check(obs, nstnnets, var, ivar, qc_flag):
    """
    Perform "delta test" which, for each station checks each hour
    in a day, checks for jumps between consecutive observations
    that exceed a given threshold.
    """

    iqcflag = istepflag
    ndts = len(obs[:, 0, ivar])   # # of hours in d.

    level1 = suspflag
    level2 = warnflag

    # if too_many_spikes (hours around which a spike is found) or more are found, flag all ndts worth.
    too_many_spikes = 2

    # set two maximum absolute steps allowable for each variable, one for "suspect" flag and one for "warning" flag.
    steps = {
        'temp': (10.0, 15.0, 8.0),
        'dew': (10.0, 15.0, 8.0),
        'wind_gust': (40.0, 50.0, None),
        'rel_hum': (60.0, 80.0, None),
        'pressure': (1500.0, 2000.0, 1000.0),
        'wind_speed': (25.0, 35.0, 15.0),
        'wind_dir': (361., 361., None),

        'mixr': (7.0, 10.0, None),
        'pcpn1': (1.0, 2.0, None),
    }

    try:
        step1, step2, step_3pt = steps[var]
    except KeyError:
        raise ValueError('Unrecognized variable')

    for s in range(nstnnets):
        spikes_found = 0
        for d in range(ndts):
            if d == 0:
                qc_flag[d, s, ivar, iqcflag] = notestflag
                continue

            # FIRST SET OF TESTS
            if qc_flag[d-1, s, ivar, irangeflag] in [failflag, mflag] or qc_flag[d, s, ivar, irangeflag] in [failflag, mflag]:
                qc_flag[d, s, ivar, iqcflag] = notestflag
            elif qc_flag[d, s, ivar, istepflag] in [level1, level2]:
                pass  # do nothing... must have been flagged by 3pt test for the previous d.

            elif step1 < abs(obs[d, s, ivar] - obs[d-1, s, ivar]) < step2:  # flag current and previous time with susp
                spikes_found += 1
                qc_flag[d-1, s, ivar, iqcflag] = level1
                qc_flag[d, s, ivar, iqcflag] = level1
            elif abs(obs[d, s, ivar] - obs[d-1, s, ivar]) >= step2:  # flag current and previous time with warning
                spikes_found += 1
                qc_flag[d-1, s, ivar, iqcflag] = level2
                qc_flag[d, s, ivar, iqcflag] = level2
            else:
                qc_flag[d, s, ivar, iqcflag] = passflag

            # New test which looks for smaller spike in windspeed that is a 1 hour jump that come back down immediately
            # not implemented?

            # SECOND SET OF TESTS
            # if (var in ['spd', 't', 'td', 'slp']) and d != ndts - 1:  # our code never enters there although it should
            if var in ['wind_speed', 'temp', 'dew', 'pressure'] and d != ndts - 1:
                if (qc_flag[d-1, s, ivar, irangeflag] in [failflag, mflag] or
                   qc_flag[d, s, ivar, irangeflag] in [failflag, mflag] or
                   qc_flag[d+1, s, ivar, irangeflag] in [failflag, mflag]):
                    pass
                    # do nothing if any of the 3 pts in question are missing or out of range.

                elif abs(obs[d, s, ivar] - obs[d-1, s, ivar]) > step_3pt and abs(obs[d, s, ivar] - obs[d+1, s, ivar]) > step_3pt:
                    # !-- Don't recount this spike if it was already counted above.
                    if qc_flag[d, s, ivar, iqcflag] not in [level1, level2]:
                        spikes_found += 1

                    # flag current, previous, and next time with "suspect" flag (lower level flag as this is a new test)
                    qc_flag[d+1, s, ivar, iqcflag] = level1
                    qc_flag[d-1, s, ivar, iqcflag] = level1
                    qc_flag[d, s, ivar, iqcflag] = level1

        if spikes_found >= too_many_spikes:
            for d in range(ndts):
                if qc_flag[d, s, ivar, iqcflag] != notestflag:
                    qc_flag[d, s, ivar, iqcflag] = level2


def persistence_check(obs, nstnnets, var, ivar, qc_flag):

    """
    For each station, for a day of data, calculate mean and std
    deviation.  Compare std deviation to set values and if it's too
    small, flag entire day as suspect (1) or warning (2).  Also
    check the difference between subsequent obs and flag if this
    difference is too small.

    """

    iqcflag = ipersistflag
    ndts = len(obs[:, 0, ivar])  # number of dts in obs.
    min_nobs = 8  # minimum number of good obs to do 24-hr std deviation test.
    level = warnflag

    pdeltas = {
        'dew': 0.1,
        'wind_gust': 0.0,
        'rel_hum': 0.1,
        'mixr': 0.1,
        'pcpn1': mvc,
        'pressure': 10.0,
        'temp': 0.1,
        'wind_speed': 0.0,
        'wind_dir': 0.1
    }
    try:
        pdelta = pdeltas[var]
    except KeyError:
        raise ValueError('Unrecognized variable')

    # For each station, determine # of good obs (individually) for standard deviation and maxdelta portions of the
    # persistence test. Get maxdelta while we're at it too.

    for s in range(nstnnets):
        deltacount = 0
        vali = []
        val = []
        maxdelta = mvc

        # Loop through each dt gathering all non-missing/flagged obs
        # and their indices into 'val' and 'vali' respectively.
        # Also determine the 'maxdelta' between successive non-missing/flagged obs.
        for d in range(ndts):
            # get 'maxdelta' between successive non-missing obs.
            if d > 0:
                # assuming range check has been performed.
                if (qc_flag[d-1, s, ivar, irangeflag] in [failflag, mflag] or
                   qc_flag[d, s, ivar, irangeflag] in [failflag, mflag] or
                   obs[d, s, ivar] == mvc and obs[d-1, s, ivar] == mvc):
                    pass  # do nothing to maxdelta.
                elif abs(obs[d, s, ivar] - obs[d - 1, s, ivar]) > maxdelta:
                    # both the current and previous values are ok, so get a delta value between them.
                    deltacount += 1  # TODO this depends on when would the highest delta show up!
                    maxdelta = abs(obs[d, s, ivar] - obs[d-1, s, ivar])

            if qc_flag[d, s, ivar, irangeflag] in [failflag, notestflag, mflag] or obs[d, s, ivar] == mvc:
                qc_flag[d, s, ivar, iqcflag] = notestflag
            else:
                vali.append(d)
                val.append(obs[d, s, ivar])

        # Only do standard deviation portion of test if there's more than 'min_obs' number of non-missing obs.
        if len(val) >= min_nobs:
            mean = sum(val) / len(val)
            sd = (sum([(v - mean) ** 2 for v in val]) / len(val))

            # if the maxdelta between any successive obs is too small or if stdev is too small,
            # flag all non-missing (vali) values.

            if sd <= pdelta:
                qc_flag[vali, s, ivar, iqcflag] = level
            else:
                for idx in vali:  # Make sure not to stomp on previous persistence tests!  # TODO how could we?
                    if qc_flag[idx, s, ivar, iqcflag] != level:
                        qc_flag[idx, s, ivar, iqcflag] = passflag

        # Only do maxdelta portion of test if there's more than 'min_obs' number of deltas found ('deltacount')
        # for calculating a 'maxdelta'.
        if deltacount >= min_nobs:
            if maxdelta != mvc and maxdelta < pdelta:
                if var != 'rel_hum' or val[0] < 99.0:  # Don't flag RH if it's 99-100% (saturated). # still unclear why they took only the first value
                    qc_flag[vali, s, ivar, iqcflag] = level

            else:
                for idx in vali:
                    if qc_flag[idx, s, ivar, iqcflag] != level:
                        qc_flag[idx, s, ivar, iqcflag] = passflag

        #  If there wasn't enough good obs to do this the stddev or maxdelta tests, set flags to indeterminate.
        if len(vali) < min_nobs and deltacount < min_nobs:
            for idx in vali:  # Make sure not to stomp on previous persistence tests!
                if qc_flag[idx, s, ivar, iqcflag] != level and qc_flag[idx, s, ivar, iqcflag] != passflag:
                    qc_flag[idx, s, ivar, iqcflag] = notestflag


def spatial_check(obs, nstnnets, lat, lon, elev, var, ivar, qc_flag):

    """
    Spatial_check does does a spatial QC test using a simple neighbor check whereby it looks at stations within a radius
    and elevation band and checks if at least one value is near the value in question. If not, it tries a bigger radius
    and checks again, and if not again, the value is flagged.
    """

    ndts = len(obs[:, 0, 0])  # number of hours in obs.
    roism = 100.0  # smaller radius of influence.
    roibg = 150.0  # bigger radius of influence.
    min_stations = 2  # min # of stns needed for testing.
    level1 = suspflag
    level2 = warnflag
    latdiff = 3.0
    londiff = 3.0

    thresholds = {
        'pressure': (750.0, 1000.0, 1000.0),
        'temp': (5.556, 8.333, 150.0),  # (10degF), (15degF)
        'dew': (5.556, 8.333, 150.0),  # (10degF), (15degF)
        'wind_speed': (7.65, 10.2, 250.0),  # (15kts), (20kts)
        'wind_dir': (360.0, 360.0, 250.0),
        'rel_hum': (75.0, 85.0, 250.0),

        'pcp6': (76.2, 101.6, 500.0), # (mm; eq 3 inches), (mm; eq 4 inches)
        'pcp24': (152.4, 203.2, 500.0),  # (mm; eq 6 inches), (mm; eq 8 inches).
    }

    try:
        maxvdiff1, maxvdiff2, max_elev_diff = thresholds[var]
    except KeyError:
        raise ValueError('Unrecognized variable')

    # If variable is precip, look for traces make them 0.0 (not permanently as these data values don't get sent back out)
    if var == 'pcp':
        for d in range(ndts):
            for s in range(nstnnets):
                if obs[d, s, ivar] == trace:
                    obs[d, s, ivar] = 0.0  # obs[:,:,ivar]...

    # Cliff's simple similar neighbor test.

    for d in range(ndts):
        for s in range(nstnnets):
            if obs[d, s, ivar] == mvc or elev[d, s] == mvc or qc_flag[d, s, ivar, irangeflag] == failflag:
                qc_flag[d, s, ivar, ispatialflag] = notestflag
                continue

            valsm2 = []
            valbg2 = []

            # for each station, check it versus every other station (except itself). First time through get # of
            # stations within radius of influence to determine if we can do this test.
            for ss in range(nstnnets):
                if ss == s or obs[d, ss, ivar] == mvc \
                        or elev[d, ss] == mvc or lat[d, ss] == mvc or lon[d, ss] == mvc \
                        or abs(lat[d, ss] - lat[d, s]) > latdiff or abs(lon[d, ss] - lon[d, s]) > londiff \
                        or abs(elev[d, ss] - elev[d, s]) > max_elev_diff:
                    continue
                if qc_flag[d, ss, ivar, irangeflag] == failflag \
                        or qc_flag[d, ss, ivar, istepflag] in [suspflag, warnflag] \
                        or qc_flag[d, ss, ivar, ipersistflag] in [suspflag, warnflag]:
                    continue

                dist = distance(lat[d, s], lon[d, s], lat[d, ss], lon[d, ss])
                obsdiff = abs(obs[d, ss, ivar] - obs[d, s, ivar])

                if dist < roism:
                    valsm2.append(obsdiff)

                elif dist < roibg:
                    valbg2.append(obsdiff)

            # !--- If any obs found in roi was <= maxvdiff1, it's a pass. If none found <= maxvdiff1,
            # but one is >= maxvdiff1 & < maxvdiff2, it's "suspect." Otherwise it's "warning."  Look in big roi too.
            if len(valsm2) >= min_stations:
                mindiffsm = min(valsm2)
                if mindiffsm <= maxvdiff1:
                    qc_flag[d, s, ivar, ispatialflag] = passflag
                elif maxvdiff1 < mindiffsm <= maxvdiff2:
                    qc_flag[d, s, ivar, ispatialflag] = level1
                else:
                    qc_flag[d, s, ivar, ispatialflag] = level2
            elif len(valsm2) < min_stations <= len(valbg2):
                qc_flag[d, s, ivar, ispatialflag] = passflag if min(valbg2) <= maxvdiff2 else level1

            else:  # not enough obs in either roi to do test.
                qc_flag[d, s, ivar, ispatialflag] = notestflag


#
# !-----------------------------------------------------------------------------
# !--- Spatial Test for Wind Direction
# !-----------------------------------------------------------------------------
#
#       subroutine spatial_check_dir(obs, dts, stnnets, lat, lon, elev, &
#          var, ivar, &
#          qc_flag, roi_data_file)
#
#       !--- spatial_check_dir does does a spatial QC test on wind direction
#       !--- by gathering the closest 'min_stations' stations within a
#       !--- radius 'roi' and calculating a vector average spd and dir from
#       !--- those stations, and if the dir from the station in question is
#       !--- more than 'dir_diff' degrees from the vector average, the
#       !--- station's dir is flagged.
#       !---
#       !--- obs        data array with dimensions hrs, variables, stations,
#       !--- stnnets    character array of station names and netids
#       !--- lat        station latitude for each station in d array.
#       !--- lon        station longitude for each station in d array.
#       !--- elev       station elevation for each station in d array.
#       !--- var        character string name of the variable
#       !--- ivar       array index of d for the variable in question
#       !--- qc_flag    array of incoming/outgoing quality control flags.
#
#       !-- changing values of d for zeroing traces -- can't define 'IN' intent.
#       real,              dimension(:,:,:)                  :: obs
#       character(len=10), dimension(:),       intent(IN)    :: dts
#       character(len=*),  dimension(:),       intent(IN)    :: stnnets
#       real,              dimension(:,:),     intent(IN)    :: lat
#       real,              dimension(:,:),     intent(IN)    :: lon
#       real,              dimension(:,:),     intent(IN)    :: elev
#       character(len=*),                      intent(IN)    :: var
#       integer,                               intent(IN)    :: ivar
#       integer,           dimension(:,:,:,:), intent(INOUT) :: qc_flag
#       character(len=*) ,                     intent(IN)    :: roi_data_file
#
#       integer :: d, i, n, s, ss, nstnnets, ndts
#       integer :: min_stations, debug, level1, level2
#       integer :: found_one, countem_sm, countem_bg
#       integer :: print_roi_data
#       real    :: max_elev_diff, elev_diff, maxvdiff1, maxvdiff2
#       real    :: dist, roi_sm, roi_bg, latdiff, londiff, dir_diff
#       real    :: dir_thresh, spd_thresh, spd_thresh_roi, min_diff
#
#       character(len=10) :: dt_c
#
#       character(len=2), allocatable, dimension(:) :: netids
#
#       real,             allocatable, dimension(:) :: roi_dist
#       real,             allocatable, dimension(:) :: roi_spd
#       real,             allocatable, dimension(:) :: roi_dir
#       real,             allocatable, dimension(:) :: roi_lat
#       real,             allocatable, dimension(:) :: roi_lon
#       real,             allocatable, dimension(:) :: roi_elev
#       character(len=8), allocatable, dimension(:) :: roi_stnnets
#
#       real,    allocatable, dimension(:) :: dist_sort
#       integer, allocatable, dimension(:) :: isort
#
#       intrinsic maxval,minval,size
#
#       !--- Settings appropriate for all variables.
#       debug          = 0                ! sets debug level (sets what to print)
#       print_roi_data = 1
#       nstnnets       = size(stnnets)    ! get # of stations in obs.
#       ndts           = size(obs(:,1,1)) ! # of hours in obs.
#       min_stations   = 5                ! min # of stns needed for testing.
#       roi_sm         = 50               ! small radius for dir qc test.
#       roi_bg         = 75               ! big radius for dir qc test.
#       dir_thresh     = 85               ! diff in dir required for flagging.
#       spd_thresh     = 2.5722           ! spd_thresh for station in question.
#       spd_thresh_roi = 0.5144           ! spd_thresh for stations in roi.
#       level1         = suspflag         ! "suspect" flag.
#       level2         = warnflag         ! "warning" flag.
#       latdiff        = 3.0              ! to speed up station finding...
#       londiff        = 3.0              ! to speed up station finding...
#       max_elev_diff  = 99999999.0       ! for now, allow any elevations.
#
#       !--- pull netids out of the stnnets.
#       allocate(netids(nstnnets))
#       netids = stnnets(:)(7:8)
#
#       allocate( roi_dist    (nstnnets) )
#       allocate( roi_spd     (nstnnets) )
#       allocate( roi_dir     (nstnnets) )
#       allocate( roi_stnnets (nstnnets) )
#       allocate( roi_lat     (nstnnets) )
#       allocate( roi_lon     (nstnnets) )
#       allocate( roi_elev    (nstnnets) )
#
#       !--- Loop through each date.
#       do d = 1, ndts
#
#          dt_c = dts(d)
#
#          !--- Loop through each station.
#          do s = 1, nstnnets
#
#             !--- Skip this station/obs if it's mvc, or if the speed is
#             !--- below 'spd_thresh'.  Since as of 1/16/2007 many obs
#             !--- have bad elevation data, NOT skipping if this is missing
#             !--- (probably change this when station elevation data gets
#             !--- fixed by Dave Carey).
#             if (obs(d,s,ispd) .lt. spd_thresh .or. &
#                 obs(d,s,ispd) .eq. mvc .or. &
#                 obs(d,s,idir) .eq. mvc .or. &
#                 obs(d,s,iu)   .eq. mvc .or. &
#                 obs(d,s,iv)   .eq. mvc .or. &
#                 qc_flag(d,s,ispd,irangeflag) .eq. failflag .or. &
#                 qc_flag(d,s,idir,irangeflag) .eq. failflag) then
#                qc_flag(d,s,ivar,ispatialflag) = notestflag
#                cycle
#             end if
#
#             found_one = 0
#             countem_sm   = 0
#             countem_bg   = 0
#             !--- for each station, check it versus every other station
#             !--- (except itself).  First time through get # of stations
#             !--- within radius of influence to determine if we can do
#             !--- this test.
#             do ss = 1, nstnnets
#
#                !--- skip station for any of the following reasons:  same
#                !--- station as 's' (ss.eq.s), it's not within a lat/lon box
#                !--- defined by latdiff/long diff, the value is mvc,
#                !--- the value has been flagged in other tests, or the
#                !--- elevation data is mvc.
#                if ( abs(lat(d,ss) - lat(d,s) ) .gt. latdiff) cycle
#                if ( abs(lon(d,ss) - lon(d,s) ) .gt. londiff) cycle
#                if ( obs(d,ss,ispd) .eq. mvc ) cycle
#                if ( obs(d,ss,idir) .eq. mvc ) cycle
#                if ( obs(d,ss,iu)   .eq. mvc ) cycle
#                if ( obs(d,ss,iv)   .eq. mvc ) cycle
#                if ( lat(d,ss)      .eq. mvc ) cycle
#                if ( lon(d,ss)      .eq. mvc ) cycle
#                if ( obs(d,ss,ispd) .lt. spd_thresh_roi ) cycle
#                if ( abs(elev(d,ss) - elev(d,s) ) .gt. max_elev_diff) cycle
#                if ( qc_flag(d,ss,ivar,irangeflag)   .eq. failflag )  cycle
#                if ( qc_flag(d,ss,ivar,istepflag)    .eq. suspflag )  cycle
#                if ( qc_flag(d,ss,ivar,istepflag)    .eq. warnflag )  cycle
#                if ( qc_flag(d,ss,ivar,ipersistflag) .eq. suspflag )  cycle
#                if ( qc_flag(d,ss,ivar,ipersistflag) .eq. warnflag )  cycle
#                if ( ss .eq. s )  cycle
#
#                call distance(lat(d,s),lon(d,s), lat(d,ss),lon(d,ss), dist)
#
#                !--- Only add up number of stations in small roi, and keep
#                !--- around values in big roi.
#                if (dist .le. roi_sm) then
#                   countem_sm = countem_sm + 1
#                end if
#                if (dist .le. roi_bg) then
#                   countem_bg = countem_bg + 1
#                   roi_dist(countem_bg) = dist
#                   roi_spd(countem_bg) = obs(d,ss,ispd)
#                   roi_dir(countem_bg) = obs(d,ss,idir)
#                   roi_stnnets(countem_bg) = stnnets(ss)
#                   roi_lat(countem_bg) = lat(d,ss)
#                   roi_lon(countem_bg) = lon(d,ss)
#                   roi_elev(countem_bg) = elev(d,ss)
#                end if
#
#             end do
#
#             !--- if there's enough good stations in small roi, expand to big
#             !--- roi and use data from it.
#             if (countem_sm .ge. min_stations .and. &
#                 countem_bg .ge. min_stations) then
#
#                !--- calculate the minimum difference between the direction
#                !--- in question and the obs in the roi.
#                min_diff = 9999.0
#                do i = 1, countem_bg
# !                  call ndir_diff(dir_diff, roi_dir(i), obs(d,s,idir))
#                   if (dir_diff .lt. min_diff) then
#                      min_diff = dir_diff
#                   end if
#                end do
#
#                !--- if vector average speed as well as the station in
#                !--- question's speed is high enough and the direction is
#                !--- different enough from the vector average, flag it.
#                if (min_diff .gt. dir_thresh) then
#                   qc_flag(d,s,ivar,ispatialflag) = warnflag
#
#                   !--- if set, print out station and roi stations data.
#  17               format(i1,',', a10, ',', a8, ',', 4(f12.3,','), f12.3)
#                   if (print_roi_data .eq. 1) then
#                      open(unit=100, file=trim(roi_data_file), &
#                         position="append")
#                      write(100,17) 1, dt_c, &
#                         stnnets(s),elev(d,s),lat(d,s),&
#                         lon(d,s), obs(d,s,idir), obs(d,s,ispd)
#                      do i = 1, countem_bg
#                         write(100,17) 0, dt_c, &
#                            roi_stnnets(i), roi_elev(i), &
#                            roi_lat(i), roi_lon(i), &
#                            roi_dir(i), roi_spd(i)
#                      end do
#                      close(100)
#                   end if
#                end if
#
#             else
#
#                !--- not enough obs in roi to do test.
#                qc_flag(d,s,ivar,ispatialflag) = notestflag
#
#             end if
#
#          end do   !--- stations do loop.
#       end do      !--- dates do loop.
#
#       end subroutine spatial_check_dir
#

def distance(lat1, lon1, lat2, lon2):

    pi = atan2(0.0, -1.0)
    theta = lon1 - lon2

    lat1_r = lat1 * (pi / 180.)
    lat2_r = lat2 * (pi / 180.)
    theta_r = theta * (pi / 180.)

    dist = acos(sin(lat1_r) * sin(lat2_r) + cos(lat1_r) * cos(lat2_r) * cos(theta_r))
    dist_temp = (dist * (180. / pi)) * 60 * 1.1515

    # only returning in km units for now.
    return dist_temp * 1.609344
