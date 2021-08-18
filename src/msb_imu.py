import argparse
import time
import signal       # handles signals
import sys
import zmq
import logging

# TODO:
# - no ipc flag einbauen fuer testing

try:
    from config import  init
except ImportError:
    print(f'faild to init function from config.py')
    sys.exit(-1)

try:
    from ICM20948 import ICM20948 as IMU
except ImportError:
    print(f'failed to import ICM20948 module')
    sys.exit(-1)

def main():

    config = init()

    dt_sleep = 1/config['sample_rate']
    logging.debug(f'sample rate set to {config["sample_rate"]}, sleeping for {dt_sleep} s')

    logging.debug('inititating sensor..')

    imu = IMU.ICM20948(
        verbose=config['verbose'],
        output_data_div=config['imu_output_div'],
        accelerometer_sensitivity=config['acc_range'],
        gyroscope_sensitivity=config['gyro_range'],
    )

    logging.debug('.. sensor init done')

    imu.begin()

    connect_to = f'{config["ipc_protocol"]}:///tmp/msb:{config["ipc_port"]}'
    logging.debug(f'binding to {connect_to} for zeroMQ IPC')
    ctx = zmq.Context()
    s = ctx.socket(zmq.PUB)
    s.connect(connect_to)
    logging.debug(f'connected to zeroMQ IPC socket')

    #sync(connect_to)

    logging.debug('entering endless loop')

    while True:
        data = imu.get_data()

        if config['print']:
            print(','.join([f'{i:.6f}' for i in data]))
        
        s.send_pyobj(data)

        time.sleep(1/config['sample_rate'])

if __name__ == '__main__':
    main()