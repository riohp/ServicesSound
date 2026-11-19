---
name: network-debug
description: Debugging de red para aplicaciones Python con Zeroconf/mDNS, sockets UDP/TCP y descubrimiento de dispositivos en LAN. Usar al implementar o depurar service_discovery.py y connection_manager.py en ServicesSound.
---

# Network Debug Skill — ServicesSound

## Implementacion real de Zeroconf

```python
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser
import socket

SERVICE_TYPE = "_servicessound._tcp.local."
SERVICE_NAME = f"ServicesSound.{SERVICE_TYPE}"

class ServiceDiscovery:
    def __init__(self):
        self._zeroconf = None
        self._info = None
        self._browser = None

    def register_service(self, port: int, ip: str):
        """Registra el servicio en la red local via mDNS."""
        self._zeroconf = Zeroconf()
        self._info = ServiceInfo(
            type_=SERVICE_TYPE,
            name=SERVICE_NAME,
            addresses=[socket.inet_aton(ip)],
            port=port,
            properties={"version": "1.0", "device": "ServicesSound"},
            server=f"{socket.gethostname()}.local.",
        )
        self._zeroconf.register_service(self._info)
        logger.info(f"Servicio registrado: {SERVICE_NAME} en {ip}:{port}")

    def browse_devices(self, callback):
        """Descubre otros dispositivos ServicesSound en la red."""
        class Listener:
            def add_service(self, zc, type_, name):
                info = zc.get_service_info(type_, name)
                if info:
                    callback(info)

            def remove_service(self, zc, type_, name):
                pass

            def update_service(self, zc, type_, name):
                pass

        self._browser = ServiceBrowser(self._zeroconf, SERVICE_TYPE, Listener())

    def unregister_service(self):
        if self._zeroconf and self._info:
            self._zeroconf.unregister_service(self._info)
            self._zeroconf.close()
```

## Diagnostico de red en tiempo real

```bash
# Ver servicios mDNS en la red (macOS/Linux)
dns-sd -B _servicessound._tcp local.
avahi-browse -t _servicessound._tcp

# Ver puertos en uso
netstat -an | grep 8000
ss -tulnp | grep 8000

# Test de conectividad UDP
python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'ping', ('192.168.1.X', 8000))
print('UDP enviado')
s.close()
"
```

## Connection Manager — implementacion base

```python
import socket
import threading
import queue
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Client:
    ip: str
    port: int
    connected_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

class ConnectionManager:
    def __init__(self, port: int = 8000):
        self._port = port
        self._clients: dict[str, Client] = {}
        self._lock = threading.Lock()
        self._server_sock = None
        self._running = False

    def start(self):
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind(("0.0.0.0", self._port))
        self._running = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        while self._running:
            try:
                data, addr = self._server_sock.recvfrom(4096)
                self._handle_client(addr, data)
            except OSError:
                break

    def _handle_client(self, addr, data):
        ip, port = addr
        with self._lock:
            if ip not in self._clients:
                self._clients[ip] = Client(ip=ip, port=port)
                logger.info(f"Nuevo cliente: {ip}:{port}")
            else:
                self._clients[ip].last_seen = datetime.now()

    @property
    def client_count(self) -> int:
        with self._lock:
            return len(self._clients)

    def stop(self):
        self._running = False
        if self._server_sock:
            self._server_sock.close()
```

## Debugging de conexion con Alexa

### Flujo esperado
1. ServicesSound registra `_servicessound._tcp.local.` via Zeroconf
2. Alexa descubre el servicio en la red
3. Alexa se conecta al puerto UDP/TCP anunciado
4. Audio se transmite en chunks continuos

### Herramientas de diagnostico

```python
# Verificar que el puerto este disponible antes de iniciar
def check_port_before_start(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(("", port))
        return True
    except OSError as e:
        logger.error(f"Puerto {port} no disponible: {e}")
        return False
    finally:
        s.close()

# Log de trafico de red para debug
def log_network_traffic(sock, max_packets=100):
    for i in range(max_packets):
        data, addr = sock.recvfrom(4096)
        logger.debug(f"Paquete {i}: {len(data)} bytes desde {addr}")
```

## Errores comunes

| Error | Causa | Solucion |
|-------|-------|----------|
| `OSError: [Errno 98] Address already in use` | Puerto ocupado | Usar `SO_REUSEADDR` o cambiar puerto |
| Zeroconf no descubre dispositivos | Firewall bloqueando multicast | Abrir puerto 5353/UDP |
| `NonUniqueNameException` | Nombre ya registrado | Agregar sufijo unico al nombre |
| Alexa no responde | Protocolo incorrecto | Verificar que Alexa soporte el tipo de servicio |
