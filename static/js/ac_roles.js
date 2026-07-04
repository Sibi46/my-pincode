/* Shared job-role autocomplete — include on any page with job/skill inputs */
window.AC_ROLES = [
  // White collar
  "Software Developer","Web Designer","Data Analyst","Network Engineer","IT Support","Cybersecurity",
  "Doctor","Nurse","Pharmacist","Lab Technician","Physiotherapist","Medical Officer",
  "Teacher","Lecturer","Tutor","Principal","Librarian","Counsellor",
  "Accountant","Auditor","Bank Officer","Financial Analyst","Insurance Agent","Tax Consultant",
  "Sales Executive","Marketing Manager","Brand Manager","Digital Marketer","Customer Support",
  "Office Manager","HR Executive","Data Entry Operator","Receptionist","Secretary","BPO Agent",
  "Civil Engineer","Mechanical Engineer","Electrical Engineer","Project Manager","Site Engineer",
  "Lawyer","Legal Advisor","Compliance Officer","Court Clerk",
  "Graphic Designer","Video Editor","Content Writer","Journalist","Photographer",
  "Store Manager","Purchase Manager","Supply Chain","Inventory Manager","E-commerce Executive",
  // Blue collar
  "Mason","Carpenter","Painter","Welder","Plumber","Civil Labourer","Tile Fitter",
  "Electrician","Wireman","Electronics Technician","AC Technician","Solar Installer",
  "Pipe Fitter","Drainage Technician","Sanitation Worker",
  "Car Driver","Truck Driver","Auto Driver","Delivery Boy","Cab Driver","Heavy Vehicle Driver",
  "Cook","Helper","Waiter","Hotel Housekeeping","Dishwasher","Catering Staff","Baker",
  "Machine Operator","Packing Worker","Assembly Line Worker","Quality Checker","Supervisor","Forklift Operator",
  "Farm Worker","Tractor Operator","Irrigation Worker","Horticulture","Dairy Worker",
  "Security Guard","Watchman","Safety Officer","Bouncer","CCTV Operator",
  "Housemaid","Cook at Home","Babysitter","Elder Care","Gardener","Sweeper",
  "Mobile Repair","TV Technician","AC Service","Washing Machine Repair","Auto Mechanic",
  "Tailor","Barber","Beautician","Laundry Worker","Cobbler","Weaving Worker",
  "Delivery Driver","Two Wheeler Rider","Loader","Unloader","Warehouse Worker"
];

window.initJobAC = function(input) {
  if (!input || input._acInit) return;
  input._acInit = true;

  var drop = document.createElement('div');
  drop.style.cssText = [
    'position:absolute','z-index:9999','display:none',
    'background:#fff','border:1.5px solid #c5d9f5','border-radius:12px',
    'box-shadow:0 8px 28px rgba(0,0,0,.12)','max-height:220px',
    'overflow-y:auto','min-width:200px','width:100%'
  ].join(';');
  document.body.appendChild(drop);

  var acIdx = -1;

  function pos() {
    var r = input.getBoundingClientRect();
    drop.style.top  = (r.bottom + window.scrollY + 2) + 'px';
    drop.style.left = (r.left   + window.scrollX)     + 'px';
    drop.style.width = r.width + 'px';
  }

  function hl(text, q) {
    var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    return text.replace(re, '<mark style="background:none;color:#0a66c2;font-weight:800">$1</mark>');
  }

  function show() {
    var q = input.value.trim();
    drop.innerHTML = '';
    acIdx = -1;
    if (q.length < 1) { drop.style.display = 'none'; return; }
    var matches = AC_ROLES.filter(function(r) {
      return r.toLowerCase().indexOf(q.toLowerCase()) !== -1;
    });
    if (!matches.length) { drop.style.display = 'none'; return; }
    matches.slice(0, 8).forEach(function(r) {
      var item = document.createElement('div');
      item.style.cssText = 'padding:10px 14px;font-size:14px;color:#222;cursor:pointer;display:flex;align-items:center;gap:8px;border-bottom:1px solid #f3f4f6';
      item.innerHTML = '<i class="fas fa-briefcase" style="color:#0a66c2;font-size:12px;flex-shrink:0"></i>' + hl(r, q);
      item.addEventListener('mousedown', function(e) {
        e.preventDefault();
        input.value = r;
        drop.style.display = 'none';
        input.dispatchEvent(new Event('input'));
      });
      drop.appendChild(item);
    });
    pos();
    drop.style.display = 'block';
  }

  input.addEventListener('input',  show);
  input.addEventListener('focus',  show);
  input.addEventListener('blur',   function() { setTimeout(function() { drop.style.display = 'none'; }, 160); });
  window.addEventListener('scroll', function() { if (drop.style.display !== 'none') pos(); }, true);
  window.addEventListener('resize', function() { if (drop.style.display !== 'none') pos(); });

  input.addEventListener('keydown', function(e) {
    var items = drop.querySelectorAll('div');
    if (!items.length || drop.style.display === 'none') return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      acIdx = Math.min(acIdx + 1, items.length - 1);
      items.forEach(function(it, j) { it.style.background = j === acIdx ? '#e8f0fe' : ''; });
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      acIdx = Math.max(acIdx - 1, 0);
      items.forEach(function(it, j) { it.style.background = j === acIdx ? '#e8f0fe' : ''; });
    } else if (e.key === 'Enter' && acIdx >= 0) {
      e.preventDefault();
      input.value = items[acIdx].textContent.trim();
      drop.style.display = 'none';
      input.dispatchEvent(new Event('input'));
    } else if (e.key === 'Escape') {
      drop.style.display = 'none';
    }
  });
};

/* Auto-init any input with data-ac="job" attribute */
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('input[data-ac="job"]').forEach(function(inp) {
    window.initJobAC(inp);
  });
});
