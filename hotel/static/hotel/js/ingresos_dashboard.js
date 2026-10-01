document.addEventListener("DOMContentLoaded", () => {

    const dashboard = document.querySelector(
        ".ingresos-dashboard"
    );

    if (!dashboard) {
        return;
    }


    // ---------------------------------------------
    // Animación de entrada
    // ---------------------------------------------

    const cards = dashboard.querySelectorAll(
        ".ingreso-kpi, " +
        ".ingreso-property-card, " +
        ".ingreso-room-row, " +
        ".ingreso-temporal-row"
    );

    cards.forEach((card, index) => {

        card.style.opacity = "0";
        card.style.transform = "translateY(10px)";
        card.style.transition =
            "opacity 420ms ease, transform 420ms ease";

        window.setTimeout(() => {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, 70 * index);
    });


    // ---------------------------------------------
    // Botón añadir ingreso
    // ---------------------------------------------

    const addButton = dashboard.querySelector(
        ".ingresos-add-button"
    );

    if (addButton) {
        addButton.addEventListener("click", () => {
            addButton.classList.add("is-loading");
        });
    }


    // ---------------------------------------------
    // Tarjeta de gastos normales
    // ---------------------------------------------

   const gastosCard = dashboard.querySelector(
    "[data-gastos-toggle]"
);

const gastosDetalle = dashboard.querySelector(
    "#detalle-gastos-recurrentes"
);

const detalleButton = dashboard.querySelector(
    "[data-open-gastos-detail]"
);

const gastosImporte = dashboard.querySelector(
    "[data-gastos-importe]"
);

const gastosDescripcion = dashboard.querySelector(
    "[data-gastos-descripcion]"
);

const flujoImporte = dashboard.querySelector(
    "[data-flujo-importe]"
);

const flujoDescripcion = dashboard.querySelector(
    "[data-flujo-descripcion]"
);

if (gastosCard) {

    gastosCard.addEventListener("click", (event) => {

        if (
            event.target.closest(
                "[data-open-gastos-detail]"
            )
        ) {
            return;
        }

        const estadoActual =
            gastosCard.dataset.estado;

        const mostrarReal =
            estadoActual === "previsto";

        gastosCard.dataset.estado =
            mostrarReal ? "real" : "previsto";

        if (mostrarReal) {

            gastosImporte.textContent =
                `${gastosCard.dataset.gastosReales} €`;

            gastosDescripcion.textContent =
                "Gastos reales del mes";

            if (flujoImporte) {
                flujoImporte.textContent =
                    `${gastosCard.dataset.flujoReal} €`;
            }

            if (flujoDescripcion) {
                flujoDescripcion.textContent =
                    "Ingresos menos gastos reales y préstamos";
            }

        } else {

            gastosImporte.textContent =
                `${gastosCard.dataset.gastosPrevistos} €`;

            gastosDescripcion.textContent =
                "Recurrentes prorrateados y gastos puntuales";

            if (flujoImporte) {
                flujoImporte.textContent =
                    `${gastosCard.dataset.flujoPrevisto} €`;
            }

            if (flujoDescripcion) {
                flujoDescripcion.textContent =
                    "Ingresos menos gastos previstos y préstamos";
            }
        }
    });
}


if (detalleButton && gastosDetalle) {

    detalleButton.addEventListener("click", (event) => {

        event.stopPropagation();

        gastosDetalle.hidden = false;

        gastosDetalle.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    });
}


    // ---------------------------------------------
    // Pestañas del detalle
    // ---------------------------------------------

    const tabs = dashboard.querySelectorAll(
        "[data-gastos-tab]"
    );

    const panels = dashboard.querySelectorAll(
        "[data-gastos-panel]"
    );

    tabs.forEach((button) => {

        button.addEventListener("click", () => {

            const tabSeleccionada =
                button.dataset.gastosTab;

            tabs.forEach((item) => {
                item.classList.toggle(
                    "is-active",
                    item === button
                );
            });

            panels.forEach((panel) => {
                panel.hidden = (
                    panel.dataset.gastosPanel
                    !== tabSeleccionada
                );
            });
        });
    });

});