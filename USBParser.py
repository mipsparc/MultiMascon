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

# サンイン重工ワンハンドルマスコンを取得する
def list_OHC_PC01A():
    context = pyudev.Context()
    
    positions = []
    for device in context.list_devices(subsystem='input'):
        if device.attributes.get('idVendor') == b'0079' and device.attributes.get('idProduct') == b'0006':
            positions.append(convertUSBPathToPos(device.sys_path))
    
    print(list(set(positions)))

# タイトー 電車でGO! コントローラType2 PS2 (USB接続) を取得する
def list_DENSYA_CON_T01():
    context = pyudev.Context()
    
    positions = []
    for device in context.list_devices(subsystem='usb'):
        if device.attributes.get('idVendor') == b'0ae4' and device.attributes.get('idProduct') == b'0004':
            positions.append(convertUSBPathToPos(device.sys_path))
    
    print(list(set(positions)))
