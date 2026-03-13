import asyncio
from abc import ABC, abstractmethod

# CONFIGURACIÓN
BASE_URL = "http://ecomarket.local/api/v1"
TOKEN = "eyJ0eXAiO..."
INTERVALO_BASE = 5
INTERVALO_MAX = 60
TIMEOUT = 10


# INTERFAZ OBSERVADOR
class Observador(ABC):

    @abstractmethod
    async def actualizar(self, inventario):
        pass


# OBSERVABLE
class MonitorInventario:

    def __init__(self):
        self._observadores = []
        self._ultimo_etag = None
        self._ultimo_estado = None
        self._ejecutando = False
        self._intervalo = INTERVALO_BASE


    def suscribir(self, obs):
        self._observadores.append(obs)


    def desuscribir(self, obs):
        self._observadores.remove(obs)


    async def _notificar(self, inventario):

        for obs in self._observadores:
            try:
                await obs.actualizar(inventario)
            except Exception as e:
                print("Error en observador:", e)


    async def _consultar_inventario(self):
        pass


    async def iniciar(self):
        pass


    def detener(self):
        self._ejecutando = False


# OBSERVADORES
class ModuloCompras(Observador):

    async def actualizar(self, inventario):
        pass


class ModuloAlertas(Observador):

    async def actualizar(self, inventario):
        pass


# MAIN
async def main():

    monitor = MonitorInventario()

    monitor.suscribir(ModuloCompras())
    monitor.suscribir(ModuloAlertas())

    await monitor.iniciar()


if __name__ == "__main__":
    asyncio.run(main())