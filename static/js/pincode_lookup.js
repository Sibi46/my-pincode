/* PIN code → city/area auto-lookup via India Post API
   Usage: add data-pinlookup to any pincode input
   Optional: data-fill-city="<input-id>"  — auto-fill that city input
             data-fill-state="<input-id>" — auto-fill that state input
*/
(function () {
  var cache = {};

  function lookup(pin, cb) {
    if (cache[pin]) { cb(cache[pin]); return; }
    fetch('https://api.postalpincode.in/pincode/' + pin)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var result = null;
        if (data && data[0] && data[0].Status === 'Success' && data[0].PostOffice && data[0].PostOffice.length) {
          var po = data[0].PostOffice[0];
          result = { area: po.Name, district: po.District, state: po.State };
        }
        cache[pin] = result;
        cb(result);
      })
      .catch(function () { cb(null); });
  }

  function getOrCreateHint(input) {
    var hint = input.parentElement.querySelector('.pin-hint');
    if (!hint) {
      hint = document.createElement('small');
      hint.className = 'pin-hint';
      hint.style.cssText = 'display:block;margin-top:4px;font-size:12px;font-weight:600;min-height:16px';
      input.parentElement.appendChild(hint);
    }
    return hint;
  }

  function initOne(input) {
    if (input._pinInit) return;
    input._pinInit = true;

    var hint      = getOrCreateHint(input);
    var cityId    = input.dataset.fillCity;
    var stateId   = input.dataset.fillState;
    var lastPin   = '';

    function run() {
      var pin = input.value.replace(/\D/g, '');
      if (pin.length !== 6 || pin === lastPin) return;
      lastPin = pin;
      hint.style.color = '#aaa';
      hint.textContent = '🔍 Looking up…';

      lookup(pin, function (res) {
        if (!res) {
          hint.style.color = '#e65100';
          hint.textContent = '⚠️ PIN code not found';
          return;
        }
        hint.style.color = '#2e7d32';
        var parts = res.area !== res.district ? [res.area, res.district, res.state] : [res.district, res.state];
        hint.textContent = '📍 ' + parts.join(', ');

        if (cityId) {
          var cityEl = document.getElementById(cityId);
          if (cityEl) cityEl.value = res.area !== res.district ? res.area + ', ' + res.district : res.district;
        }
        if (stateId) {
          var stateEl = document.getElementById(stateId);
          if (stateEl) stateEl.value = res.state;
        }
      });
    }

    input.addEventListener('input', run);
    input.addEventListener('blur',  run);
    // run on load if already filled (e.g. edit forms)
    if (input.value.length === 6) run();
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[data-pinlookup]').forEach(initOne);
  });

  window.initPinLookup = initOne;
})();
