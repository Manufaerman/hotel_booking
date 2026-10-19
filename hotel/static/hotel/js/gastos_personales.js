document.addEventListener(
    "DOMContentLoaded",
    function () {
        const form = document.querySelector(
            "[data-personal-form]"
        );

        if (!form) {
            return;
        }

        const countrySelect = form.querySelector(
            "select[data-personal-country]"
        );

        const countryButtons = (
            form.querySelectorAll(
                ".personal-country-button"
            )
        );

        const currencyLabel = form.querySelector(
            "[data-currency-label]"
        );

        if (!countrySelect) {
            console.error(
                "No se encontró el selector de país."
            );

            return;
        }

        function seleccionarPais(pais) {
            if (
                pais !== "ES"
                && pais !== "AR"
            ) {
                pais = "ES";
            }

            countrySelect.value = pais;

            countryButtons.forEach(
                function (button) {
                    const activo = (
                        button.dataset.countryValue
                        === pais
                    );

                    button.classList.toggle(
                        "is-active",
                        activo
                    );

                    button.setAttribute(
                        "aria-pressed",
                        activo ? "true" : "false"
                    );
                }
            );

            if (currencyLabel) {
                currencyLabel.textContent = (
                    pais === "AR"
                        ? "ARS"
                        : "€"
                );
            }
        }

        countryButtons.forEach(
            function (button) {
                button.addEventListener(
                    "click",
                    function () {
                        seleccionarPais(
                            button.dataset.countryValue
                        );
                    }
                );
            }
        );

        seleccionarPais(
            countrySelect.value || "ES"
        );
    }
);