(function() {
    const ThemeManager = {
        init() {
            this.loadTheme();
            this.createToggle();
            this.updateToggleIcon();
        },
        loadTheme() {
            const saved = localStorage.getItem("gosen-theme") || "light";
            document.documentElement.setAttribute("data-theme", saved);
            this.currentTheme = saved;
        },
        toggle() {
            const current = document.documentElement.getAttribute("data-theme");
            const newTheme = current === "light" ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("gosen-theme", newTheme);
            this.currentTheme = newTheme;
            this.updateToggleIcon();
        },
        updateToggleIcon() {
            const btn = document.querySelector('.theme-toggle');
            if (btn) {
                const span = btn.querySelector('span');
                if (span) {
                    span.textContent = this.currentTheme === 'light' ? '🌙' : '☀️';
                }
            }
        },
        createToggle() {
            // Remove existing button if any
            const existing = document.querySelector('.theme-toggle');
            if (existing) existing.remove();
            
            const btn = document.createElement("button");
            btn.className = "theme-toggle";
            btn.innerHTML = "<span>🌙</span>";
            btn.setAttribute("aria-label", "Toggle theme");
            Object.assign(btn.style, {
                position: "fixed",
                top: "70px",
                right: "20px",
                width: "50px",
                height: "50px",
                borderRadius: "50%",
                background: "var(--bg-card)",
                border: "2px solid var(--gabon-green)",
                cursor: "pointer",
                zIndex: "1001",
                fontSize: "22px",
                transition: "all 0.3s ease",
                boxShadow: "0 4px 12px rgba(0, 158, 96, 0.3)"
            });
            btn.addEventListener("mouseenter", () => {
                btn.style.transform = "scale(1.1)";
                btn.style.boxShadow = "0 6px 20px rgba(0, 158, 96, 0.5)";
            });
            btn.addEventListener("mouseleave", () => {
                btn.style.transform = "scale(1)";
                btn.style.boxShadow = "0 4px 12px rgba(0, 158, 96, 0.3)";
            });
            btn.addEventListener("click", () => this.toggle());
            document.body.appendChild(btn);
        }
    };
    
    const AnimationManager = {
        init() {
            const cards = document.querySelectorAll(".card");
            cards.forEach((card, i) => {
                card.style.opacity = "0";
                card.style.transform = "translateY(20px)";
                setTimeout(() => {
                    card.style.transition = "opacity 0.6s ease, transform 0.6s ease";
                    card.style.opacity = "1";
                    card.style.transform = "translateY(0)";
                }, i * 100);
            });
        }
    };
    
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
            ThemeManager.init();
            AnimationManager.init();
        });
    } else {
        ThemeManager.init();
        AnimationManager.init();
    }
    
    window.GosenTheme = ThemeManager;
    console.log('Theme manager loaded - current theme:', ThemeManager.currentTheme);
})();
