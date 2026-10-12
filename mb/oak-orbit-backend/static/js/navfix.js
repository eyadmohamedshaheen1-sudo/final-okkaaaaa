/* navfix.js -- shows the "Back to store / Sign out" bar whenever the embedded
   admin console is open. (The buttons themselves are wired in app.js via
   data-fn="adminback" / data-fn="adminlogout".) */
(function () {
  function wireAdminBar() {
    var root = document.getElementById('admin-root'), bar = document.getElementById('admin-bar');
    if (!root || !bar) return;
    var sync = function () { bar.classList.toggle('hide', root.classList.contains('hide')); };
    new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ['class'] });
    sync();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wireAdminBar);
  else wireAdminBar();
})();
