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