const promptInput = document.getElementById('prompt');
const synthBtn = document.getElementById('synthesize');
const leafBtn = document.getElementById('leaf');
const results = document.getElementById('results');
const notesEl = document.getElementById('notes');
const needle = document.getElementById('needle');
const scoreEl = document.getElementById('score');
const loaderEl = document.getElementById('loader');
const dynamicPrefixEl = document.getElementById('dynamicPrefix');

// Death-themed prefix words and their associated prompts
// Each word naturally pairs with "SENTENCE" to create death-related phrases
const themes = [
  {
    prefix: 'FINAL',
    color: '#ff0000',
    prompts: [
      'I want to rest in the forest alone..',
      'Lay me by the ocean during a storm..',
      'Disappear into neon rain in a cyberpunk alley..',
      'Freeze into a glacier under auroras..',
    ]
  },
  {
    prefix: 'LAST',
    color: '#ffb700',
    prompts: [
      'Take me to the mountains one final time..',
      'Let me see the northern lights before I go..',
      'I want to taste the sea air and feel the wind..',
      'Bring me flowers from the wildflower field..',
    ]
  },
  {
    prefix: 'DARK',
    color: '#8b0000',
    prompts: [
      'Bury me in the shadows of ancient trees..',
      'Let me dissolve into the midnight fog..',
      'I want to become one with the eternal night..',
      'Scatter my ashes in the deepest cave..',
    ]
  },
  {
    prefix: 'SILENT',
    color: '#696969',
    prompts: [
      'I want to fade away without a sound..',
      'Let me disappear into the quiet mist..',
      'I wish to become the silence between heartbeats..',
      'Take me where the world stops speaking..',
    ]
  },
  {
    prefix: 'COLD',
    color: '#00bfff',
    prompts: [
      'I want to freeze into a crystal of ice..',
      'Let me become the snow that never melts..',
      'I wish to rest in the eternal winter..',
      'Bury me in the heart of a glacier..',
    ]
  },
  {
    prefix: 'DEEP',
    color: '#191970',
    prompts: [
      'I want to sink into the ocean\'s abyss..',
      'Let me become one with the deep sea..',
      'I wish to rest in the darkest trench..',
      'Take me to the bottom of the world..',
    ]
  },
  {
    prefix: 'FOREVER',
    color: '#800080',
    prompts: [
      'I want to become eternal stardust..',
      'Let me transform into cosmic energy..',
      'I wish to merge with the infinite void..',
      'Take me beyond the edge of existence..',
    ]
  }
];

let currentThemeIndex = 0;
let allPrompts = [];

// Initialize with all prompts
themes.forEach(theme => {
  allPrompts = allPrompts.concat(theme.prompts);
});

// Cycle through themes
function cycleTheme() {
  currentThemeIndex = (currentThemeIndex + 1) % themes.length;
  const theme = themes[currentThemeIndex];
  
  if (dynamicPrefixEl) {
    // Add transitioning class for quick fade out
    dynamicPrefixEl.classList.add('transitioning');
    
    setTimeout(() => {
      // Change text while invisible
      dynamicPrefixEl.textContent = theme.prefix;
      // Remove transitioning class to fade back in
      dynamicPrefixEl.classList.remove('transitioning');
    }, 150);
  }
}

// Start theme cycling - faster for sense of potential
setInterval(cycleTheme, 2000); // Change every 2 seconds

// Base notes are loaded from scent_classification.json; file must exist
const baseNotes = [];
let scentsData = {};
let currentSequence = null; // Store the last generated sequence for playback

// Attempt to load scent names dynamically from JSON (keys become base notes)
fetch('scent_classification.json')
  .then(r => { if (!r.ok) throw new Error('Missing scent_classification.json'); return r.json(); })
  .then(data => {
    scentsData = data || {};
    const names = Object.keys(scentsData);
    if (names.length === 0) throw new Error('scent_classification.json has no entries');
    baseNotes.splice(0, baseNotes.length, ...names);
  })
  .catch(err => {
    console.error(err);
  });

leafBtn.addEventListener('click', () => {
  const v = allPrompts[Math.floor(Math.random() * allPrompts.length)];
  promptInput.value = v;
});

synthBtn.addEventListener('click', async () => {
  const prompt = (promptInput.value || '').trim();
  if (!prompt) {
    alert('Please enter your death sentence.');
    return;
  }
  // Optionally ensure local data is present; backend also validates
  if (baseNotes.length === 0) {
    console.warn('Local scent data not yet loaded; proceeding with backend composition.');
  }
  setLoading(true);
  const sequence = await composeScent(prompt);
  setLoading(false);
  if (!sequence) { return; }
  
  // Store the sequence for playback
  currentSequence = sequence;
  
  const notes = sequence.map(item => {
    const meta = scentsData && scentsData[item.scent_name];
    const loc = meta && meta.location ? ` [${meta.location}]` : '';
    return `${item.scent_name} (${item.scent_duration}s)${loc}`;
  });
  const strengths = sequence.map(item => Math.round((item.scent_duration / 30) * 100));
  const mortality = computeMortality(prompt);
  renderProfile({ notes, strengths, mortality });
});

async function composeScent(sentence) {
  try {
    const res = await fetch('http://localhost:8000/compose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sentence })
    });
    if (!res.ok) {
      const msg = await res.text();
      alert(`Composition failed: ${msg}`);
      return null;
    }
    const data = await res.json();
    return data.scent_sequence || null;
  } catch (err) {
    console.error(err);
    alert('Network error calling composition service. Is the backend running on :8000?');
    return null;
  }
}

function computeMortality(prompt) {
  const rng = mulberry32(hashString(prompt || 'default'));
  return Math.round(10 * (0.4 + rng() * 0.6)) / 1;
}

function setLoading(isLoading) {
  if (!loaderEl) return;
  if (isLoading) {
    loaderEl.classList.remove('hidden');
    synthBtn.disabled = true;
  } else {
    loaderEl.classList.add('hidden');
    synthBtn.disabled = false;
  }
}

function renderProfile(profile) {
  notesEl.innerHTML = '';
  profile.notes.forEach((name, i) => {
    const li = document.createElement('li');
    li.className = 'note';
    li.innerHTML = `
      <div class="note-name">${i + 1}. ${name}</div>
      <div class="bars">
        <div class="bar"><span style="width:${profile.strengths[i]}%"></span></div>
      </div>
    `;
    notesEl.appendChild(li);
  });

  results.classList.remove('hidden');
  scoreEl.textContent = `${profile.mortality.toFixed(1)}/10`;

  const angle = -70 + (profile.mortality / 10) * 140; // -70deg to +70deg
  needle.style.transform = `rotate(${angle}deg)`;
}

// Utils
function pickUnique(arr, count, rng) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1));[a[i], a[j]] = [a[j], a[i]]; }
  return a.slice(0, count);
}

function hashString(str) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function mulberry32(a) {
  return function () {
    let t = a += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// BLE Integration Functions
async function playSequenceOnDevice() {
  if (!currentSequence || currentSequence.length === 0) {
    alert('No sequence to play. Generate a scent sequence first!');
    return;
  }

  // Convert scent names to scent_ids using the location field
  const bleSequence = currentSequence.map(item => {
    const meta = scentsData[item.scent_name];
    if (!meta || !meta.location) {
      throw new Error(`Location not found for scent: ${item.scent_name}`);
    }
    return {
      scent_id: parseInt(meta.location),
      duration: item.scent_duration
    };
  });

  try {
    setLoading(true);
    const playBtn = document.getElementById('playSequenceBtn');
    if (playBtn) playBtn.disabled = true;

    const response = await fetch('http://localhost:5001/play_sequence', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sequence: bleSequence })
    });

    const result = await response.json();

    if (result.status === 'success') {
      alert('✅ Sequence is playing on your device!');
    } else {
      alert(`❌ Error: ${result.message}`);
    }
  } catch (err) {
    console.error('BLE Error:', err);
    alert('❌ Could not connect to BLE device. Make sure:\n1. The Flask backend is running on :5001\n2. Your BLE device is powered on\n3. Device is in range');
  } finally {
    setLoading(false);
    const playBtn = document.getElementById('playSequenceBtn');
    if (playBtn) playBtn.disabled = false;
  }
}

async function testBLEConnection() {
  try {
    setLoading(true);
    const response = await fetch('http://localhost:5001/test_connection', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    const result = await response.json();

    if (result.status === 'success') {
      alert(`✅ ${result.message}`);
    } else {
      alert(`❌ ${result.message}`);
    }
  } catch (err) {
    console.error('Connection test error:', err);
    alert('❌ Could not connect to BLE backend. Make sure the Flask server is running on :5001');
  } finally {
    setLoading(false);
  }
}

