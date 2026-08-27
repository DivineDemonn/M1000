/* =========================================================
   M1000 — MAIN JAVASCRIPT
   Premium Netflix-style Yellow + Black UI
   File: static/js/app.js
========================================================= */

"use strict";


/* =========================================================
   DOM READY
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initPageLoader();

    initMobileSearch();

    initMobileMenu();

    initCurrentYear();

    initImageFallback();

});


/* =========================================================
   PAGE LOADER
========================================================= */

function initPageLoader() {

    const loader = document.getElementById("pageLoader");

    if (!loader) {
        return;
    }

    window.addEventListener("load", () => {

        setTimeout(() => {

            loader.classList.add("hidden");

            setTimeout(() => {
                loader.style.display = "none";
            }, 350);

        }, 250);

    });

}


/* =========================================================
   MOBILE SEARCH
========================================================= */

function initMobileSearch() {

    const searchButton =
        document.getElementById("mobileSearchButton");

    const searchPanel =
        document.getElementById("mobileSearchPanel");

    if (!searchButton || !searchPanel) {
        return;
    }


    searchButton.addEventListener("click", () => {

        const isOpen =
            searchPanel.classList.contains("active");


        if (isOpen) {

            closeMobileSearch();

        } else {

            openMobileSearch();

        }

    });


    /* Close search when pressing Escape */

    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {

            closeMobileSearch();

        }

    });


    /* Close search when clicking outside */

    document.addEventListener("click", (event) => {

        const clickedInsidePanel =
            searchPanel.contains(event.target);

        const clickedButton =
            searchButton.contains(event.target);


        if (
            searchPanel.classList.contains("active") &&
            !clickedInsidePanel &&
            !clickedButton
        ) {

            closeMobileSearch();

        }

    });

}


/* =========================================================
   OPEN MOBILE SEARCH
========================================================= */

function openMobileSearch() {

    const searchButton =
        document.getElementById("mobileSearchButton");

    const searchPanel =
        document.getElementById("mobileSearchPanel");


    if (!searchButton || !searchPanel) {
        return;
    }


    searchPanel.classList.add("active");

    searchPanel.setAttribute(
        "aria-hidden",
        "false"
    );

    searchButton.setAttribute(
        "aria-expanded",
        "true"
    );


    /* Focus search input */

    const input =
        searchPanel.querySelector(
            'input[name="q"]'
        );


    if (input) {

        setTimeout(() => {
            input.focus();
        }, 100);

    }

}


/* =========================================================
   CLOSE MOBILE SEARCH
========================================================= */

function closeMobileSearch() {

    const searchButton =
        document.getElementById("mobileSearchButton");

    const searchPanel =
        document.getElementById("mobileSearchPanel");


    if (!searchButton || !searchPanel) {
        return;
    }


    searchPanel.classList.remove("active");

    searchPanel.setAttribute(
        "aria-hidden",
        "true"
    );

    searchButton.setAttribute(
        "aria-expanded",
        "false"
    );

}


/* =========================================================
   MOBILE MENU
========================================================= */

function initMobileMenu() {

    const menuButton =
        document.getElementById("mobileMenuButton");

    const menu =
        document.getElementById("mobileMenu");

    const closeButton =
        document.getElementById("closeMenu");

    const overlay =
        document.getElementById("menuOverlay");


    if (!menuButton || !menu) {
        return;
    }


    /* Open menu */

    menuButton.addEventListener("click", () => {

        openMobileMenu();

    });


    /* Close button */

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeMobileMenu
        );

    }


    /* Overlay */

    if (overlay) {

        overlay.addEventListener(
            "click",
            closeMobileMenu
        );

    }


    /* Escape */

    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {

            closeMobileMenu();

        }

    });

}


/* =========================================================
   OPEN MOBILE MENU
========================================================= */

function openMobileMenu() {

    const menuButton =
        document.getElementById("mobileMenuButton");

    const menu =
        document.getElementById("mobileMenu");

    const overlay =
        document.getElementById("menuOverlay");


    if (!menuButton || !menu) {
        return;
    }


    menu.classList.add("active");

    menuButton.classList.add("active");

    document.body.classList.add("menu-open");


    menu.setAttribute(
        "aria-hidden",
        "false"
    );

    menuButton.setAttribute(
        "aria-expanded",
        "true"
    );


    if (overlay) {

        overlay.classList.add("active");

        overlay.setAttribute(
            "aria-hidden",
            "false"
        );

    }

}


/* =========================================================
   CLOSE MOBILE MENU
========================================================= */

function closeMobileMenu() {

    const menuButton =
        document.getElementById("mobileMenuButton");

    const menu =
        document.getElementById("mobileMenu");

    const overlay =
        document.getElementById("menuOverlay");


    if (!menu) {
        return;
    }


    menu.classList.remove("active");


    if (menuButton) {

        menuButton.classList.remove("active");

        menuButton.setAttribute(
            "aria-expanded",
            "false"
        );

    }


    menu.setAttribute(
        "aria-hidden",
        "true"
    );


    document.body.classList.remove(
        "menu-open"
    );


    if (overlay) {

        overlay.classList.remove("active");

        overlay.setAttribute(
            "aria-hidden",
            "true"
        );

    }

}


/* =========================================================
   CLOSE MENU AFTER CLICKING A LINK
========================================================= */

document.addEventListener("click", (event) => {

    const link =
        event.target.closest(
            ".mobile-nav-link"
        );


    if (link) {

        closeMobileMenu();

    }

});


/* =========================================================
   CURRENT YEAR
========================================================= */

function initCurrentYear() {

    const year =
        new Date().getFullYear();


    document
        .querySelectorAll("[data-current-year]")
        .forEach((element) => {

            element.textContent = year;

        });

}


/* =========================================================
   IMAGE FALLBACK
========================================================= */

function initImageFallback() {

    const images =
        document.querySelectorAll(
            "img"
        );


    images.forEach((image) => {

        image.addEventListener(
            "error",
            () => {

                image.classList.add(
                    "image-error"
                );

            },
            {
                once: true
            }
        );

    });

}


/* =========================================================
   SEARCH FORM PROTECTION
========================================================= */

document.addEventListener("submit", (event) => {

    const form =
        event.target;


    if (!form.matches(
        '.desktop-search, #mobileSearchPanel form'
    )) {
        return;
    }


    const input =
        form.querySelector(
            'input[name="q"]'
        );


    if (!input) {
        return;
    }


    const query =
        input.value.trim();


    if (!query) {

        event.preventDefault();

        input.focus();

        return;

    }


    input.value = query;

});


/* =========================================================
   SMOOTH INTERNAL LINKS
========================================================= */

document.addEventListener("click", (event) => {

    const link =
        event.target.closest(
            'a[href^="#"]'
        );


    if (!link) {
        return;
    }


    const targetId =
        link.getAttribute("href");


    if (
        !targetId ||
        targetId === "#"
    ) {
        return;
    }


    const target =
        document.querySelector(
            targetId
        );


    if (!target) {
        return;
    }


    event.preventDefault();


    target.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

});


/* =========================================================
   M1000 READY
========================================================= */
