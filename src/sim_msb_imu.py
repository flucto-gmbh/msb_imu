import zmq
import sys
import logging
import uptime
from multiprocessing import Process
## needs python 3.10
# from dataclass import dataclass

try:
    from config import init
except ImportError as e:
    print(f'failed to import init function from config.py: {e}')
    sys.exit(-1)

class IMU():
    
    """
    ICM-20948

        : param address: I2C address to use for the motion sensor. 
                         The sensor has two different possible addresses (0x68 and 0x69)
                         depending on wether AD0 is high (0x69) or low (0x68)
        : param i2c_bus: if an I2C bus has already been initiated somewehere else, 
                         use this parameter to pass the bus object to the object.
        : return:        ICM20938 object
        : rtype:         Object
    """

    device_name = "ICM20948_SIM"
    _data_generator_process = None

    _acceleration_x_raw = _acceleration_y_raw = _acceleration_z_raw = 0
    _gyroscope_x_raw = _gyroscope_y_raw = _gyroscope_z_raw = 0
    _mag_x_raw = _mag_y_raw = _mag_z_raw = _mag_stat_1 = _mag_stat_2 = 0
    _temp_raw = 0
    _update_time = 0            # holds the time stamp at which the last sensor data was retrieved 
    _update_time_uptime = 0     # holds the uptime at which the last sensor data was retrieved since boot
    _verbose = False
    
    def __init__(self):
        pass

    def _update_data(self):
        
        """
        this funciton is regularly called by the data_generator_process to 
        provide updated values of the simulated sensor
        """
        
        self._update_time = time.time()
        self._update_time_uptime = uptime.uptime()
        
        
        
    def begin(self):
        
        self._data_generator_process = Process(target = self._update_data, args=(self,))
        self._data_generator_process.start()

    def get_data(self):
        return [
            self._update_time,
            self._update_time_uptime,
            
            self._acceleration_x_raw/self._selected_accelerometer_scale,
            self._acceleration_y_raw/self._selected_accelerometer_scale,
            self._acceleration_z_raw/self._selected_accelerometer_scale,

            self._gyroscope_x_raw/self._selected_gyroscope_scale,
            self._gyroscope_y_raw/self._selected_gyroscope_scale,
            self._gyroscope_z_raw/self._selected_gyroscope_scale,
            
            self._mag_x_raw,
            self._mag_y_raw,
            self._mag_z_raw,
            
            self._temp_raw,
        ]

    


def main():

    config = init()

    dt_sleep = 1/config['sample_rate']
    logging.debug(f'sample rate set to {config["sample_rate"]}, sleeping for {dt_sleep} s')

    logging.debug('inititating sensor..')
    imu = IMU()
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
    
    try:
        while True:

            data = {config['id'] : imu.get_data()}

            if config['print']:
                print(json.dumps(data))

            s.send_pyobj(data)

            time.sleep(1/config['sample_rate'])
    except KeyboardInterrupt:
        logging.info('msb_imu bye')
        sys.exit(0)

if __name__ == '__main__':
    main()

