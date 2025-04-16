from scipy.spatial.transform import Rotation as R

def euler_to_quaternion(roll: float, pitch: float, yaw: float, degrees=True):
    """
    Convert Euler angles (roll, pitch, yaw) to a quaternion [x, y, z, w].
    
    Args:
        roll (float): rotation around X-axis
        pitch (float): rotation around Y-axis
        yaw (float): rotation around Z-axis
        degrees (bool): whether input angles are in degrees (default: True)
    
    Returns:
        List[float]: quaternion [x, y, z, w]
    """
    r = R.from_euler('xyz', [roll, pitch, yaw], degrees=degrees)
    return r.as_quat().tolist()


def main():
    # Rotate 90 degrees around Z (yaw)
    quat = euler_to_quaternion(0, 0, 90)
    print(quat)  # -> e.g., [0.0, 0.0, 0.7071, 0.7071]

if __name__ == "__main__":
    main()
