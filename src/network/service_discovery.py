from zeroconf import ServiceInfo, Zeroconf
import socket
import netifaces as ni

class ServiceDiscovery:
    def __init__(self):
        self.zeroconf = None
        self.service_info = None
        
    def register_service(self, port):
        self.zeroconf = Zeroconf()
        ip = self._get_local_ip()
        
        self.service_info = ServiceInfo(
            "_http._tcp.local.",
            "ServicesSound._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=port,
            properties={'path': '/stream'}
        )
        self.zeroconf.register_service(self.service_info)
        
    def _get_local_ip(self):
        return ni.ifaddresses(ni.gateways()['default'][ni.AF_INET][1])[ni.AF_INET][0]['addr']
