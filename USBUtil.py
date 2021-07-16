import pyudev
import queue
import re
import logging

trig_q = queue.Queue()

class USBUtil:
    # もともとつながっていたデバイスの追加を行う
    @staticmethod
    def init():
        context = pyudev.Context()
        for device in context.list_devices():
            if '/usb' in device.sys_path:
                USBUtil.usbTrigger('add', device)
    
    # ポートごとにイベントをまとめる
    @staticmethod
    def sumUSBEvents():
        add_events = {}
        remove_ports = []
        
        while True:
            try:
                e = trig_q.get_nowait()
                
                formatted = {'bus': e['bus'], 'address': e['address'], 'path': e['path'], 'vendor': e['vendor'], 'product': e['product']}

                # 追加
                if e['action'] == 'add':
                    if e['port'] in add_events:
                        add_events[e['port']].append(formatted)
                    else:
                        add_events[e['port']] = [formatted, ]
                # 除去
                else:
                    if e['port'] not in remove_ports:
                        remove_ports.append(e['port'])
            except queue.Empty:
                break
        
        
        adds = []
        for port, events in add_events.items():
            # 正常にすべての項目が埋まらなかったときはNameErrorがでる
            try:
                adds.append(USBUtil.parseAddEvents(port, events))
            except NameError:
                pass

        remove_ports_splitted = []
        for port in remove_ports:
            port = port[4:]
            if port == '':
                continue
            remove_ports_splitted.append(port)
            
        return [adds, remove_ports_splitted]
    
    @staticmethod
    def parseAddEvents(port, events):
        p = re.compile(r'/js[0-9]$')
        # ジョイスティックでなければNoneが入る
        joystick_num = None
        for data in events:
            if data['bus'] is not None:
                bus = int(data['bus'].decode())
            if data['address'] is not None:
                address = int(data['address'].decode())
            if data['vendor'] is not None:
                vendor = data['vendor'].decode()
            if data['product'] is not None:
                product = data['product'].decode()
            if p.search(data['path']) is not None:
                j = data['path'].split('/')[-1]
                joystick_num = int(j.replace('js', ''))
        
        # 基底USBデバイスを対象外にする
        port = port[4:]
        if port == '':
            raise NameError

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
    def usbTrigger(action, device):
        if '/usb' not in device.sys_path:
            return
        
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
