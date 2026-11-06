// Menu mobile
document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".menu-toggle");
    const menu = document.querySelector(".menu");
    if (toggle && menu) {
        toggle.addEventListener("click", () => {
            menu.classList.toggle("aberto");
            const aberto = menu.classList.contains("aberto");
            toggle.setAttribute("aria-expanded", aberto);
        });
    }
});