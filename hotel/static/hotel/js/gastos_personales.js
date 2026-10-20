document.addEventListener(
    "DOMContentLoaded",
    function () {
        inicializarFormularioPersonal();
        inicializarGraficosPersonales();
    }
);


/* =========================================================
   FORMULARIO: ESPAÑA / ARGENTINA
========================================================= */

function inicializarFormularioPersonal() {
    const form = document.querySelector(
        "[data-personal-form]"
    );

    /*
     * No detenemos todo el archivo si estamos
     * en el dashboard y no existe el formulario.
     */
    if (!form) {
        return;
    }

    const countrySelect = form.querySelector(
        "select[data-personal-country]"
    );

    const countryButtons = form.querySelectorAll(
        ".personal-country-button"
    );

    const currencyLabel = form.querySelector(
        "[data-currency-label]"
    );

    if (!countrySelect) {
        return;
    }

    function seleccionarPais(pais) {
        const paisSeleccionado = (
            pais === "AR" ? "AR" : "ES"
        );

        countrySelect.value = paisSeleccionado;

        countryButtons.forEach(function (button) {
            const activo = (
                button.dataset.countryValue
                === paisSeleccionado
            );

            button.classList.toggle(
                "is-active",
                activo
            );

            button.setAttribute(
                "aria-pressed",
                activo ? "true" : "false"
            );
        });

        if (currencyLabel) {
            currencyLabel.textContent = (
                paisSeleccionado === "AR"
                    ? "ARS"
                    : "€"
            );
        }

        countrySelect.dispatchEvent(
            new Event("change", {
                bubbles: true,
            })
        );
    }

    countryButtons.forEach(function (button) {
        button.addEventListener(
            "click",
            function () {
                seleccionarPais(
                    button.dataset.countryValue
                );
            }
        );
    });

    seleccionarPais(
        countrySelect.value || "ES"
    );
}


/* =========================================================
   DATOS DE LOS GRÁFICOS
========================================================= */

function leerDatosGrafico(id) {
    const element = document.getElementById(id);

    if (!element) {
        return [];
    }

    try {
        const datos = JSON.parse(
            element.textContent
        );

        return Array.isArray(datos)
            ? datos
            : [];
    } catch (error) {
        console.error(
            `No se pudieron leer los datos: ${id}`,
            error
        );

        return [];
    }
}


function convertirValores(datos) {
    return datos.map(function (valor) {
        const numero = Number(valor);

        return Number.isFinite(numero)
            ? numero
            : 0;
    });
}


/* =========================================================
   MENSAJE CUANDO NO HAY DATOS
========================================================= */

const personalEmptyChartPlugin = {
    id: "personalEmptyChart",

    afterDraw(chart) {
        const tieneDatos = chart.data.datasets.some(
            function (dataset) {
                return dataset.data.some(
                    function (valor) {
                        return Number(valor) > 0;
                    }
                );
            }
        );

        if (tieneDatos) {
            return;
        }

        const context = chart.ctx;
        const chartArea = chart.chartArea;

        if (!chartArea) {
            return;
        }

        context.save();

        context.fillStyle = "#8a7d82";
        context.font =
            '500 13px Arial, Helvetica, sans-serif';
        context.textAlign = "center";
        context.textBaseline = "middle";

        context.fillText(
            "Sin gastos registrados",
            (
                chartArea.left
                + chartArea.right
            ) / 2,
            (
                chartArea.top
                + chartArea.bottom
            ) / 2
        );

        context.restore();
    },
};


/* =========================================================
   GRÁFICOS
========================================================= */

function inicializarGraficosPersonales() {
    const evolutionCanvas = document.getElementById(
        "personalEvolutionChart"
    );

    const categoryCanvas = document.getElementById(
        "personalCategoryChart"
    );

    if (!evolutionCanvas && !categoryCanvas) {
        return;
    }

    if (typeof Chart === "undefined") {
        console.error(
            "Chart.js no se ha cargado correctamente."
        );

        return;
    }

    const formatoEuro = new Intl.NumberFormat(
        "es-ES",
        {
            style: "currency",
            currency: "EUR",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }
    );


    /* -----------------------------------------------------
       EVOLUCIÓN MENSUAL
    ----------------------------------------------------- */

    if (evolutionCanvas) {
        const labels = leerDatosGrafico(
            "personal-evolution-labels"
        );

        const valores = convertirValores(
            leerDatosGrafico(
                "personal-evolution-values"
            )
        );

        const graficoAnterior = Chart.getChart(
            evolutionCanvas
        );

        if (graficoAnterior) {
            graficoAnterior.destroy();
        }

        new Chart(
            evolutionCanvas,
            {
                type: "line",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            label: "Gastos personales",
                            data: valores,
                            borderColor: "#704456",
                            backgroundColor:
                                "rgba(112, 68, 86, 0.12)",
                            pointBackgroundColor: "#704456",
                            pointBorderColor: "#fffdf9",
                            pointBorderWidth: 2,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            borderWidth: 2.5,
                            fill: true,
                            tension: 0.35,
                        },
                    ],
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: "index",
                    },

                    plugins: {
                        legend: {
                            display: false,
                        },

                        tooltip: {
                            displayColors: false,

                            callbacks: {
                                label(context) {
                                    return formatoEuro.format(
                                        context.parsed.y || 0
                                    );
                                },
                            },
                        },
                    },

                    scales: {
                        x: {
                            grid: {
                                display: false,
                            },

                            ticks: {
                                color: "#786c70",
                                font: {
                                    size: 11,
                                },
                            },
                        },

                        y: {
                            beginAtZero: true,

                            grid: {
                                color:
                                    "rgba(81, 52, 62, 0.08)",
                            },

                            ticks: {
                                color: "#786c70",

                                callback(valor) {
                                    return formatoEuro.format(
                                        valor
                                    );
                                },
                            },
                        },
                    },
                },

                plugins: [
                    personalEmptyChartPlugin,
                ],
            }
        );
    }


    /* -----------------------------------------------------
       DISTRIBUCIÓN POR CATEGORÍA
    ----------------------------------------------------- */

    if (categoryCanvas) {
        const labels = leerDatosGrafico(
            "personal-category-labels"
        );

        const valores = convertirValores(
            leerDatosGrafico(
                "personal-category-values"
            )
        );

        const coloresBase = [
            "#704456",
            "#73a7a3",
            "#c9a6ad",
            "#bd9159",
            "#927c88",
            "#d9c589",
            "#8ea294",
            "#b97168",
            "#9d8ab0",
            "#d7b9a4",
        ];

        const colores = labels.map(
            function (_, index) {
                return coloresBase[
                    index % coloresBase.length
                ];
            }
        );

        const graficoAnterior = Chart.getChart(
            categoryCanvas
        );

        if (graficoAnterior) {
            graficoAnterior.destroy();
        }

        new Chart(
            categoryCanvas,
            {
                type: "doughnut",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            data: valores,
                            backgroundColor: colores,
                            borderColor: "#fffdf9",
                            borderWidth: 4,
                            hoverOffset: 7,
                        },
                    ],
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "66%",

                    plugins: {
                        legend: {
                            position: "bottom",

                            labels: {
                                usePointStyle: true,
                                pointStyle: "circle",
                                boxWidth: 8,
                                boxHeight: 8,
                                padding: 16,
                                color: "#5c4d52",

                                font: {
                                    size: 11,
                                },
                            },
                        },

                        tooltip: {
                            callbacks: {
                                label(context) {
                                    const etiqueta = (
                                        context.label || "Gasto"
                                    );

                                    return (
                                        `${etiqueta}: `
                                        + formatoEuro.format(
                                            context.parsed || 0
                                        )
                                    );
                                },
                            },
                        },
                    },
                },

                plugins: [
                    personalEmptyChartPlugin,
                ],
            }
        );
    }
}