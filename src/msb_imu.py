import argparse
import time
import signal       # handles signals
import sys
import zmq
import logging

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

    args = init()

    # calculate time.sleep time
    # 1100/(1+output_data_div)

    imu = IMU.ICM20948(
        verbose=args['verbose'],
        output_data_div=args['imu_output_div'],
        accelerometer_sensitivity=args['acc_range'],
        gyroscope_sensitivity=args['gyro_range'],
    )

    imu.begin()

    """
    try:
        socket.recv()
    except KeyboardInterrupt:
        print("W: interrupt received, stopping...")
    finally:
        # clean up
        socket.close()
        context.term()

    """

    while True:
        data = imu.get_data()

        if args['print']:
            print(','.join([f'{i:.6f}' for i in data]))

        if args['logfile']:
            pass
        
        time.sleep(1/args['sample_rate'])

if __name__ == '__main__':
    main()