// ── Employer type metadata ───────────────────────────────────────────────────
const EMPLOYER_TYPES = [
    'company', 'shop', 'recruiter', 'factory', 'startup',
    'institution', 'ngo', 'hospital', 'hotel',
    'farm', 'individual_employer'
];

const TYPE_META = {
    company:             { label: 'Company',             icon: 'fa-building',      badge: 'blue',   org: 'Company Name',       desc: 'Register your company and start hiring talent' },
    shop:                { label: 'Shop',                 icon: 'fa-store',         badge: 'purple', org: 'Shop Name',          desc: 'Hire the right staff for your shop' },
    recruiter:           { label: 'Recruiter',            icon: 'fa-user-tie',      badge: 'teal',   org: 'Agency Name',        desc: 'Post jobs on behalf of your client companies' },
    factory:             { label: 'Factory',              icon: 'fa-industry',      badge: 'orange', org: 'Factory Name',       desc: 'Hire skilled workers for your factory' },
    startup:             { label: 'Startup',              icon: 'fa-rocket',        badge: 'red',    org: 'Startup Name',       desc: 'Build your startup team from scratch' },
    institution:         { label: 'Institution',          icon: 'fa-university',    badge: 'blue',   org: 'Institution Name',   desc: 'Hire staff for your school, college or institute' },
    ngo:                 { label: 'NGO',                  icon: 'fa-hands-helping', badge: 'green',  org: 'NGO / Trust Name',   desc: 'Hire workers for your social organization' },
    hospital:            { label: 'Hospital',             icon: 'fa-hospital',      badge: 'teal',   org: 'Hospital Name',      desc: 'Hire doctors, nurses & support staff' },
    hotel:               { label: 'Hotel / Restaurant',   icon: 'fa-hotel',         badge: 'gold',   org: 'Hotel / Rest. Name', desc: 'Hire hospitality and kitchen staff' },
    farm:                { label: 'Farm',                  icon: 'fa-leaf',          badge: 'green',  org: 'Farm Name',          desc: 'Hire agricultural and farm workers' },
    individual_employer: { label: 'Individual Employer',  icon: 'fa-user-plus',     badge: 'orange', org: 'Your Full Name',     desc: 'Hire personal, domestic or household staff' },
};

let currentType = '';

// ── Auto-select type from URL ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const type = new URLSearchParams(window.location.search).get('type');
    if (type) selectType(type);
});

// ── Type selection ─────────────────────────────────────────────────────────────
function selectType(type) {
    currentType = type;
    document.querySelectorAll('.reg-step').forEach(s => s.classList.add('hidden'));

    if (type === 'individual_employer') {
        // Individual employer has its own lightweight OTP-based form
        document.getElementById('step-individual_employer').classList.remove('hidden');
    } else if (EMPLOYER_TYPES.includes(type)) {
        loadEmployerForm(type);
        document.getElementById('step-employer').classList.remove('hidden');
    } else {
        const step = document.getElementById('step-' + type);
        if (step) step.classList.remove('hidden');
    }
}

// Badge colour → banner background mapping
const BADGE_COLORS = {
    blue:   {bg:'linear-gradient(135deg,#e8f0fe,#dbeafe)', border:'#c5d9f5', icon:'#0a66c2', text:'#0a47a1'},
    purple: {bg:'linear-gradient(135deg,#f3e5f5,#e8d5f5)', border:'#d4b8e8', icon:'#6a1b9a', text:'#4a0e6e'},
    orange: {bg:'linear-gradient(135deg,#fff3e0,#ffe5b4)', border:'#ffcc80', icon:'#e65100', text:'#bf360c'},
    red:    {bg:'linear-gradient(135deg,#fce4ec,#f8c1ce)', border:'#f48fb1', icon:'#c62828', text:'#b71c1c'},
    green:  {bg:'linear-gradient(135deg,#e8f5e9,#c8e6c9)', border:'#a5d6a7', icon:'#2e7d32', text:'#1b5e20'},
    teal:   {bg:'linear-gradient(135deg,#e0f7fa,#b2ebf2)', border:'#80deea', icon:'#00838f', text:'#006064'},
    gold:   {bg:'linear-gradient(135deg,#fff8e1,#ffecb3)', border:'#ffe082', icon:'#f9a825', text:'#e65100'},
};

function loadEmployerForm(type) {
    const m = TYPE_META[type];
    if (!m) return;
    const c = BADGE_COLORS[m.badge] || BADGE_COLORS.blue;

    document.getElementById('emp-user-type-input').value = type;
    document.getElementById('emp-type-label').textContent = m.label;
    document.getElementById('emp-type-icon').className    = 'fas ' + m.icon;
    document.getElementById('emp-type-desc').textContent  = m.desc;
    document.getElementById('emp-org-label').innerHTML    =
        '<i class="fas ' + m.icon + '"></i> ' + m.org + ' *';
    document.getElementById('emp-org-input').placeholder  = 'Enter ' + m.org.toLowerCase();
    document.getElementById('emp-submit-label').textContent =
        'Create ' + m.label + ' Account';

    // Sync dropdown selection
    var sel = document.getElementById('empTypeSwitcher');
    if (sel) sel.value = type;

    // Update banner colours
    var banner = document.getElementById('empTypeBanner');
    var icon   = document.getElementById('etbIcon');
    var label  = document.getElementById('emp-type-badge');
    if (banner) { banner.style.background = c.bg; banner.style.borderColor = c.border; }
    if (icon)   { icon.style.background   = c.icon; }
    if (label)  { label.style.color       = c.text; }
}

function switchEmployerType(type) {
    currentType = type;
    loadEmployerForm(type);
    var sel = document.getElementById('empTypeSwitcher');
    if (sel && sel.value !== type) sel.value = type;
}

function goBack() {
    document.querySelectorAll('.reg-step').forEach(s => s.classList.add('hidden'));
    document.getElementById('step1').classList.remove('hidden');
}

// ── Inject hidden field helper (used by OTP-based seeker forms) ───────────────
function injectField(form, name, value) {
    let el = form.querySelector('[name="' + name + '"]');
    if (!el) {
        el = document.createElement('input');
        el.type = 'hidden';
        el.name = name;
        form.appendChild(el);
    }
    el.value = value;
}

// ── OTP flow ──────────────────────────────────────────────────────────────────
function showDemoOtpPopup() {
    var existing = document.getElementById('demoOtpPopup');
    if (existing) existing.remove();

    var popup = document.createElement('div');
    popup.id = 'demoOtpPopup';
    popup.innerHTML = `
        <div style="
            position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
            background:#fff;border-radius:20px;padding:32px 36px;
            box-shadow:0 20px 60px rgba(0,0,0,.25);z-index:99999;
            text-align:center;min-width:280px;animation:otpPopIn .3s cubic-bezier(.22,.68,0,1.4)
        ">
            <div style="font-size:48px;margin-bottom:10px">📱</div>
            <div style="font-size:13px;font-weight:700;color:#888;letter-spacing:.5px;margin-bottom:6px">DEMO OTP</div>
            <div style="font-size:42px;font-weight:900;color:#0a66c2;letter-spacing:12px;margin-bottom:14px">123456</div>
            <div style="font-size:13px;color:#aaa">Use this code to verify</div>
            <button onclick="document.getElementById('demoOtpPopup').remove()" style="
                margin-top:20px;background:#0a66c2;color:#fff;border:none;
                padding:10px 32px;border-radius:24px;font-size:14px;font-weight:700;cursor:pointer
            ">Got it!</button>
        </div>
        <div onclick="document.getElementById('demoOtpPopup').remove()" style="
            position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:99998
        "></div>
        <style>
        @keyframes otpPopIn{
            0%{transform:translate(-50%,-50%) scale(.7);opacity:0}
            100%{transform:translate(-50%,-50%) scale(1);opacity:1}
        }
        </style>
    `;
    document.body.appendChild(popup);
    setTimeout(function(){ if(document.getElementById('demoOtpPopup')) document.getElementById('demoOtpPopup').remove(); }, 8000);
}

function sendOTP(prefix) {
    const phoneInput = document.getElementById(prefix + 'Phone');
    if (!phoneInput) return;
    const phone = phoneInput.value.trim();

    if (phone.length !== 10 || isNaN(phone)) {
        alert('Please enter a valid 10-digit mobile number.');
        return;
    }

    const btn = phoneInput.closest('.otp-input-row').querySelector('.otp-btn');
    btn.textContent = 'Sent!';
    btn.classList.add('sent');
    btn.disabled = true;

    document.getElementById(prefix + 'OtpBox').classList.remove('hidden');
    setTimeout(() => {
        const first = document.getElementById(prefix + 'OtpBox').querySelector('.otp-digit');
        if (first) first.focus();
    }, 100);

    showDemoOtpPopup();

    setTimeout(() => {
        btn.textContent = 'Resend';
        btn.classList.remove('sent');
        btn.disabled = false;
    }, 30000);
}

function otpNext(input) {
    input.value = input.value.replace(/[^0-9]/g, '');
    if (input.value.length === 1) {
        const next = input.nextElementSibling;
        if (next && next.classList.contains('otp-digit')) next.focus();
    }
}

function verifyOTP(prefix) {
    const box    = document.getElementById(prefix + 'OtpBox');
    const digits = box.querySelectorAll('.otp-digit');
    let otp = '';
    digits.forEach(d => otp += d.value);

    if (otp.length !== 6) {
        alert('Please enter the 6-digit OTP.');
        return;
    }

    document.getElementById(prefix + '-substep1').classList.add('hidden');
    document.getElementById(prefix + '-substep2').classList.remove('hidden');
}

// ── Password match check ──────────────────────────────────────────────────────
function checkPasswords(form) {
    const pwd  = form.querySelector('[name="password"]');
    const pwd2 = form.querySelector('[name="password2"]');
    const err  = form.querySelector('.pwd-error, #emp-pwd-error');
    if (!pwd || !pwd2) return true;
    if (pwd.value !== pwd2.value) {
        if (err) err.style.display = 'block';
        pwd2.focus();
        return false;
    }
    if (err) err.style.display = 'none';
    return true;
}

// ── AJAX submit for all register forms ───────────────────────────────────────
function regAjaxSubmit(form) {
    if (!checkPasswords(form)) return;

    const btn = form.querySelector('button[type="submit"]');
    let errEl = form.querySelector('.reg-ajax-err');
    if (!errEl) {
        errEl = document.createElement('p');
        errEl.className = 'reg-ajax-err';
        errEl.style.cssText = 'color:#dc2626;background:#fef2f2;border:1px solid #fca5a5;' +
            'border-radius:8px;padding:.6rem .9rem;font-size:.85rem;margin:.75rem 0 0;display:none';
        form.prepend(errEl);
    }
    errEl.style.display = 'none';

    if (btn) {
        btn.disabled    = true;
        btn.dataset.orig = btn.innerHTML;
        btn.innerHTML   = '<i class="fas fa-circle-notch fa-spin"></i> Creating account…';
    }

    var csrfInput   = form.querySelector('[name=csrfmiddlewaretoken]');
    var csrfCookie  = document.cookie.split('; ').filter(function(c){ return c.indexOf('csrftoken=') === 0; })[0];
    var csrf        = (csrfInput ? csrfInput.value : '') || (csrfCookie ? csrfCookie.split('=')[1] : '');

    fetch('/register/process/', {
        method:  'POST',
        headers: { 'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest' },
        body:    new FormData(form),
    })
        .then(function (r) { return r.json(); })
        .then(function (res) {
            if (res.success) {
                window.location.href = res.redirect;
            } else {
                errEl.textContent = res.error || 'Registration failed. Please try again.';
                errEl.style.display = 'block';
                if (btn) { btn.disabled = false; btn.innerHTML = btn.dataset.orig; }
            }
        })
        .catch(function () {
            errEl.textContent = 'Network error. Please check your connection and try again.';
            errEl.style.display = 'block';
            if (btn) { btn.disabled = false; btn.innerHTML = btn.dataset.orig || 'Submit'; }
        });
}

// ── Password live-check (employer form) ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    var p1 = document.getElementById('emp-pwd');
    var p2 = document.getElementById('emp-pwd2');
    var er = document.getElementById('emp-pwd-error');
    if (p1 && p2 && er) {
        p2.addEventListener('input', function () {
            er.style.display = (p1.value && p2.value && p1.value !== p2.value) ? 'block' : 'none';
        });
    }
});

// ── Intercept ALL register forms — document-level delegation ──────────────────
// Fires after onsubmit attribute (field injection), so FormData picks up injected fields.
document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.action || form.action.indexOf('/register/process/') === -1) return;
    e.preventDefault();
    regAjaxSubmit(form);
});
