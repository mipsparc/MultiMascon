import pyudev

# 物理接続位置を取得する
# 例: 
# - 1(1番ポートに接続)
# - 2/1(2番ポートに接続されたハブの1番ポートに接続)
def convertUSBPathToPos(devpath):
    path = devpath.split("/usb")[1]
    path = path.split(":")[0]
    path = path.split("/")[-1]
    path = path[4:]
    path = path.replace("-", "/")
    path = path.replace(".", "/")
    
    return path

def list_OHC_PC01A():
    context = pyudev.Context()
    
    positions = []
    for device in context.list_devices(subsystem='input'):
        if '0079:0006' in device.sys_path:
            positions.append(convertUSBPathToPos(device.sys_path))
    
    print(list(set(positions)))
