/* =========================================================
   M1000 — PREMIUM STREAMING UI
   Black + Gold / Yellow Cinematic Theme

   File:
   static/js/app.js
========================================================= */

"use strict";


/* =========================================================
   1. DOM READY
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initMobileMenu();
    initMobileSearch();
    initImageFallback();
    initEscapeKey();
    initMenuLinks();
    initSearchEnhancements();
    initLazyImages();

});


/* =========================================================
   2. MOBILE MENU
========================================================= */

function initMobileMenu() {

    const menuButton = document.getElementById("mobile-menu-button");
    const mobileMenu = document.getElementById("mobile-menu");
    const closeButton = document.getElementById("close-menu");

    if (!menuButton || !mobileMenu) {
        return;
    }

    function openMenu() {

        mobileMenu.classList.add("active");

        menuButton.classList.add("active");

        menuButton.setAttribute(
            "aria-expanded",
            "true"
        );

        document.body.classList.add("menu-open");

    }


    function closeMenu() {

        mobileMenu.classList.remove("active");

        menuButton.classList.remove("active");

        menuButton.setAttribute(
            "aria-expanded",
            "false"
        );

        document.body.classList.remove("menu-open");

    }


    function toggleMenu() {

        const isOpen =
            mobileMenu.classList.contains("active");

        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }

    }


    menuButton.addEventListener(
        "click",
        toggleMenu
    );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeMenu
        );

    }


    /*
     * Close when clicking outside the menu.
     */

    document.addEventListener(
        "click",
        (event) => {

            if (!mobileMenu.classList.contains("active")) {
                return;
            }

            const clickedInsideMenu =
                mobileMenu.contains(event.target);

            const clickedButton =
                menuButton.contains(event.target);

            if (!clickedInsideMenu && !clickedButton) {
                closeMenu();
            }

        }
    );


    /*
     * Expose functions globally if needed.
     */

    window.M1000Menu = {
        open: openMenu,
        close: closeMenu,
        toggle: toggleMenu
    };

}


/* =========================================================
   3. MOBILE SEARCH
========================================================= */

function initMobileSearch() {

    const searchButton =
        document.getElementById(
            "mobile-search-button"
        );

    const searchPanel =
        document.getElementById(
            "mobile-search-panel"
        );

    if (!searchButton || !searchPanel) {
        return;
    }


    function openSearch() {

        searchPanel.classList.add("active");

        searchButton.setAttribute(
            "aria-expanded",
            "true"
        );

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


    function closeSearch() {

        searchPanel.classList.remove("active");

        searchButton.setAttribute(
            "aria-expanded",
            "false"
        );

    }


    function toggleSearch() {

        const isOpen =
            searchPanel.classList.contains("active");

        if (isOpen) {
            closeSearch();
        } else {
            openSearch();
        }

    }


    searchButton.addEventListener(
        "click",
        toggleSearch
    );


    /*
     * Expose search controls.
     */

    window.M1000Search = {
        open: openSearch,
        close: closeSearch,
        toggle: toggleSearch
    };

}


/* =========================================================
   4. ESCAPE KEY
========================================================= */

function initEscapeKey() {

    document.addEventListener(
        "keydown",
        (event) => {

            if (event.key !== "Escape") {
                return;
            }


            /*
             * Close mobile menu.
             */

            const mobileMenu =
                document.getElementById(
                    "mobile-menu"
                );

            const menuButton =
                document.getElementById(
                    "mobile-menu-button"
                );

            if (
                mobileMenu &&
                mobileMenu.classList.contains("active")
            ) {

                mobileMenu.classList.remove(
                    "active"
                );

                if (menuButton) {

                    menuButton.classList.remove(
                        "active"
                    );

                    menuButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

                document.body.classList.remove(
                    "menu-open"
                );

            }


            /*
             * Close mobile search.
             */

            const searchPanel =
                document.getElementById(
                    "mobile-search-panel"
                );

            const searchButton =
                document.getElementById(
                    "mobile-search-button"
                );

            if (
                searchPanel &&
                searchPanel.classList.contains("active")
            ) {

                searchPanel.classList.remove(
                    "active"
                );

                if (searchButton) {

                    searchButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }

        }
    );

}


/* =========================================================
   5. MOBILE MENU LINKS
========================================================= */

function initMenuLinks() {

    const mobileMenu =
        document.getElementById(
            "mobile-menu"
        );

    if (!mobileMenu) {
        return;
    }


    const links =
        mobileMenu.querySelectorAll(
            "a"
        );


    links.forEach((link) => {

        link.addEventListener(
            "click",
            () => {

                mobileMenu.classList.remove(
                    "active"
                );

                const menuButton =
                    document.getElementById(
                        "mobile-menu-button"
                    );

                if (menuButton) {

                    menuButton.classList.remove(
                        "active"
                    );

                    menuButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

                document.body.classList.remove(
                    "menu-open"
                );

            }
        );

    });

}


/* =========================================================
   6. SEARCH ENHANCEMENTS
========================================================= */

function initSearchEnhancements() {

    const searchForms =
        document.querySelectorAll(
            'form[action*="search"]'
        );


    searchForms.forEach((form) => {

        const input =
            form.querySelector(
                'input[name="q"]'
            );


        if (!input) {
            return;
        }


        /*
         * Prevent empty searches.
         */

        form.addEventListener(
            "submit",
            (event) => {

                const value =
                    input.value.trim();


                if (!value) {

                    event.preventDefault();

                    input.focus();

                    input.classList.add(
                        "search-invalid"
                    );


                    setTimeout(() => {

                        input.classList.remove(
                            "search-invalid"
                        );

                    }, 700);

                }

            }
        );


        /*
         * Remove invalid state when typing.
         */

        input.addEventListener(
            "input",
            () => {

                input.classList.remove(
                    "search-invalid"
                );

            }
        );

    });

}


/* =========================================================
   7. IMAGE FALLBACK
========================================================= */

function initImageFallback() {

    const images =
        document.querySelectorAll(
            "img"
        );


    images.forEach((image) => {

        /*
         * Prevent attaching the handler twice.
         */

        if (
            image.dataset.fallbackReady === "true"
        ) {
            return;
        }


        image.dataset.fallbackReady = "true";


        image.addEventListener(
            "error",
            () => {

                /*
                 * Don't repeatedly trigger
                 * the error event.
                 */

                image.onerror = null;


                /*
                 * Logo fallback.
                 */

                if (
                    image.classList.contains(
                        "brand-logo"
                    )
                ) {

                    image.style.display = "none";

                    return;

                }


                /*
                 * Poster / general image fallback.
                 */

                image.classList.add(
                    "image-error"
                );


                /*
                 * Keep broken images visually
                 * clean instead of showing the
                 * browser's broken-image icon.
                 */

                image.style.opacity = "0";


                const parent =
                    image.parentElement;


                if (parent) {

                    parent.classList.add(
                        "image-error"
                    );

                }

            }
        );

    });

}


/* =========================================================
   8. LAZY LOADING
========================================================= */

function initLazyImages() {

    const images =
        document.querySelectorAll(
            "img"
        );


    images.forEach((image) => {

        /*
         * Do not override explicitly eager images.
         */

        if (
            image.loading !== "eager"
        ) {

            image.loading = "lazy";

        }


        /*
         * Improve decoding performance.
         */

        image.decoding = "async";

    });

}


/* =========================================================
   9. SMOOTH ANCHOR SCROLL
========================================================= */

function initSmoothAnchors() {

    const links =
        document.querySelectorAll(
            'a[href^="#"]'
        );


    links.forEach((link) => {

        link.addEventListener(
            "click",
            (event) => {

                const targetId =
                    link.getAttribute(
                        "href"
                    );


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

            }
        );

    });

}


/* =========================================================
   10. CARD TOUCH SUPPORT
========================================================= */

function initCardTouch() {

    const cards =
        document.querySelectorAll(
            ".movie-card"
        );


    cards.forEach((card) => {

        card.addEventListener(
            "touchstart",
            () => {

                card.classList.add(
                    "touch-active"
                );

            },
            {
                passive: true
            }
        );


        card.addEventListener(
            "touchend",
            () => {

                setTimeout(() => {

                    card.classList.remove(
                        "touch-active"
                    );

                }, 150);

            },
            {
                passive: true
            }
        );

    });

}


/* =========================================================
   11. DOWNLOAD BUTTON FEEDBACK
========================================================= */

function initDownloadButtons() {

    const buttons =
        document.querySelectorAll(
            ".btn-download"
        );


    buttons.forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                /*
                 * Small visual feedback.
                 */

                button.classList.add(
                    "download-clicked"
                );


                setTimeout(() => {

                    button.classList.remove(
                        "download-clicked"
                    );

                }, 500);

            }
        );

    });

}


/* =========================================================
   12. CURRENT YEAR
========================================================= */

function setCurrentYear() {

    const yearElements =
        document.querySelectorAll(
            "[data-current-year]"
        );


    if (!yearElements.length) {
        return;
    }


    const year =
        new Date().getFullYear();


    yearElements.forEach((element) => {

        element.textContent = year;

    });

}


/* =========================================================
   13. NETWORK STATUS
========================================================= */

function initNetworkStatus() {

    function updateNetworkStatus() {

        document.documentElement.classList.toggle(
            "offline",
            !navigator.onLine
        );

    }


    window.addEventListener(
        "online",
        updateNetworkStatus
    );


    window.addEventListener(
        "offline",
        updateNetworkStatus
    );


    updateNetworkStatus();

}


/* =========================================================
   14. VIEWPORT RESPONSIVENESS
========================================================= */

function initResponsiveCleanup() {

    const mobileBreakpoint =
        1000;


    function checkViewport() {

        if (
            window.innerWidth >
            mobileBreakpoint
        ) {

            const menu =
                document.getElementById(
                    "mobile-menu"
                );

            const menuButton =
                document.getElementById(
                    "mobile-menu-button"
                );

            const searchPanel =
                document.getElementById(
                    "mobile-search-panel"
                );

            const searchButton =
                document.getElementById(
                    "mobile-search-button"
                );


            if (menu) {
                menu.classList.remove(
                    "active"
                );
            }


            if (menuButton) {

                menuButton.classList.remove(
                    "active"
                );

                menuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }


            if (searchPanel) {

                searchPanel.classList.remove(
                    "active"
                );

            }


            if (searchButton) {

                searchButton.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }


            document.body.classList.remove(
                "menu-open"
            );

        }

    }


    window.addEventListener(
        "resize",
        checkViewport
    );

}


/* =========================================================
   15. INITIALIZE OPTIONAL FEATURES
========================================================= */

initSmoothAnchors();
initCardTouch();
initDownloadButtons();
setCurrentYear();
initNetworkStatus();
initResponsiveCleanup();


/* =========================================================
   16. M1000 GLOBAL API
========================================================= */

window.M1000 = {

    version: "1.0.0",

    /*
     * Simple helper for future templates.
     */

    scrollToTop() {

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    },


    /*
     * Show a temporary message.
     */

    notify(message, duration = 2500) {

        if (!message) {
            return;
        }


        let notification =
            document.getElementById(
                "m1000-notification"
            );


        if (!notification) {

            notification =
                document.createElement(
                    "div"
                );

            notification.id =
                "m1000-notification";


            notification.setAttribute(
                "role",
                "status"
            );


            notification.style.position =
                "fixed";

            notification.style.left =
                "50%";

            notification.style.bottom =
                "25px";

            notification.style.transform =
                "translateX(-50%) translateY(20px)";

            notification.style.zIndex =
                "9999";

            notification.style.padding =
                "12px 18px";

            notification.style.border =
                "1px solid rgba(255,212,0,.25)";

            notification.style.borderRadius =
                "8px";

            notification.style.background =
                "rgba(10,10,10,.96)";

            notification.style.color =
                "#fff";

            notification.style.fontSize =
                "12px";

            notification.style.fontWeight =
                "700";

            notification.style.boxShadow =
                "0 10px 35px rgba(0,0,0,.6)";

            notification.style.opacity =
                "0";

            notification.style.pointerEvents =
                "none";

            notification.style.transition =
                "opacity .25s ease, transform .25s ease";


            document.body.appendChild(
                notification
            );

        }


        notification.textContent =
            message;


        requestAnimationFrame(() => {

            notification.style.opacity =
                "1";

            notification.style.transform =
                "translateX(-50%) translateY(0)";

        });


        clearTimeout(
            notification._timeout
        );


        notification._timeout =
            setTimeout(() => {

                notification.style.opacity =
                    "0";

                notification.style.transform =
                    "translateX(-50%) translateY(20px)";

            }, duration);

    }

};


/* =========================================================
   M1000 APP.JS READY
========================================================= */
