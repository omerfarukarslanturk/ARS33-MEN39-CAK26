document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-menu-toggle]");
    const menu = document.querySelector("[data-menu]");
    if (toggle && menu) {
        toggle.addEventListener("click", () => menu.classList.toggle("open"));
    }

    const roleSelect = document.querySelector("[data-role-select]");
    const companyField = document.querySelector("[data-company-field]");
    if (roleSelect && companyField) {
        const syncCompanyField = () => {
            companyField.classList.toggle("hidden", roleSelect.value !== "employer");
        };
        roleSelect.addEventListener("change", syncCompanyField);
        syncCompanyField();
    }
});
