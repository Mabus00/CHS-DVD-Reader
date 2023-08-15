import subprocess

def get_usb_devices():
    output = subprocess.check_output(['wmic', 'path', 'win32_pnpentity', 'where', 'Caption like "%USB%"', 'get', 'DeviceID'], text=True)
    lines = output.strip().split('\n')
    devices = []

    for line in lines[1:]:  # Skip the header line
        device_id = line.strip()
        devices.append(device_id)

    return devices

usb_devices = get_usb_devices()

for device_id in usb_devices:
    print(f"USB Device ID: {device_id}")
