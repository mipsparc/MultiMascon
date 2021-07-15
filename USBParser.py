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

def listMascons():
    context = pyudev.Context()
    
    # サンイン重工ワンハンドルマスコン
    OHC_PC01A = []
    # タイトー 電車でGO! コントローラType2 PS2 (USB接続)
    DENSYA_CON_T01 = []
    for device in context.list_devices(subsystem='usb'):
        if device.attributes.get('idVendor') == b'0079' and device.attributes.get('idProduct') == b'0006':
            OHC_PC01A.append(convertUSBPathToPos(device.sys_path))
        if device.attributes.get('idVendor') == b'0ae4' and device.attributes.get('idProduct') == b'0004':
            DENSYA_CON_T01.append(convertUSBPathToPos(device.sys_path))
    
    # 重複排除
    OHC_PC01A = set(OHC_PC01A)
    DENSYA_CON_T01 = set(DENSYA_CON_T01)

    return {'OHC_PC01A': OHC_PC01A, 'DENSYA_CON_T01': DENSYA_CON_T01}
