// ── Data ──────────────────────────────────────────────────────────────────
const WHITE_INDUSTRIES = [
    'IT & Technology', 'Finance & Banking', 'Healthcare', 'Education',
    'Marketing & Media', 'Legal & Compliance', 'HR & Recruitment',
    'Engineering', 'Management & Admin', 'Customer Support'
];

const BLUE_INDUSTRIES = [
    'Construction', 'Manufacturing', 'Transport & Logistics',
    'Food & Hospitality', 'Retail & Commerce', 'Home Services',
    'Agriculture', 'Security Services', 'Personal Services'
];

const WHITE_ROLES = [
    'Software Developer', 'Web Designer', 'Data Analyst', 'IT Support',
    'Accountant', 'Finance Manager', 'Bank Officer', 'Auditor',
    'Doctor', 'Nurse', 'Pharmacist', 'Lab Technician',
    'Teacher', 'Lecturer', 'Tutor',
    'Marketing Executive', 'Sales Manager', 'Content Writer',
    'HR Executive', 'Recruiter', 'Admin Executive',
    'Civil Engineer', 'Mechanical Engineer', 'Electrical Engineer',
    'Customer Support Executive', 'BPO Executive',
    'Legal Advisor', 'Company Secretary'
];

const BLUE_ROLES = [
    'Plumber', 'Electrician', 'Carpenter', 'Painter', 'Mason / Mistri',
    'Driver (Car)', 'Driver (Truck)', 'Auto Driver', 'Two Wheeler Driver',
    'Delivery Boy', 'Cook / Chef', 'Hotel Helper', 'Waiter',
    'House Maid', 'Helper / Assistant', 'Cleaner / Sweeper', 'Gardener',
    'Security Guard / Watchman',
    'Mechanic (Bike)', 'Mechanic (Car)', 'AC / Fridge Repair',
    'Welder', 'Fabricator',
    'Tailor', 'Embroidery Worker',
    'Construction Labour', 'Daily Wage Worker',
    'Barber', 'Beautician',
    'Peon / Office Boy'
];

// ── State ─────────────────────────────────────────────────────────────────
let selectedCollar = '';
let jobMap = null;
let jobMarker = null;

// ── Step 1: Choose Collar ─────────────────────────────────────────────────
function chooseCollar(type) {
    selectedCollar = type;
    document.getElementById('collarTypeInput').value = type;

    // Set badge
    const badge = document.getElementById('collarBadge');
    if (type === 'white') {
        badge.className = 'pj-collar-badge badge-white';
        badge.innerHTML = '<i class="fas fa-user-tie"></i> White Collar Job';
    } else {
        badge.className = 'pj-collar-badge badge-blue';
        badge.innerHTML = '<i class="fas fa-wrench"></i> Blue Collar Job';
    }

    // Populate dropdowns
    populateSelect('industrySelect', type === 'white' ? WHITE_INDUSTRIES : BLUE_INDUSTRIES);
    populateSelect('categorySelect', type === 'white' ? WHITE_ROLES : BLUE_ROLES);

    // Switch steps
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.remove('hidden');

    // Init map after step is visible
    setTimeout(initMap, 100);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function populateSelect(id, items) {
    const sel = document.getElementById(id);
    sel.innerHTML = '<option value="">Select...</option>';
    items.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item;
        opt.textContent = item;
        sel.appendChild(opt);
    });
}

// ── Back ──────────────────────────────────────────────────────────────────
function goBack() {
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step1').classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Map (Leaflet + OpenStreetMap) ─────────────────────────────────────────
function initMap() {
    if (jobMap) return; // already initialised

    jobMap = L.map('jobMap').setView([11.0168, 76.9558], 11); // default: Coimbatore

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(jobMap);

    jobMap.on('click', function (e) {
        setMarker(e.latlng.lat, e.latlng.lng);
        document.getElementById('mapHint').style.display = 'none';
    });
}

function setMarker(lat, lng) {
    if (jobMarker) jobMap.removeLayer(jobMarker);
    jobMarker = L.marker([lat, lng]).addTo(jobMap);
    document.getElementById('latInput').value = lat.toFixed(6);
    document.getElementById('lngInput').value = lng.toFixed(6);
}

function locateByPin() {
    const pin = document.getElementById('pincodeInput').value.trim();
    if (pin.length !== 6) { alert('Enter a valid 6-digit PIN code'); return; }

    const btn = document.querySelector('.locate-btn');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';
    btn.disabled = true;

    fetch(`https://nominatim.openstreetmap.org/search?postalcode=${pin}&country=India&format=json`)
        .then(r => r.json())
        .then(data => {
            if (data && data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lng = parseFloat(data[0].lon);
                jobMap.setView([lat, lng], 14);
                setMarker(lat, lng);
                document.getElementById('mapHint').style.display = 'none';
            } else {
                alert('Could not locate PIN code. Please click on the map to set location.');
            }
        })
        .catch(() => alert('Location fetch failed. Click on map to set location.'))
        .finally(() => {
            btn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Locate';
            btn.disabled = false;
        });
}

// ── Working Days ──────────────────────────────────────────────────────────
function getWorkingDays() {
    const days = [];
    ['mon','tue','wed','thu','fri','sat','sun'].forEach(d => {
        const el = document.querySelector(`input[name="day_${d}"]`);
        if (el && el.checked) days.push(el.value);
    });
    return days.join(', ');
}

// ── Languages ─────────────────────────────────────────────────────────────
function getLanguages() {
    const langs = [];
    ['any','tamil','english','hindi','telugu','malayalam'].forEach(l => {
        const el = document.querySelector(`input[name="lang_${l}"]`);
        if (el && el.checked) langs.push(el.value);
    });
    return langs.join(', ') || 'Any';
}

// ── Form submit: inject computed fields before POST ───────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('jobForm');
    if (!form) return;

    form.addEventListener('submit', function () {
        // Inject working days
        let wdInput = form.querySelector('input[name="working_days"]');
        if (!wdInput) {
            wdInput = document.createElement('input');
            wdInput.type = 'hidden';
            wdInput.name = 'working_days';
            form.appendChild(wdInput);
        }
        wdInput.value = getWorkingDays();

        // Inject languages
        let langInput = form.querySelector('input[name="language"]');
        if (!langInput) {
            langInput = document.createElement('input');
            langInput.type = 'hidden';
            langInput.name = 'language';
            form.appendChild(langInput);
        }
        langInput.value = getLanguages();
    });
});
