/* Court Rhythm website — small, dependency-free behaviour for every page. */
(function () {
  'use strict';

  /* Header: border after scrolling, mobile menu */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 8); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
    };
    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  /* Launch countdown — hidden when the date has passed or JS is off */
  var cd = document.querySelector('[data-countdown]');
  if (cd) {
    var target = new Date(cd.getAttribute('data-countdown')).getTime();
    var block = cd.closest('[data-countdown-block]') || cd;
    var parts = {
      d: cd.querySelector('[data-d]'), h: cd.querySelector('[data-h]'),
      m: cd.querySelector('[data-m]'), s: cd.querySelector('[data-s]')
    };
    var pad = function (n) { return String(n).padStart(2, '0'); };
    var timer;
    var tick = function () {
      var left = target - Date.now();
      if (!(left > 0)) { block.hidden = true; clearInterval(timer); return; }
      block.hidden = false;
      parts.d.textContent = pad(Math.floor(left / 864e5));
      parts.h.textContent = pad(Math.floor(left / 36e5) % 24);
      parts.m.textContent = pad(Math.floor(left / 6e4) % 60);
      parts.s.textContent = pad(Math.floor(left / 1e3) % 60);
    };
    tick();
    timer = setInterval(tick, 1000);
  }

  /* Current year in the footer */
  var y = document.querySelectorAll('[data-year]');
  for (var i = 0; i < y.length; i++) y[i].textContent = String(new Date().getFullYear());
})();
