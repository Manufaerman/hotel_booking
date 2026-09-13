from dataclasses import dataclass
from datetime import timedelta
from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP,
)
import json
from urllib.error import (
    HTTPError,
    URLError,
)
from urllib.request import (
    Request,
    urlopen,
)


API_URL = (
    "https://api.argentinadatos.com/"
    "v1/cotizaciones/dolares/blue/{fecha}"
)

FUENTE_AUTOMATICA = (
    "ArgentinaDatos · dólar blue venta"
)

DIAS_RETROCESO = 7
TIMEOUT_SEGUNDOS = 8


class CotizacionNoDisponible(Exception):
    pass


@dataclass(frozen=True)
class CotizacionBlue:
    fecha: object
    venta: Decimal
    fuente: str


def _convertir_decimal(valor):
    try:
        numero = Decimal(str(valor))

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as error:
        raise CotizacionNoDisponible(
            "La cotización recibida no es válida."
        ) from error

    if numero <= 0:
        raise CotizacionNoDisponible(
            "La cotización recibida debe ser positiva."
        )

    return numero


def _consultar_fecha(fecha):
    fecha_url = fecha.strftime(
        "%Y/%m/%d"
    )

    url = API_URL.format(
        fecha=fecha_url,
    )

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "ByColeccionCRM/1.0"
            ),
        },
    )

    try:
        with urlopen(
            request,
            timeout=TIMEOUT_SEGUNDOS,
        ) as response:
            contenido = response.read()

    except HTTPError as error:
        if error.code == 404:
            return None

        raise CotizacionNoDisponible(
            (
                "El servicio de cotización respondió "
                f"con el error {error.code}."
            )
        ) from error

    except (
        URLError,
        TimeoutError,
        OSError,
    ) as error:
        raise CotizacionNoDisponible(
            (
                "No se pudo conectar con el servicio "
                "de cotizaciones."
            )
        ) from error

    try:
        datos = json.loads(
            contenido.decode("utf-8")
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as error:
        raise CotizacionNoDisponible(
            (
                "El servicio devolvió una respuesta "
                "que no se pudo interpretar."
            )
        ) from error


    if isinstance(datos, list):
        datos = datos[0] if datos else None

    if not isinstance(datos, dict):
        return None

    venta = datos.get("venta")

    if venta in (
        None,
        "",
    ):
        return None

    return CotizacionBlue(
        fecha=fecha,
        venta=_convertir_decimal(venta),
        fuente=FUENTE_AUTOMATICA,
    )


def obtener_dolar_blue(fecha):
    if not fecha:
        raise CotizacionNoDisponible(
            "No se indicó la fecha del gasto."
        )

    ultimo_error = None

    for dias in range(
        DIAS_RETROCESO + 1
    ):
        fecha_consulta = (
            fecha - timedelta(days=dias)
        )

        try:
            cotizacion = _consultar_fecha(
                fecha_consulta
            )

        except CotizacionNoDisponible as error:
            ultimo_error = error
            break

        if cotizacion:
            return cotizacion

    if ultimo_error:
        raise ultimo_error

    raise CotizacionNoDisponible(
        (
            "No se encontró una cotización blue "
            "para la fecha indicada ni para los "
            "siete días anteriores."
        )
    )


def aplicar_conversion_gasto(
    gasto,
    cotizacion_manual=None,
):
    if gasto.pais != "AR":
        gasto.moneda = "EUR"
        gasto.cotizacion_usd = None
        gasto.importe_usd = None
        gasto.fecha_cotizacion = None
        gasto.fuente_cotizacion = ""

        return gasto

    gasto.moneda = "ARS"

    if gasto.importe is None:
        raise CotizacionNoDisponible(
            "El gasto no tiene un importe."
        )

    if cotizacion_manual not in (
        None,
        "",
    ):
        cotizacion = _convertir_decimal(
            cotizacion_manual
        )

        fecha_cotizacion = gasto.fecha
        fuente = "Cotización introducida manualmente"

    else:
        resultado = obtener_dolar_blue(
            gasto.fecha
        )

        cotizacion = resultado.venta
        fecha_cotizacion = resultado.fecha
        fuente = resultado.fuente

    gasto.cotizacion_usd = cotizacion

    gasto.importe_usd = (
        Decimal(gasto.importe)
        / cotizacion
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    gasto.fecha_cotizacion = (
        fecha_cotizacion
    )

    gasto.fuente_cotizacion = fuente

    return gasto