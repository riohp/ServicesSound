import logging

class ServiceDiscovery:
    
    def __init__ (self, service_name="ServicesSound"):
        self.logger = logging.getLogger(__name__)
        self.service_name = service_name
        self.registered = False
    
    def register_service(self):
        """
        Registra el servicio en la red local para que otros dispositivos lo encuentren.
        
        Por ahora, esta función solo simula el registro. En versiones futuras,
        implementaremos la funcionalidad completa de Zeroconf.
        """
        if self.registered:
            self.logger.warning("El servicio ya está registrado")
            return True
        
        self.logger.info("Registrando servicio en la red...")
        # TODO: Implementar registro real con Zeroconf
        self.registered = True
        self.logger.info("Servicio registrado exitosamente (simulado)")
        return True
    
    def unregister_service(self):
        """
        Quita el registro del servicio de la red.
        
        Esta función limpia el registro cuando la aplicación se cierra.
        """
        if not self.registered:
            self.logger.warning("El servicio no está registrado")
            return
        
        self.logger.info("Quitando registro del servicio...")
        # TODO: Implementar des-registro real con Zeroconf
        self.registered = False
        self.logger.info("Servicio des-registrado exitosamente (simulado)")