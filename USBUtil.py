import pyudev
import queue
import re

trig_q = queue.Queue()

class USBUtil:
    # もともとつながっていたデバイスの追加を行う
    @staticmethod
    def init():
        devices = usb.core.find(find_all=True)
        for device in devices:
            USBUtil.usbTrigger('add', device)
    
    # ポートごとにイベントをまとめる
    @staticmethod
    def sumUSBEvents():
        add_events = {}
        remove_events = {}
        
        while True:
            try:
                e = trig_q.get_nowait()
                
                formatted = {'bus': e['bus'], 'address': e['address'], 'path': e['path'], 'vendor': e['vendor'], 'product': e['product']}

                if e['action'] == 'add':
                    if e['port'] in add_events:
                        add_events[e['port']].append(formatted)
                    else:
                        add_events[e['port']] = [formatted, ]
                else:
                    if e['port'] in remove_events:
                        remove_events[e['port']].append(formatted)
                    else:
                        remove_events[e['port']] = [formatted, ]
            except queue.Empty:
                break
        
        
        adds = []
        removes = []
        for port in add_events:
            try:
                adds.append(USBUtil.parseEvents(port, add_events))
            except NameError:
                pass
        for port in remove_events:
            try:
                removes.append(USBUtil.parseEvents(port, remove_events))
            except NameError:
                pass
            
        return [adds, removes]
    
    @staticmethod
    def parseEvents(port, events):
        p = re.compile(r'/js[0-9]$')
        # ジョイスティックでなければNoneが入る
        joystick_num = None
        for data in events[port]:
            if data['bus'] is not None:
                bus = int(data['bus'].decode())
            if data['address'] is not None:
                address = int(data['address'].decode())
            if data['vendor'] not in None:
                vendor = data['vendor'].decode()
            if data['product'] not in None:
                product = data['product'].decode()
            if p.search(data['path']) is not None:
                j = data['path'].split('/')[-1]
                joystick_num = int(j.replace('js', ''))

        return {'port': port, 'bus': bus, 'address': address, 'joystick_num': joystick_num, 'vendor': vendor, 'product': product}
    
    # 物理接続位置を取得する
    # 例: 
    # - 1(1番ポートに接続)
    # - 2/1(2番ポートに接続されたハブの1番ポートに接続)
    @staticmethod
    def convertUSBPathToPos(devpath):
        path = devpath.split("/usb")[1]
        path = path.split(":")[0]
        path = path.split("/")[-1]
        path = path.replace("-", "/")
        path = path.replace(".", "/")
        
        return path

    @staticmethod
    def is_DENSYA_CON_T01(device):
        return 

    @staticmethod
    def usbTrigger(action, device):
        if action == 'add' or action == 'remove':
            trig_q.put({
                'action': action,
                'port': str(USBUtil.convertUSBPathToPos(device.sys_path)),
                'path': str(device.sys_path),
                'bus': device.attributes.get('busnum'),
                'address': device.attributes.get('devnum'),
                'vendor': device.attributes.get('idVendor'),
                'product': device.attributes.get('idProduct')
            })

    @staticmethod
    def startMasconMonitor():
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
                    
        observer = pyudev.MonitorObserver(monitor, USBUtil.usbTrigger)
        observer.start()
