from __future__ import absolute_import, division, print_function, unicode_literals
from nose.tools import assert_equal, assert_raises, assert_true, assert_false, assert_dict_equal
from parser.vedurstofan import *


def test_parse_header_line():
    parser = VedurstofanCsvObservationParser()
    assert_true(parser.parse_header_line('#STOD,TIMI,AR,MAN,DAGUR,KLST,TEG,T,TW,TD,RH,VP,TX,TXSL,TN,TNSP,TGN,TGNSP,TS,TP,PO,PS,P,PBR,A,R,RTEG,RDRY,D,F,FX,FG,V,N,NH,H,CL,CM,CH,W,W1,W2,W3,SUN,E,SNC,SNCM,SND,S,ICE,EH,QT,QTW,QTX,QTN,QTGN,QTS,QP,QPBR,QA,QR,QRTEG,QD,QF,QFX,QFG,QV,QN,QNH,QH,QCL,QCM,QCH,QW,QW1,QW2,QW3,QSUN,QE,QSNC,QSNCM,QSND,QS,QICE,QEH,ERRT,ERRTW,ERRTX,ERRTN,ERRTGN,ERRTS,ERRP,ERRPBR,ERRA,ERRR,ERRRTEG,ERRD,ERRF,ERRFX,ERRFG,ERRV,ERRN,ERRNH,ERRH,ERRCL,ERRCM,ERRCH,ERRW,ERRW1,ERRW2,ERRW3,ERRSUN,ERRE,ERRSNC,ERRSNCM,ERRSND,ERRS,ERRICE,ERREH,CRETIME,CREUSR,MODTIME,MODUSR,ORIGIN'))
    assert_true(parser.parse_header_line('#aaa,TIMI,STOD'))
    assert_true(parser.parse_header_line(''))
    assert_false(parser.parse_header_line('12345'))
    assert_false(parser.parse_header_line('252,2010-09-03_00:00:00.0,2010,9,2,24,1,13.9,12.1,10.5,80,12.7,#,#,#,#,#,#,#,25.4,1011.4,1008.9,1011.0,-0.6,7,#,#,#,20,1.4,1.4,2.2,89,3,3,4,2,0,0,#,#,#,#,#,#,#,#,#,0,#,#,70000,70000,99999,99999,99999,99999,70000,70000,70000,99999,99999,70000,70000,70000,70000,80999,70000,70000,70000,70000,70000,70000,99999,99999,99999,99999,99999,99999,99999,99999,99999,70000,99999,99999,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,2010-09-03_00:01:07.236,157.157.13.20,2010-09-03_00:01:13.005,157.157.13.20,1'))


def test_parse_data_line():
    parser = VedurstofanCsvObservationParser()
    parser.parse_header_line('#STOD,TIMI,AR,MAN,DAGUR,KLST,TEG,T,TW,TD,RH,VP,TX,TXSL,TN,TNSP,TGN,TGNSP,TS,TP,PO,PS,P,PBR,A,R,RTEG,RDRY,D,F,FX,FG,V,N,NH,H,CL,CM,CH,W,W1,W2,W3,SUN,E,SNC,SNCM,SND,S,ICE,EH,QT,QTW,QTX,QTN,QTGN,QTS,QP,QPBR,QA,QR,QRTEG,QD,QF,QFX,QFG,QV,QN,QNH,QH,QCL,QCM,QCH,QW,QW1,QW2,QW3,QSUN,QE,QSNC,QSNCM,QSND,QS,QICE,QEH,ERRT,ERRTW,ERRTX,ERRTN,ERRTGN,ERRTS,ERRP,ERRPBR,ERRA,ERRR,ERRRTEG,ERRD,ERRF,ERRFX,ERRFG,ERRV,ERRN,ERRNH,ERRH,ERRCL,ERRCM,ERRCH,ERRW,ERRW1,ERRW2,ERRW3,ERRSUN,ERRE,ERRSNC,ERRSNCM,ERRSND,ERRS,ERRICE,ERREH,CRETIME,CREUSR,MODTIME,MODUSR,ORIGIN')
    actual = parser.parse_data_line('252,2010-09-03_00:00:00.0,2010,9,2,24,1,13.9,12.1,10.5,80,12.7,#,#,#,#,#,#,#,25.4,1011.4,1008.9,1011.0,-0.6,7,#,#,#,20,1.4,1.4,2.2,89,3,3,4,2,0,0,#,#,#,#,#,#,#,#,#,0,#,#,70000,70000,99999,99999,99999,99999,70000,70000,70000,99999,99999,70000,70000,70000,70000,80999,70000,70000,70000,70000,70000,70000,99999,99999,99999,99999,99999,99999,99999,99999,99999,70000,99999,99999,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,2010-09-03_00:01:07.236,157.157.13.20,2010-09-03_00:01:13.005,157.157.13.20,1')
    expected = {'wind_speed': 1.4, 'wind_gust': 2.2, 'temp': 13.9, 'pressure': 1011.0, 'rel_hum': 80.0, 'station_ref': '252', 'time': datetime(2010, 9, 3, 0, 0), 'wind_dir': 20.0}
    assert_dict_equal(expected, actual)


def test_parse_time():
    assert_equal(datetime(2011, 10, 27, 21), parse_time('2011-10-27_21:00:00.0'))
    assert_equal(datetime(2011, 10, 27, 21, 1, 49), parse_time('2011-10-27_21:01:49.0'))
    with assert_raises(ValueError):
        parse_time('2011-10-27_21:01:49')