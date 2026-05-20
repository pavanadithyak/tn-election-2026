const RevealOnScroll = {
  init() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -100px 0px' });

    document.querySelectorAll('[data-reveal]').forEach(el => {
      observer.observe(el);
    });
  }
};

const DashboardToggle = {
  init() {
    const buttons = document.querySelectorAll('[data-dashboard-btn]');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const view = btn.getAttribute('data-dashboard-btn');
        document.querySelectorAll('[data-dashboard-view]').forEach(v => {
          v.style.display = 'none';
        });
        const target = document.querySelector(`[data-dashboard-view="${view}"]`);
        if (target) target.style.display = 'block';
      });
    });
  }
};

const MobileNav = {
  init() {
    const navItems = document.querySelectorAll('[data-nav-item]');
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        navItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });
  }
};

const MapInteraction = {
  init() {
    const mapContainer = document.querySelector('[data-map-container]');
    if (!mapContainer) return;
    const pins = mapContainer.querySelectorAll('[data-map-pin]');
    pins.forEach(pin => {
      pin.addEventListener('click', () => {
        const pinName = pin.getAttribute('data-map-pin');
        const event = new CustomEvent('pinSelected', { detail: { region: pinName } });
        document.dispatchEvent(event);
      });
    });
  }
};

const Parallax = {
  init() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    if (!parallaxElements.length) return;
    window.addEventListener('scroll', () => {
      parallaxElements.forEach(el => {
        const scrollPos = window.pageYOffset;
        const speed = parseFloat(el.getAttribute('data-parallax')) || 0.1;
        el.style.transform = `translateY(${scrollPos * speed}px)`;
      });
    });
  }
};

const VoteShareHover = {
  init() {
    const rows = document.querySelectorAll('.vote-share-row');
    rows.forEach(row => {
      row.addEventListener('mouseover', () => {
        rows.forEach(r => { if (r !== row) r.style.opacity = '0.5'; });
        row.style.opacity = '1';
      });
      row.addEventListener('mouseout', () => {
        rows.forEach(r => r.style.opacity = '1');
      });
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  RevealOnScroll.init();
  DashboardToggle.init();
  MobileNav.init();
  MapInteraction.init();
  Parallax.init();
  VoteShareHover.init();
});
