document.addEventListener('DOMContentLoaded', () => {
    const filters = [...document.querySelectorAll('[data-course-filter]')];
    const cards = [...document.querySelectorAll('.course-card[data-difficulty]')];
    const empty = document.querySelector('.course-empty');
    const status = document.querySelector('.catalog-filter-status');

    filters.forEach(button => button.addEventListener('click', () => {
        const difficulty = button.dataset.courseFilter;
        filters.forEach(filter => {
            const selected = filter === button;
            filter.classList.toggle('active', selected);
            filter.setAttribute('aria-pressed', String(selected));
        });
        let visible = 0;
        cards.forEach(card => {
            const show = difficulty === 'all' || card.dataset.difficulty === difficulty;
            card.hidden = !show;
            if (show) visible += 1;
        });
        if (empty) empty.hidden = visible > 0;
        if (status) status.textContent = `${visible} курс көрсетілді`;
    }));

    const nav = document.getElementById('sidebar');
    const menu = document.querySelector('.header-menu');
    if (nav && menu) {
        document.addEventListener('keydown', event => {
            if (event.key === 'Escape' && nav.classList.contains('open')) {
                nav.classList.remove('open');
                menu.setAttribute('aria-expanded', 'false');
                menu.focus();
            }
        });
        document.addEventListener('click', event => {
            if (!nav.contains(event.target) && !menu.contains(event.target)) {
                nav.classList.remove('open');
                menu.setAttribute('aria-expanded', 'false');
            }
        });
    }
});
