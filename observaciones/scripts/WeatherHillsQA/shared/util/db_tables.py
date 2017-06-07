#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from sqlalchemy import Table, Column, MetaData, ForeignKey, UniqueConstraint, create_engine, REAL
from sqlalchemy import Integer, String, Float, SmallInteger, Interval, Boolean, Index, func
from sqlalchemy.types import DateTime


# noinspection PyUnusedLocal
def prepare_tables(metadata):
    # id columns are always intended for internal-use only and not exposed to external systems
    # ref columns are our externally visible machine-readable names for use in APIs and configs

    ## INFRASTRUCTURE META-DATA

    # Providers of observation data
    provider = Table(
        'provider', metadata,
        Column('id', Integer, primary_key=True),
        Column('ref', String, nullable=False, unique=True),
        Column('name', String, nullable=False, unique=True)  # provider name
    )

    # Properties for a weather station, wind-mill or any other target of point forecasts
    station = Table(
        'station', metadata,
        Column('id', Integer, primary_key=True),
        Column('ref', String, nullable=False, unique=True),

        Column('name', String, nullable=False),  # station name
        Column('provider_id', Integer, ForeignKey(provider.c.id), nullable=False),  # the organisation running this station
        Column('ref_provider', String),  # provider's internal reference for this station
        Column('ref_wmo', Integer),  # World Meteorological Organisation ID for this station
        Column('lat', Float, nullable=False),  # position latitude [degrees]
        Column('lon', Float, nullable=False),  # position longitude [degrees]
        Column('hag', REAL),  # height above ground [m]
        Column('has', REAL),  # height above see level [m]
        Column('active', Boolean, default=True),  # is the station operational at the moment or already shut down
        Column('manual', Boolean, default=False)  # is the station man-operated or automatic
    )

    ## OBSERVATIONS

    # Each row corresponding to a single observation for a station
    observation = Table(
        'observation', metadata,
        Column('station_id', Integer, ForeignKey(station.c.id), nullable=False),  # the station where this observation was made
        Column('time', DateTime(True), nullable=False),  # date and time of the observation

        Column('wind_dir', Float),  # wind direction [deg]
        Column('wind_speed', Float),  # wind speed [m/s]
        Column('wind_gust', Float),  # wind gust [m/s]
        Column('temp', Float),  # temperature at 2m [C]
        Column('temp_road', Float),  # temperature of the road [C]
        Column('pressure', Float),  # pressure [hPa]
        Column('rel_hum', Float),  # relative humidity [%]

        Column('dew', Float),  # dew point
        Column('precip', Float), # precipitation accumulated from the last timestamp
        Column('vis', Float),  # visibility
        Column('clouds', Float),
        Column('weather', Float),
        Column('swdown', Float),  # incoming shortwave radiation
        Column('lwdown', Float),  # incoming longwave radiation

        UniqueConstraint('station_id', 'time')
    )

    # Measured power output for stations which happen to be wind mills.
    # wind_power = Table(
    #     'wind_power', metadata,
    #     Column('station_id', Integer, ForeignKey(station.c.id), nullable=False),
    #     Column('time', DateTime(True), nullable=False),
    #     Column('power_value', Float),
    #     UniqueConstraint('station_id', 'time')
    # )

    # Quality assurance results for observations.
    observation_quality = Table(
        'observation_quality', metadata,
        Column('time', DateTime(True), nullable=False),  # date and time of the observation
        Column('station_id', Integer, ForeignKey(station.c.id), nullable=False),
        Column('variable', String, nullable=False),  # name of the variable for which the QA was done (temp, wind_dir etc.)
        Column('value', Float),  # value we perform QA for
        Column('q_range', SmallInteger),  # the result of range check
        Column('q_step', SmallInteger),  # the result of step check
        Column('q_persistence', SmallInteger),  # the result of persistence check
        Column('q_spatial', SmallInteger),  # the result of spatial check

        UniqueConstraint('station_id', 'time', 'variable')
    )


    ## FORECASTS

    # Schedule for Belgingur forecasts
    schedule = Table(
        'schedule', metadata,
        Column('id', Integer, primary_key=True),
        Column('ref', String, nullable=False, unique=True)
    )

    # Point forecast. Metadata about a single point forecast created from a wrfout file for a concrete station.
    point_forecast = Table(
        'point_forecast', metadata,
        Column('id', Integer, primary_key=True),
        Column('station_id', Integer, ForeignKey(station.c.id), nullable=False),  # the station which this forecast applies to
        Column('analysis', DateTime(True), nullable=False),  # date of global analysis used to generate this forecast
        Column('schedule_id', Integer, ForeignKey(schedule.c.id)),  # id of a schedule this point forecast was made for
        Column('domain', SmallInteger, server_default='-1'),  # number of the domain within schedule (d01, d02)
        UniqueConstraint('station_id', 'analysis', 'schedule_id', 'domain'),
    )

    # Point forecast data. Structure should be kept similar to observation table.
    point_forecast_data = Table(
        'point_forecast_data', metadata,
        Column('forecast_id', Integer, ForeignKey(point_forecast.c.id, ondelete="CASCADE"), nullable=False),
        Column('time', DateTime(True), nullable=False),

        Column('wind_dir', Float),  # wind direction [deg]
        Column('wind_speed', Float),  # wind speed [m/s]
        Column('temp', Float),  # 2m temperature
        Column('prec_rate', Float),  # precipitation rate
        Column('total_clouds', Float),
        Column('mslp', Float),  # mean sea level pressure
        Column('snow_ratio', Float),
        Column('air_density', Float),
        Column('rel_hum', Float),  # relative humidity
        Column('dew', Float),  # dew point
        Column('precip', Float), # precipitation accumulated from the last timestamp
        Column('vis', Float),  # visibility
        Column('cloudfrac', Float),
        Column('cloudbase', Float),
        Column('swdown', Float),  # incoming shortwave radiation
        Column('lwdown', Float),  # incoming longwave radiation

        UniqueConstraint('forecast_id', 'time')
    )


def create_tables(engine_or_url):
    if isinstance(engine_or_url, basestring):
        engine = create_engine(engine_or_url)
    else:
        engine = engine_or_url
    with engine.begin():
        metadata = MetaData()
        prepare_tables(metadata)
        metadata.create_all(engine)
    return metadata
