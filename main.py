from abc import ABC, abstractmethod  # Importa herramientas para crear clases y métodos abstractos
import logging  # Importa logging para guardar eventos y errores en un archivo de texto

# Configuración del archivo de logs para registrar eventos y errores sin usar base de datos
logging.basicConfig(
    filename="software_fj.log",  # Nombre del archivo donde se guardarán los registros
    level=logging.INFO,  # Nivel mínimo de registro (INFO y ERROR)
    format="%(asctime)s | %(levelname)s | %(message)s",  # Formato de fecha, nivel y mensaje
    encoding="utf-8",  # Codificación UTF-8 para soportar tildes y caracteres en español
)
logger = logging.getLogger("SoftwareFJ")  # Crea el objeto logger del sistema


# --- EXCEPCIONES PERSONALIZADAS ---
class ErrorSistemaFJ(Exception):
    """Excepción base del sistema Software FJ."""
    pass  # Hereda directamente de Exception sin agregar lógica extra


class ErrorValidacionCliente(ErrorSistemaFJ):
    """Se lanza cuando los datos de un cliente no cumplen las reglas de validación."""
    pass  # Excepción específica para errores en clientes


class ErrorServicio(ErrorSistemaFJ):
    """Se lanza cuando hay parámetros inválidos o el servicio no está disponible."""
    pass  # Excepción específica para errores en servicios


class ErrorReserva(ErrorSistemaFJ):
    """Se lanza cuando ocurre una operación inválida o cálculo inconsistente en reservas."""
    pass  # Excepción específica para errores en reservas


# --- CLASE ABSTRACTA GENERAL ---
class EntidadSistema(ABC):
    """Clase abstracta base para entidades generales del sistema."""

    def __init__(self, id_entidad: str):  # Constructor que recibe el identificador de la entidad
        if not id_entidad or not str(id_entidad).strip():  # Verifica que el ID no esté vacío
            raise ValueError("El ID de la entidad no puede estar vacío.")  # Lanza error si falta ID
        self._id = str(id_entidad).strip()  # Guarda el ID limpio como atributo protegido

    @property
    def id(self) -> str:  # Getter de solo lectura para el ID
        return self._id  # Retorna el identificador

    @abstractmethod
    def mostrar_info(self) -> str:  # Método abstracto que las subclases deben implementar
        """Retorna una descripción resumida de la entidad."""
        pass  # Sin implementación en la clase base


# --- CLASE CLIENTE ---
class Cliente(EntidadSistema):
    """Representa un cliente con encapsulación de datos personales y validaciones estrictas."""

    def __init__(self, id_cliente: str, nombre: str, correo: str):  # Inicializa atributos del cliente
        super().__init__(id_cliente)  # Llama al constructor de EntidadSistema para validar el ID
        self.nombre = nombre  # Usa el setter de nombre para validar
        self.correo = correo  # Usa el setter de correo para validar

    @property
    def nombre(self) -> str:  # Getter para el nombre privado
        return self.__nombre  # Retorna el nombre encapsulado

    @nombre.setter
    def nombre(self, valor: str):  # Setter que valida el nombre antes de asignarlo
        if not valor or len(valor.strip()) < 2:  # Valida que tenga al menos 2 caracteres
            raise ErrorValidacionCliente("El nombre del cliente debe tener al menos 2 caracteres.")  # Lanza excepción
        self.__nombre = valor.strip()  # Guarda el nombre limpio en atributo privado

    @property
    def correo(self) -> str:  # Getter para el correo privado
        return self.__correo  # Retorna el correo encapsulado

    @correo.setter
    def correo(self, valor: str):  # Setter que valida el formato básico del correo
        if not valor or "@" not in valor or "." not in valor.split("@")[-1]:  # Revisa '@' y dominio con punto
            raise ErrorValidacionCliente(f"Correo electrónico inválido: '{valor}'.")  # Lanza excepción personalizada
        self.__correo = valor.strip().lower()  # Guarda el correo normalizado en minúsculas

    def mostrar_info(self) -> str:  # Implementa el método abstracto de EntidadSistema
        return f"Cliente[{self.id}] - {self.nombre} ({self.correo})"  # Devuelve texto informativo del cliente


# --- CLASE ABSTRACTA SERVICIO Y SUBCLASES ---
class Servicio(ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True):  # Constructor base
        self.codigo = codigo  # Asigna código del servicio
        self.nombre = nombre  # Asigna nombre del servicio
        self.tarifa_base = tarifa_base  # Asigna tarifa base numérica
        self.disponible = disponible  # Indica si el servicio está disponible para reservar

    @abstractmethod
    def validar_parametros(self, duracion: int) -> None:  # Valida parámetros específicos de cada servicio
        pass  # Implementado en cada clase hija

    @abstractmethod
    def describir(self) -> str:  # Describe el servicio (polimorfismo)
        pass  # Implementado en cada clase hija

    @abstractmethod
    def calcular_costo(self, duracion: int, descuento: float = 0.0, aplicar_iva: bool = True) -> float:  # Sobrecarga vía opcionales
        pass  # Implementado en cada clase hija

    def _calcular_total_con_ajustes(self, subtotal: float, descuento: float, aplicar_iva: bool) -> float:
        """Calcula subtotal con descuento e IVA y valida que el resultado sea consistente."""
        if subtotal < 0:  # Verifica que el subtotal no sea negativo
            raise ErrorReserva("Cálculo inconsistente: el subtotal no puede ser negativo.")  # Error de cálculo
        if not (0.0 <= descuento < 1.0):  # Valida que el descuento esté entre 0% y 99%
            raise ErrorReserva("Cálculo inconsistente: el descuento debe estar entre 0.0 y 0.99.")  # Error de cálculo
        con_descuento = subtotal * (1.0 - descuento)  # Aplica el porcentaje de descuento
        total = con_descuento * 1.19 if aplicar_iva else con_descuento  # Aplica IVA del 19% si corresponde
        if total <= 0:  # Verifica que el costo final sea positivo
            raise ErrorReserva("Cálculo inconsistente: el costo total debe ser mayor que cero.")  # Error de cálculo
        return round(total, 2)  # Redondea a dos decimales


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas (tarifa por hora)."""

    def __init__(self, codigo: str, nombre: str, tarifa_hora: float, capacidad: int, disponible: bool = True):
        if tarifa_hora <= 0:  # Valida que la tarifa por hora sea positiva
            raise ErrorServicio("La tarifa por hora de la sala debe ser mayor que cero.")  # Lanza error de servicio
        if capacidad <= 0:  # Valida que la capacidad de personas sea positiva
            raise ErrorServicio("La capacidad de la sala debe ser mayor que cero.")  # Lanza error de servicio
        super().__init__(codigo, nombre, tarifa_hora, disponible)  # Inicializa atributos de Servicio
        self.capacidad = capacidad  # Guarda capacidad máxima de personas

    def validar_parametros(self, duracion: int) -> None:  # Valida duración en horas
        if not self.disponible:  # Verifica disponibilidad
            raise ErrorServicio(f"La sala '{self.nombre}' no está disponible.")  # Lanza error si no está disponible
        if duracion <= 0 or duracion > 12:  # Permite reservas de 1 a 12 horas
            raise ErrorServicio("La duración de reserva de sala debe estar entre 1 y 12 horas.")  # Error de duración

    def describir(self) -> str:  # Descripción polimórfica de la sala
        return f"Sala '{self.nombre}' (Cap. {self.capacidad} pers., ${self.tarifa_base}/h)"  # Texto descriptivo

    def calcular_costo(self, duracion: int, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        self.validar_parametros(duracion)  # Valida antes de calcular
        subtotal = self.tarifa_base * duracion  # Calcula costo base por horas
        return self._calcular_total_con_ajustes(subtotal, descuento, aplicar_iva)  # Aplica descuento e IVA


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos tecnológicos (tarifa por día)."""

    def __init__(self, codigo: str, nombre: str, tarifa_dia: float, unidades: int, disponible: bool = True):
        if tarifa_dia <= 0:  # Valida tarifa diaria positiva
            raise ErrorServicio("La tarifa por día del equipo debe ser mayor que cero.")  # Lanza error de servicio
        if unidades <= 0:  # Valida cantidad de unidades disponible
            raise ErrorServicio("Las unidades del equipo deben ser mayores que cero.")  # Lanza error de servicio
        super().__init__(codigo, nombre, tarifa_dia, disponible)  # Inicializa clase padre
        self.unidades = unidades  # Guarda número de unidades

    def validar_parametros(self, duracion: int) -> None:  # Valida duración en días
        if not self.disponible:  # Revisa disponibilidad
            raise ErrorServicio(f"El equipo '{self.nombre}' no está disponible.")  # Error si no está disponible
        if duracion <= 0 or duracion > 30:  # Permite alquiler de 1 a 30 días
            raise ErrorServicio("El alquiler de equipo debe ser entre 1 y 30 días.")  # Error de duración

    def describir(self) -> str:  # Descripción polimórfica del equipo
        return f"Equipo '{self.nombre}' ({self.unidades} und., ${self.tarifa_base}/día)"  # Texto descriptivo

    def calcular_costo(self, duracion: int, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        self.validar_parametros(duracion)  # Valida antes de calcular
        subtotal = self.tarifa_base * duracion  # Calcula costo por días
        return self._calcular_total_con_ajustes(subtotal, descuento, aplicar_iva)  # Retorna total ajustado


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas (tarifa por sesión)."""

    def __init__(self, codigo: str, nombre: str, tarifa_sesion: float, especialidad: str, disponible: bool = True):
        if tarifa_sesion <= 0:  # Valida tarifa por sesión positiva
            raise ErrorServicio("La tarifa de asesoría debe ser mayor que cero.")  # Error de servicio
        if not especialidad or not especialidad.strip():  # Valida que exista especialidad
            raise ErrorServicio("La especialidad de la asesoría es obligatoria.")  # Error de especialidad
        super().__init__(codigo, nombre, tarifa_sesion, disponible)  # Inicializa clase padre
        self.especialidad = especialidad.strip()  # Guarda área de especialidad

    def validar_parametros(self, duracion: int) -> None:  # Valida número de sesiones
        if not self.disponible:  # Verifica disponibilidad
            raise ErrorServicio(f"La asesoría '{self.nombre}' no está disponible.")  # Error si no está disponible
        if duracion <= 0 or duracion > 20:  # Permite entre 1 y 20 sesiones
            raise ErrorServicio("La cantidad de sesiones debe estar entre 1 y 20.")  # Error de sesiones

    def describir(self) -> str:  # Descripción polimórfica de la asesoría
        return f"Asesoría '{self.nombre}' [{self.especialidad}] (${self.tarifa_base}/sesión)"  # Texto descriptivo

    def calcular_costo(self, duracion: int, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        self.validar_parametros(duracion)  # Valida antes de calcular
        subtotal = self.tarifa_base * duracion  # Calcula costo por sesiones
        return self._calcular_total_con_ajustes(subtotal, descuento, aplicar_iva)  # Retorna total ajustado


# --- CLASE RESERVA ---
class Reserva:
    """Integra cliente, servicio, duración y estado, gestionando su ciclo de vida."""

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
        if not isinstance(cliente, Cliente):  # Verifica que el objeto sea instancia de Cliente
            raise ErrorReserva("Se requiere un objeto Cliente válido.")  # Lanza error de reserva
        if not isinstance(servicio, Servicio):  # Verifica que el objeto sea instancia de Servicio
            raise ErrorReserva("Se requiere un objeto Servicio válido.")  # Lanza error de reserva
        self.id_reserva = id_reserva  # Identificador de la reserva
        self.cliente = cliente  # Cliente asociado
        self.servicio = servicio  # Servicio reservado
        self.duracion = duracion  # Duración (horas, días o sesiones)
        self.estado = "PENDIENTE"  # Estado inicial de la reserva
        self.costo_total = 0.0  # Costo calculado al procesar/confirmar

    def procesar(self, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        """Calcula el costo y deja la reserva lista usando try/except/else/finally y encadenamiento."""
        try:  # Bloque principal de ejecución
            if self.estado == "CANCELADA":  # Impide procesar una reserva cancelada
                raise ErrorReserva("No se puede procesar una reserva cancelada.")  # Error de operación no permitida
            self.costo_total = self.servicio.calcular_costo(self.duracion, descuento, aplicar_iva)  # Calcula costo
        except ErrorSistemaFJ as exc:  # Captura errores propios del dominio
            raise ErrorReserva(f"Fallo al procesar reserva '{self.id_reserva}'.") from exc  # Encadena excepción con 'from'
        except Exception as exc:  # Captura cualquier error inesperado (ej. TypeError)
            raise ErrorReserva(f"Error inesperado en reserva '{self.id_reserva}'.") from exc  # Encadena excepción
        else:  # Se ejecuta solo si no hubo excepciones en try
            logger.info(f"Reserva {self.id_reserva} procesada. Total: ${self.costo_total}")  # Registra éxito en log
            return self.costo_total  # Devuelve el costo calculado
        finally:  # Se ejecuta siempre, ocurra o no error
            logger.info(f"Fin de intento de procesamiento para reserva {self.id_reserva} (estado: {self.estado}).")  # Log final

    def confirmar(self) -> None:
        """Confirma la reserva si no está cancelada y su costo es válido."""
        if self.estado == "CANCELADA":  # Verifica estado actual
            raise ErrorReserva(f"No se puede confirmar la reserva {self.id_reserva}: está cancelada.")  # Error de estado
        if self.costo_total <= 0:  # Asegura que haya sido procesada con costo positivo
            self.procesar()  # Procesa automáticamente si aún no tiene costo calculado
        self.estado = "CONFIRMADA"  # Actualiza estado a confirmada
        logger.info(f"Reserva {self.id_reserva} CONFIRMADA para {self.cliente.nombre}.")  # Registra confirmación

    def cancelar(self) -> None:
        """Cancela la reserva si aún no estaba cancelada."""
        if self.estado == "CANCELADA":  # Evita cancelar dos veces
            raise ErrorReserva(f"Operación no permitida: la reserva {self.id_reserva} ya está cancelada.")  # Error
        self.estado = "CANCELADA"  # Cambia el estado a cancelada
        logger.info(f"Reserva {self.id_reserva} CANCELADA.")  # Registra cancelación


# --- SIMULACIÓN DE 10 OPERACIONES EN MEMORIA ---
def ejecutar_simulacion():
    clientes = []  # Lista en memoria para clientes (sin base de datos)
    servicios = []  # Lista en memoria para servicios (sin base de datos)
    reservas = []  # Lista en memoria para reservas (sin base de datos)

    def registrar_operacion(numero: int, descripcion: str, accion):  # Helper para correr cada operación sin detener el programa
        try:  # Intenta ejecutar la operación
            resultado = accion()  # Ejecuta la función pasada
            print(f"[OP {numero:02d} - OK] {descripcion} -> {resultado}")  # Muestra éxito en consola
        except Exception as err:  # Captura cualquier excepción controlada
            logger.error(f"OP {numero:02d} | {descripcion} | Error: {err} | Causa: {err.__cause__}")  # Guarda en log
            print(f"[OP {numero:02d} - ERROR CONTROLADO] {descripcion} -> {err}")  # Informa sin detener el flujo

    # 1. Registro válido de cliente
    registrar_operacion(1, "Registrar cliente válido", lambda: (
        c1 := Cliente("CLI-01", "Laura Gómez", "laura@correo.com"),
        clientes.append(c1),
        c1.mostrar_info(),
    )[-1])

    # 2. Registro inválido de cliente (correo sin '@')
    registrar_operacion(2, "Registrar cliente con correo inválido", lambda: (
        c_bad := Cliente("CLI-02", "Carlos Ruiz", "carlos.correo.com"),
        clientes.append(c_bad),
    )[-1])

    # 3. Creación correcta de servicio: Reserva de sala
    registrar_operacion(3, "Crear servicio ReservaSala válido", lambda: (
        s1 := ReservaSala("SRV-01", "Sala Ejecutiva A", 50000, 12, disponible=True),
        servicios.append(s1),
        s1.describir(),
    )[-1])

    # 4. Creación incorrecta de servicio: tarifa negativa
    registrar_operacion(4, "Crear servicio AlquilerEquipo con tarifa inválida", lambda: (
        s_bad := AlquilerEquipo("SRV-02", "Laptop Pro", -15000, 5),
        servicios.append(s_bad),
    )[-1])

    # 5. Creación correcta de servicio: Asesoría especializada (no disponible para probar fallo de reserva)
    registrar_operacion(5, "Crear servicio AsesoriaEspecializada no disponible", lambda: (
        s2 := AsesoriaEspecializada("SRV-03", "Arquitectura Cloud", 120000, "Cloud", disponible=False),
        servicios.append(s2),
        s2.describir(),
    )[-1])

    # 6. Reserva exitosa con descuento e IVA
    registrar_operacion(6, "Crear y confirmar reserva válida con 10% descuento", lambda: (
        r1 := Reserva("RES-01", clientes[0], servicios[0], duracion=3),
        r1.procesar(descuento=0.10, aplicar_iva=True),
        r1.confirmar(),
        reservas.append(r1),
        f"Estado={r1.estado}, Total=${r1.costo_total}",
    )[-1])

    # 7. Reserva fallida por servicio no disponible (encadena excepción)
    registrar_operacion(7, "Intentar reservar asesoría no disponible", lambda: (
        r2 := Reserva("RES-02", clientes[0], servicios[1], duracion=2),
        r2.procesar(),
    )[-1])

    # 8. Reserva fallida por duración inválida (0 horas)
    registrar_operacion(8, "Intentar reservar sala con duración 0", lambda: (
        r3 := Reserva("RES-03", clientes[0], servicios[0], duracion=0),
        r3.procesar(),
    )[-1])

    # 9. Cancelación válida de reserva existente
    registrar_operacion(9, "Cancelar reserva RES-01", lambda: (
        reservas[0].cancelar(),
        f"Nuevo estado={reservas[0].estado}",
    )[-1])

    # 10. Operación fallida por intentar cancelar una reserva ya cancelada
    registrar_operacion(10, "Intentar cancelar nuevamente RES-01", lambda: (
        reservas[0].cancelar(),
    )[-1])

    print("\nSimulación finalizada. Revisa 'software_fj.log' para ver el historial de eventos y errores.")  # Aviso final


if __name__ == "__main__":  # Punto de entrada principal del script
    ejecutar_simulacion()  # Ejecuta las 10 operaciones al correr el archivo