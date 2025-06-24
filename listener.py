import math
import socket
import struct
import os
from scipy.spatial.transform import Rotation as R

log_file_path = "drone_telemetry_log.txt"

def listen_to_udp(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('0.0.0.0', port))
        print(f"Listening for UDP packets on port {port}...")
        
        while True:
            data, client_address = udp_socket.recvfrom(1024)
            bytes_telemetry = bytearray(data)   

            timestamp = bytes_telemetry[0:4]
            position_x = bytes_telemetry[4:8]
            position_y = bytes_telemetry[8:12]
            position_z = bytes_telemetry[12:16]
            quaternion_x = bytes_telemetry[16:20]
            quaternion_y = bytes_telemetry[20:24]
            quaternion_z = bytes_telemetry[24:28]
            quaternion_w = bytes_telemetry[28:32]
            speed_x = bytes_telemetry[32:36]
            speed_y = bytes_telemetry[36:40]
            speed_z = bytes_telemetry[40:44]
            gyro_pitch = bytes_telemetry[44:48]
            gyro_roll = bytes_telemetry[48:52]
            gyro_yaw = bytes_telemetry[52:56]
            input_throttle = bytes_telemetry[56:60]
            input_yaw = bytes_telemetry[60:64]
            input_pitch = bytes_telemetry[64:68]
            input_roll = bytes_telemetry[68:72]
            battery_percentage = bytes_telemetry[72:76]
            battery_voltage = bytes_telemetry[76:80]
            motor_rpm_count = bytes_telemetry[80:81]
            motor_left_front = bytes_telemetry[81:85]
            motor_right_front = bytes_telemetry[85:89]
            motor_left_back = bytes_telemetry[89:93]
            motor_right_back = bytes_telemetry[93:97]

            drone_position_x = struct.unpack('f', position_x[:4])[0]
            drone_position_y = struct.unpack('f', position_y[:4])[0]
            drone_position_z = struct.unpack('f', position_z[:4])[0]
            drone_quaternion_x = struct.unpack('f', quaternion_x[:4])[0]
            drone_quaternion_y = struct.unpack('f', quaternion_y[:4])[0]
            drone_quaternion_z = struct.unpack('f', quaternion_z[:4])[0]
            drone_quaternion_w = struct.unpack('f', quaternion_w[:4])[0]
            

            # Convert quaternion to Euler angles
            quat = [drone_quaternion_x, drone_quaternion_y, drone_quaternion_z, drone_quaternion_w]
            r = R.from_quat(quat)
            euler_rad = r.as_euler('yxz', degrees=False)
            drone_euler_x, drone_euler_y, drone_euler_z = [math.degrees(angle) for angle in euler_rad]

            #inverse y and x
            temp_value = drone_euler_x
            drone_euler_x = drone_euler_y
            drone_euler_y = temp_value

      

            #d = f"Timestamp: {struct.unpack('f', timestamp[:4])[0]:.2f}, Position: ({drone_position_x:.2f}, {drone_position_y:.2f}, {drone_position_z:.2f}), Euler Angles: ({drone_euler_x:.2f}, {drone_euler_y:.2f}, {drone_euler_z:.2f})"
            data_dict = {
                "Timestamp": struct.unpack('f', timestamp[:4])[0],
                "PositionX": drone_position_x,
                "PositionY": drone_position_y,
                "PositionZ": drone_position_z,
                "EulerX": drone_euler_x,
                "EulerY": drone_euler_y,
                "EulerZ": drone_euler_z,
                "SpeedX": struct.unpack('f', speed_x[:4])[0],
                "SpeedY": struct.unpack('f', speed_y[:4])[0],
                "SpeedZ": struct.unpack('f', speed_z[:4])[0],
                "GyroPitch": struct.unpack('f', gyro_pitch[:4])[0],
                "GyroRoll": struct.unpack('f', gyro_roll[:4])[0],
                "GyroYaw": struct.unpack('f', gyro_yaw[:4])[0],
                "InputThrottle": struct.unpack('f', input_throttle[:4])[0],
                "InputYaw": struct.unpack('f', input_yaw[:4])[0],
                "InputPitch": struct.unpack('f', input_pitch[:4])[0],
                "InputRoll": struct.unpack('f', input_roll[:4])[0],
                "BatteryPercentage": struct.unpack('f', battery_percentage[:4])[0],
                "BatteryVoltage": struct.unpack('f', battery_voltage[:4])[0],
                "MotorLeftFrontRPM": struct.unpack('f', motor_left_front[:4])[0],
                "MotorRightFrontRPM": struct.unpack('f', motor_right_front[:4])[0],
                "MotorLeftBackRPM": struct.unpack('f', motor_left_back[:4])[0],
                "MotorRightBackRPM": struct.unpack('f', motor_right_back[:4])[0]
            }
            # Convert the dictionary to a CSV format string
            csv_data = ','.join(f"{value}" for value in data_dict.values())
            print(csv_data)
            #append data to log file
            #os.system(f"echo '{d}' >> {log_file_path}")
if __name__ == "__main__":
    listen_to_udp(port=9998)




# """
# https://steamcommunity.com/sharedfiles/filedetails/?id=3160488434
# C:\Users\Shadow\AppData\LocalLow\LuGus Studios\Liftoff  TelemetryConfiguration.json
# {
#     "EndPoint": "127.0.0.1:9001",
#     "StreamFormat": [
#       "Timestamp",
#       "Position",
#       "Attitude",
#       "Velocity",
#       "Gyro",
#       "Input",
#       "Battery",
#       "MotorRPM"
#     ]
#   }


# Timestamp (1 float) - current timestamp of the drone's flight. The unit scale is in seconds. This value is reset to zero when the drone is reset.
# Position (3 floats) - the drone's world position as a 3D coordinate. The unit scale is in meters. Each position component can be addressed individually as PositionX, PositionY, or PositionZ.
# Attitude (4 floats) - the drone's world attitude as a quaternion. Each quaternion component can be addressed individually as AttitudeX, AttitudeY, AttitudeZ and AttitudeW.
# Velocity (3 floats) - the drone's linear velocity as a 3D vector in world-space. The unit scale is in meters/second. Each component can be addressed individually as SpeedX, SpeedY, or SpeedZ. Note: to get the velocity in local-space, transform it[math.stackexchange.com] using the values in the Attitude data stream.
# Gyro (3 floats) - the drone's angular velocity rates, represented with three components in the order: pitch, roll and yaw. The unit scale is in degrees/second. Each component can also be addressed individually as GyroPitch, GyroRoll and GyroYaw.
# Input (4 floats) - the drone's input at that time, represented with four components in the following order: throttle, yaw, pitch and roll. Each input can be addressed individually as InputThrottle, InputYaw, InputPitch and InputRoll.
# Battery (2 floats) - the drone's current battery state, represented by the remaining voltage, and the charge percentage. Each of these two can be addressed individually with the BatteryPercentage and BatteryVoltage keys. Note - these values will only make sense when battery simulation is enabled in the game's options.
# MotorRPM (1 byte + (1 float * number of motors)) - the rotations per minute for each motor. The byte at the front of this piece of data defines the amount of motors on the drone, and thus how many floats you can expect to find next. The sequence of motors for a quadcopter in Liftoff is as follows: left front, right front, left back, right back.

# """
