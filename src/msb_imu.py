import time
import sys
import zmq
import logging
import pickle

# TODO:
# - no ipc flag einbauen fuer testing

try:
    from imu_config import (init, IMU_TOPIC)
except ImportError:
    print('faild to import init function from config.py')
    sys.exit(-1)

try:
    from ICM20948 import ICM20948 as IMU
except ImportError:
    print('failed to import ICM20948 module')
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

    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port"]}'
    logging.debug(f'binding to {connect_to} for zeroMQ IPC')
    ctx = zmq.Context()
    s = ctx.socket(zmq.PUB)
    s.connect(connect_to)
    logging.debug(f'connected to zeroMQ IPC socket')

    #sync(connect_to)

    logging.debug('entering endless loop')
    
    try:
        while True:

            # data = {config['id'] : imu.get_data()}
            data = imu.get_data()

            if config['print']:
                print(data)
            # send multipart message:

            s.send_multipart(
                [
                    IMU_TOPIC,    # topic
                    pickle.dumps( # serialize the payload
                        data
                    )
                ]
            )

            # s.send_pyobj(data)

            time.sleep(1/config['sample_rate'])
    except KeyboardInterrupt:
        logging.info('msb_imu bye')
        sys.exit(0)

if __name__ == '__main__':
    main()
