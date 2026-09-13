document.addEventListener("DOMContentLoaded", function () {
    const dashboard = document.getElementById(
        "gastos-dashboard"
    );

    if (!dashboard) {
        return;
    }

    const currency = (
        dashboard.dataset.moneda || "EUR"
    ).toUpperCase();

    const locale = currency === "USD"
        ? "es-AR"
        : "es-ES";


    /* =====================================================
       UTILIDADES
    ===================================================== */

    function readJson(id) {
        const element =
            document.getElementById(id);

        if (!element) {
            return [];
        }

        try {
            return JSON.parse(
                element.textContent
            );

        } catch (error) {
            console.warn(
                "No se pudo leer:",
                id,
                error
            );

            return [];
        }
    }


    function formatCurrency(value) {
        const numericValue =
            Number(value) || 0;

        return new Intl.NumberFormat(
            locale,
            {
                style: "currency",
                currency: currency,
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }
        ).format(numericValue);
    }


    function hasValues(values) {
        return (
            Array.isArray(values)
            && values.some(function (value) {
                return Number(value) !== 0;
            })
        );
    }


    /* =====================================================
       CONFIGURACIÓN COMÚN
    ===================================================== */

    const textColor = "#51343e";
    const softTextColor = "#786d71";
    const gridColor = "rgba(81, 52, 62, 0.08)";
    const chartBorder = "#fffdf9";


    function tooltipLabel(context) {
        return (
            context.label
            + ": "
            + formatCurrency(context.raw)
        );
    }


    /* =====================================================
       GRÁFICO CIRCULAR
    ===================================================== */

    function createDoughnutChart(config) {
        if (typeof Chart === "undefined") {
            console.warn(
                "Chart.js no está disponible."
            );

            return;
        }

        const canvas =
            document.getElementById(
                config.canvasId
            );

        if (
            !canvas
            || !Array.isArray(config.labels)
            || !config.labels.length
            || !hasValues(config.values)
        ) {
            return;
        }

        new Chart(
            canvas,
            {
                type: "doughnut",

                data: {
                    labels: config.labels,

                    datasets: [
                        {
                            data: config.values,
                            backgroundColor:
                                config.colors,
                            borderColor:
                                chartBorder,
                            borderWidth: 4,
                            hoverOffset: 8,
                        },
                    ],
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "64%",

                    interaction: {
                        intersect: false,
                        mode: "nearest",
                    },

                    plugins: {
                        legend: {
                            position: "bottom",

                            labels: {
                                usePointStyle: true,
                                pointStyle: "circle",
                                padding: 16,
                                color: textColor,

                                font: {
                                    size: 12,
                                    weight: "600",
                                },
                            },
                        },

                        tooltip: {
                            callbacks: {
                                label: tooltipLabel,
                            },
                        },
                    },
                },
            }
        );
    }


    /* =====================================================
       GRÁFICO DE PREVISIÓN
    ===================================================== */

    function createExpectedChart() {
        if (typeof Chart === "undefined") {
            return;
        }

        const canvas =
            document.getElementById(
                "gastos-chart-esperado"
            );

        if (!canvas) {
            return;
        }

        const labels = readJson(
            "grafico-esperado-labels"
        );

        const expectedValues = readJson(
            "grafico-esperado-valores"
        );

        const actualValues = readJson(
            "grafico-esperado-reales"
        );

        if (
            !labels.length
            || (
                !hasValues(expectedValues)
                && !hasValues(actualValues)
            )
        ) {
            return;
        }

        new Chart(
            canvas,
            {
                type: "bar",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            label: "Esperado",
                            data: expectedValues,
                            backgroundColor:
                                "#c9a7ad",
                            borderColor:
                                "#a77f89",
                            borderWidth: 1,
                            borderRadius: 8,
                            borderSkipped: false,
                            maxBarThickness: 44,
                        },
                        {
                            label: "Gastado",
                            data: actualValues,
                            backgroundColor:
                                "#51343e",
                            borderColor:
                                "#422333",
                            borderWidth: 1,
                            borderRadius: 8,
                            borderSkipped: false,
                            maxBarThickness: 44,
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

                    scales: {
                        y: {
                            beginAtZero: true,

                            ticks: {
                                color: softTextColor,

                                callback: function (
                                    value
                                ) {
                                    return formatCurrency(
                                        value
                                    );
                                },
                            },

                            grid: {
                                color: gridColor,
                            },
                        },

                        x: {
                            ticks: {
                                color: textColor,
                                maxRotation: 30,
                                minRotation: 0,
                            },

                            grid: {
                                display: false,
                            },
                        },
                    },

                    plugins: {
                        legend: {
                            position: "bottom",

                            labels: {
                                usePointStyle: true,
                                pointStyle: "circle",
                                padding: 18,
                                color: textColor,

                                font: {
                                    size: 12,
                                    weight: "600",
                                },
                            },
                        },

                        tooltip: {
                            callbacks: {
                                label: function (
                                    context
                                ) {
                                    return (
                                        context
                                            .dataset
                                            .label
                                        + ": "
                                        + formatCurrency(
                                            context.raw
                                        )
                                    );
                                },
                            },
                        },
                    },
                },
            }
        );
    }


    /* =====================================================
       CREAR LOS CUATRO GRÁFICOS
    ===================================================== */

    createExpectedChart();


    createDoughnutChart({
        canvasId: "gastos-chart-mes",

        labels: readJson(
            "grafico-mes-labels"
        ),

        values: readJson(
            "grafico-mes-valores"
        ),

        colors: readJson(
            "grafico-mes-colores"
        ),
    });


    createDoughnutChart({
        canvasId:
            "gastos-chart-mes-anterior",

        labels: readJson(
            "grafico-mes-anterior-labels"
        ),

        values: readJson(
            "grafico-mes-anterior-valores"
        ),

        colors: readJson(
            "grafico-mes-anterior-colores"
        ),
    });


    createDoughnutChart({
        canvasId: "gastos-chart-anio",

        labels: readJson(
            "grafico-anio-labels"
        ),

        values: readJson(
            "grafico-anio-valores"
        ),

        colors: readJson(
            "grafico-anio-colores"
        ),
    });


    /* =====================================================
       SLIDER DE GRÁFICOS
    ===================================================== */

    const slider =
        document.getElementById(
            "gastos-slider"
        );

    const previousButton =
        document.getElementById(
            "gastos-slider-prev"
        );

    const nextButton =
        document.getElementById(
            "gastos-slider-next"
        );

    const dotsContainer =
        document.getElementById(
            "gastos-slider-dots"
        );

    const slides = slider
        ? Array.from(
            slider.querySelectorAll(
                ".gastos-slide"
            )
        )
        : [];

    let activeSlide = 0;
    let sliderTimer = null;


    function getSlidePosition(slide) {
        if (!slider || !slide) {
            return 0;
        }

        return (
            slide.offsetLeft
            - slider.offsetLeft
        );
    }


    function scrollToSlide(index) {
        if (!slider || !slides.length) {
            return;
        }

        const safeIndex = Math.max(
            0,
            Math.min(
                index,
                slides.length - 1
            )
        );

        slider.scrollTo({
            left: getSlidePosition(
                slides[safeIndex]
            ),
            behavior: "smooth",
        });

        updateSliderState(safeIndex);
    }


    function updateSliderState(index) {
        activeSlide = index;

        if (previousButton) {
            previousButton.disabled =
                index === 0;
        }

        if (nextButton) {
            nextButton.disabled =
                index === slides.length - 1;
        }

        if (!dotsContainer) {
            return;
        }

        dotsContainer
            .querySelectorAll(
                ".gastos-slider-dot"
            )
            .forEach(function (dot, dotIndex) {
                const active =
                    dotIndex === index;

                dot.classList.toggle(
                    "is-active",
                    active
                );

                dot.setAttribute(
                    "aria-current",
                    active
                        ? "true"
                        : "false"
                );
            });
    }


    function findClosestSlide() {
        if (!slider || !slides.length) {
            return 0;
        }

        let closestIndex = 0;
        let closestDistance = Infinity;

        slides.forEach(function (slide, index) {
            const distance = Math.abs(
                getSlidePosition(slide)
                - slider.scrollLeft
            );

            if (distance < closestDistance) {
                closestDistance = distance;
                closestIndex = index;
            }
        });

        return closestIndex;
    }


    if (
        dotsContainer
        && slides.length
    ) {
        dotsContainer.innerHTML = "";

        slides.forEach(function (_, index) {
            const dot =
                document.createElement(
                    "button"
                );

            dot.type = "button";
            dot.className =
                "gastos-slider-dot";

            dot.setAttribute(
                "aria-label",
                "Ver gráfico "
                + (index + 1)
            );

            dot.addEventListener(
                "click",
                function () {
                    scrollToSlide(index);
                }
            );

            dotsContainer.appendChild(dot);
        });
    }


    if (previousButton) {
        previousButton.addEventListener(
            "click",
            function () {
                scrollToSlide(
                    activeSlide - 1
                );
            }
        );
    }


    if (nextButton) {
        nextButton.addEventListener(
            "click",
            function () {
                scrollToSlide(
                    activeSlide + 1
                );
            }
        );
    }


    if (slider && slides.length) {
        slider.addEventListener(
            "scroll",
            function () {
                window.clearTimeout(
                    sliderTimer
                );

                sliderTimer =
                    window.setTimeout(
                        function () {
                            updateSliderState(
                                findClosestSlide()
                            );
                        },
                        90
                    );
            },
            {
                passive: true,
            }
        );

        slider.addEventListener(
            "keydown",
            function (event) {
                if (event.key === "ArrowLeft") {
                    event.preventDefault();

                    scrollToSlide(
                        activeSlide - 1
                    );
                }

                if (event.key === "ArrowRight") {
                    event.preventDefault();

                    scrollToSlide(
                        activeSlide + 1
                    );
                }
            }
        );

        updateSliderState(0);
    }


    if (slides.length <= 1) {
        if (previousButton) {
            previousButton.hidden = true;
        }

        if (nextButton) {
            nextButton.hidden = true;
        }

        if (dotsContainer) {
            dotsContainer.hidden = true;
        }
    }


    /* =====================================================
       MOVIMIENTOS: CUATRO POR PÁGINA
    ===================================================== */

    const movementRows = Array.from(
        document.querySelectorAll(
            ".gastos-table tbody tr"
        )
    );

    const movementsPrevious =
        document.getElementById(
            "movimientos-prev"
        );

    const movementsNext =
        document.getElementById(
            "movimientos-next"
        );

    const movementsStatus =
        document.getElementById(
            "movimientos-page-status"
        );

    const movementsFooter =
        document.querySelector(
            ".movimientos-slider-footer"
        );

    const movementsPerPage = 4;

    const movementPages = Math.ceil(
        movementRows.length
        / movementsPerPage
    );

    let activeMovementPage = 0;


    function showMovementPage(page) {
        if (!movementRows.length) {
            return;
        }

        activeMovementPage = Math.max(
            0,
            Math.min(
                page,
                movementPages - 1
            )
        );

        const first =
            activeMovementPage
            * movementsPerPage;

        const last =
            first
            + movementsPerPage;

        movementRows.forEach(
            function (row, index) {
                row.hidden = !(
                    index >= first
                    && index < last
                );
            }
        );

        if (movementsPrevious) {
            movementsPrevious.disabled =
                activeMovementPage === 0;
        }

        if (movementsNext) {
            movementsNext.disabled = (
                activeMovementPage
                === movementPages - 1
            );
        }

        if (movementsStatus) {
            movementsStatus.textContent = (
                (first + 1)
                + "–"
                + Math.min(
                    last,
                    movementRows.length
                )
                + " de "
                + movementRows.length
            );
        }
    }


    if (movementRows.length) {
        showMovementPage(0);

        if (movementsPrevious) {
            movementsPrevious.addEventListener(
                "click",
                function () {
                    showMovementPage(
                        activeMovementPage - 1
                    );
                }
            );
        }

        if (movementsNext) {
            movementsNext.addEventListener(
                "click",
                function () {
                    showMovementPage(
                        activeMovementPage + 1
                    );
                }
            );
        }

        if (
            movementsFooter
            && movementPages <= 1
        ) {
            movementsFooter.hidden = true;
        }
    }
});