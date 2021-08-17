import argparse
import json
import sys
import signal
import logging

from os import path

def signal_handler_exit(sig, frame):
    print('* msb_imu: bye')
    sys.exit(0)

def dump_config_file(args : dict):
    with open(args['dump_config_file'], 'w') as config_file_handle:
        config_file_handle.writelines(
            json.dumps(
                args,
                indent=4
            )
        )

def read_parse_config_file(args : dict) -> dict:

    try:
        config_file_handler = open(args['config_file'], 'r')
    except Exception as e:
        print(f'failed to open config file: {e}')
        sys.exit(-1)

    config_file_args = json.load(config_file_handler)

    for key, value in config_file_args.items():
        if key == 'config_file':
            continue

        if key in args:

            print(f'parsing {key} : {value}')
            args[key] = value
        else:
            print(f'key not found: {key} omitting')

    return args    
    # 1. read config file
    # 2. convert from json to dict
    # 3. iterate over entries in dictionary and override parsed arguments

# build a config named tuple

def parse_arguments() -> dict:
    arg_pars = argparse.ArgumentParser()

    arg_pars.add_argument(
        '--verbose',
        action='store_true',
        help='for debugging purposes'
    )

    arg_pars.add_argument(
        '--print',
        action='store_true',
        help='use this flag to print data to stdout'
    )

    arg_pars.add_argument(
        '--logfile',
        help='path to logfile',
        type=str,
        default='',
    )

    arg_pars.add_argument(
        '--imu-output-div',
        help='sensor output data rate. calculated by 1100/(1+output_data_div). default 21 (100 Hz)',
        default=21,
        type=int
    )

    arg_pars.add_argument(
        '--sample-rate',
        help='polling frequency with which data is retrieved from the sensor. must be >= ODR',
        default=50,
        type=int,
    )

    arg_pars.add_argument(
        '--acc-range',
        help=' ',
        default='2g',
        type=str,
    )

    arg_pars.add_argument(
        '--acc-filter',
        help='low pass filter to be applied to the raw data coming from the sensor. options are 1 - 6',
        default=1,
        type=int,
    )

    arg_pars.add_argument(
        '--gyro-range',
        help=' ',
        default='500dps',
        type=str,
    )

    arg_pars.add_argument(
        '--gyro-filter',
        help='low pass filter to be applied to the raw data coming from the gyro. options are 1 - 6',
        default=1,
        type=int,
    )

    arg_pars.add_argument(
        '--config-file',
        help='configuration file: overwrite all commandline options!',
        default='',
        type=str,
    )

    arg_pars.add_argument(
        '--dump-config-file',
        help='dumps the default config values into a file',
        default='msb_imu.json',
    )

    arg_pars.add_argument(
        '--udp-stream', 
        help='flag to enable data streaming via a UDP socket',
        default=False,
        action='store_true'
    )

    arg_pars.add_argument(
        '--udp-address', 
        help='host to stream sensor data to',
        default='192.168.4.1',
        type=str
    )

    arg_pars.add_argument(
        '--udp-port',
        help='port to stream darta to',
        default=9870,
        type=int
    )

    arg_pars.add_argument(
        '--profile',
        help='profile flag',
        default=False,
        action='store_true'
    )

    return arg_pars.parse_args().__dict__

def init() -> dict:

    signal.signal(signal.SIGINT, signal_handler_exit)

    args = parse_arguments()

    if args['config_file']:
        args = read_parse_config_file(args)

    if args['dump_config_file']:
        dump_config_file(args)

    return args
    
