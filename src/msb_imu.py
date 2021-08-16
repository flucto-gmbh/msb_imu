import argparse
import time
import signal       # handles signals
import sys
import zmq

from ICM20948 import ICM20948 as IMU


def signal_handler_exit(sig, frame):
    print('* msb_imu: bye')
    sys.exit(0)


def parse_arguments():
    args = argparse.ArgumentParser()

    args.add_argument(
        '--verbose',
        action='store_true',
        help='for debugging purposes'
    )

    args.add_argument(
        '--print',
        action='store_true',
        help='use this flag to print data to stdout'
    )

    args.add_argument(
        '--logfile',
        help='path to logfile',
        type=str
    )

    args.add_argument(
        '--imu-output-div',
        help='sensor output data rate. calculated by 1100/(1+output_data_div). default 21 (100 Hz)',
        default=21,
        type=int
    )

    args.add_argument(
        '--acc-range',
        help=' ',
        default='2g',
        type=str,
    )

    args.add_argument(
        '--gyro-range',
        help=' ',
        default='500dps',
        type=str,
    )

    args.add_argument(
        '--udp-stream', 
        help='flag to enable data streaming via a UDP socket',
        default=False,
        action='store_true'
    )

    args.add_argument(
        '--udp-address', 
        help='host to stream sensor data to',
        default='192.168.4.1',
        type=str
    )

    args.add_argument(
        '--udp-port',
        help='port to stream darta to',
        default=9870,
        type=int
    )

    return args.parse_args()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler_exit)
    args = parse_arguments()

    imu = IMU.ICM20948(
        verbose=args.verbose,
        output_data_div=args.imu_output_div,
        accelerometer_sensitivity=args.acc_range,
        gyroscope_sensitivity=args.gyro_range,
    )
    
    imu.begin()
    while True:
        data = imu.get_data()

        if args.print:
            print(','.join([f'{i:.6f}' for i in data]))