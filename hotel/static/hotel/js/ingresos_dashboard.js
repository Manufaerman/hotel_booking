document.addEventListener("DOMContentLoaded", () => {
    const dashboard = document.querySelector(".ingresos-dashboard");

    if (!dashboard) {
        return;
    }

    const cards = dashboard.querySelectorAll(
        ".ingreso-kpi, .ingreso-property-card, " +
        ".ingreso-room-row, .ingreso-temporal-row"
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

    const addButton = dashboard.querySelector(
        ".ingresos-add-button"
    );

    if (addButton) {
        addButton.addEventListener("click", () => {
            addButton.classList.add("is-loading");
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector(
        "[data-toggle-recurrentes]"
    );

    const detail = document.querySelector(
        "#detalle-gastos-recurrentes"
    );

    if (!button || !detail) {
        return;
    }

    button.addEventListener("click", () => {
        const abierto = button.getAttribute(
            "aria-expanded"
        ) === "true";

        button.setAttribute(
            "aria-expanded",
            String(!abierto)
        );

        detail.hidden = abierto;

        if (!abierto) {
            window.setTimeout(() => {
                detail.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            }, 80);
        }
    });
});

document.querySelectorAll(
    "[data-gastos-tab]"
).forEach((button) => {
    button.addEventListener("click", () => {

        const tab = button.dataset.gastosTab;

        document.querySelectorAll(
            "[data-gastos-tab]"
        ).forEach((item) => {
            item.classList.toggle(
                "is-active",
                item === button
            );
        });

        document.querySelectorAll(
            "[data-gastos-panel]"
        ).forEach((panel) => {
            panel.hidden = (
                panel.dataset.gastosPanel !== tab
            );
        });
    });
});