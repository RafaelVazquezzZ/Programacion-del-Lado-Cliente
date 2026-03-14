import asyncio
import aiohttp
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

        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json"
        }

        if self._ultimo_etag:
            headers["If-None-Match"] = self._ultimo_etag

        url = f"{BASE_URL}/inventario"

        try:

            timeout = aiohttp.ClientTimeout(total=TIMEOUT)

            async with aiohttp.ClientSession(timeout=timeout) as session:

                async with session.get(url, headers=headers) as resp:

                    if resp.status == 200:

                        data = await resp.json()

                        self._ultimo_etag = resp.headers.get("ETag")

                        return data


                    elif resp.status == 304:
                        print("Inventario sin cambios")
                        return None


                    elif 400 <= resp.status < 500:
                        print("Error cliente:", resp.status)
                        return None


                    elif 500 <= resp.status < 600:
                        print("Error servidor:", resp.status)

                        self._intervalo = min(self._intervalo * 2, INTERVALO_MAX)

                        return None


        except asyncio.TimeoutError:
            print("Timeout al consultar inventario")

        except aiohttp.ClientConnectionError:
            print("Error de conexión")

        return None


    async def iniciar(self):

        self._ejecutando = True

        while self._ejecutando:

            inventario = await self._consultar_inventario()

            if inventario:

                if inventario != self._ultimo_estado:

                    print("Inventario actualizado")

                    await self._notificar(inventario)

                    self._ultimo_estado = inventario

                    # reset del intervalo si hubo cambios
                    self._intervalo = INTERVALO_BASE

                else:
                    print("Sin cambios en inventario")

                    # pequeño backoff si no hay cambios
                    self._intervalo = min(self._intervalo * 2, INTERVALO_MAX)

            await asyncio.sleep(self._intervalo)


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