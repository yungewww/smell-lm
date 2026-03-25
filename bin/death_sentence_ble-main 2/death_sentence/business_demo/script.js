const API_BASE = window.FREQUENCY_API_BASE || 'http://localhost:8000';

/**
 * Subtle chromatic emphasis on CTA hover
 */
document.querySelector('.cta-button')?.addEventListener('mouseenter', function () {
  this.style.setProperty('--chroma', '1');
});
document.querySelector('.cta-button')?.addEventListener('mouseleave', function () {
  this.style.setProperty('--chroma', '0.9');
});

/**
 * Frequency section: record / stop button, then transcribe via OpenAI and show below circle
 */
(function () {
  var recordBtn = document.getElementById('frequencyRecordBtn');
  var transcriptionEl = document.getElementById('frequencyTranscriptionText');
  var statusEl = document.getElementById('frequencyTranscriptionStatus');
  if (!recordBtn) return;

  var micIcon = recordBtn.querySelector('.record-mic-icon');
  var stopIcon = recordBtn.querySelector('.record-stop-icon');
  var recordLabel = recordBtn.querySelector('.record-label');
  var mediaRecorder = null;
  var stream = null;
  var chunks = [];

  var progressEl = document.getElementById('frequencyProgress');
  var progressLabelEl = document.getElementById('frequencyProgressLabel');
  var progressFillEl = document.getElementById('frequencyProgressFill');

  function setRecording(recording) {
    recordBtn.classList.toggle('recording', recording);
    recordBtn.setAttribute('aria-label', recording ? 'Stop recording' : 'Record audio');
    if (recordLabel) recordLabel.textContent = recording ? 'Stop' : 'Record';
  }

  function setStatus(text, isError) {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.style.color = isError ? 'rgba(255, 120, 120, 0.9)' : 'rgba(255, 255, 255, 0.5)';
  }

  function setTranscription(text) {
    if (transcriptionEl) transcriptionEl.textContent = text || '';
  }

  function showProgress(label, percent) {
    if (!progressEl || !progressFillEl) return;
    progressEl.classList.add('frequency-progress-visible');
    if (progressLabelEl && label) progressLabelEl.textContent = label;
    progressFillEl.style.width = (percent || 0) + '%';
  }

  function updateProgress(label, percent) {
    if (!progressEl || !progressFillEl) return;
    if (progressLabelEl && label) progressLabelEl.textContent = label;
    if (typeof percent === 'number') {
      progressFillEl.style.width = percent + '%';
    }
  }

  function hideProgress() {
    if (!progressEl || !progressFillEl) return;
    progressEl.classList.remove('frequency-progress-visible');
    progressFillEl.style.width = '0%';
    if (progressLabelEl) progressLabelEl.textContent = '';
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    if (stream) {
      stream.getTracks().forEach(function (t) { t.stop(); });
      stream = null;
    }
    setRecording(false);
  }

  function sendForTranscription(blob, mimeType) {
    showProgress('Transcribing', 20);
    setStatus('');
    setTranscription('');
    var form = new FormData();
    var ext = (mimeType || '').indexOf('webm') !== -1 ? 'webm' : 'ogg';
    form.append('audio', blob, 'recording.' + ext);

    fetch(API_BASE + '/transcribe', {
      method: 'POST',
      body: form
    })
      .then(function (res) {
        if (!res.ok) return res.json().then(function (body) { throw new Error(body.detail || res.statusText); });
        return res.json();
      })
      .then(function (data) {
        var text = data.text || '';
        setTranscription(text);
        updateProgress('Fetching database', 45);

        var scentPromise;
        if (isInFeedbackMode) {
          updateProgress('Refining scent', 70);
          scentPromise = feedbackScent(text);
        } else {
          updateProgress('Composing scent', 70);
          scentPromise = composeScent(text);
        }

        return scentPromise.then(function (sequence) {
          setStatus('');
          if (sequence && sequence.length) {
            // On first compose, enter feedback mode
            if (!isInFeedbackMode) {
              sessionOriginalSentence = text;
              sessionOriginalSequence = sequence;
              isInFeedbackMode = true;
            }
            currentSequence = sequence;
            console.log("rendering scent");
            console.log(sequence);
            updateProgress('Playing on device', 95);
            renderProfile(sequence);
            playSequenceOnDevice().finally(function () {
              updateProgress('Complete', 100);
              setTimeout(hideProgress, 800);
            });
          } else {
            setStatus('No scent sequence generated.');
            updateProgress('No scent generated', 100);
            setTimeout(hideProgress, 800);
          }
        });
      })
      .catch(function (err) {
        setStatus('Transcription failed: ' + (err.message || err));
        setTranscription('');
        hideProgress();
      });
  }

  recordBtn.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (recordBtn.classList.contains('recording')) {
      stopRecording();
      return;
    }

    chunks = [];
    setRecording(true);
    // Reset UI for new run (only clear nodes on first compose, not during feedback)
    if (!isInFeedbackMode) {
      renderProfile([]);
    }
    hideProgress();
    setTranscription('');
    setStatus('');

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setRecording(false);
      if (window.alert) window.alert('Your browser does not support recording. Try Chrome or Firefox.');
      return;
    }

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(function (s) {
        stream = s;
        var options = { mimeType: 'audio/webm;codecs=opus' };
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          options = {};
        }
        mediaRecorder = new MediaRecorder(stream, options);
        mediaRecorder.ondataavailable = function (ev) {
          if (ev.data.size > 0) chunks.push(ev.data);
        };
        mediaRecorder.onstop = function () {
          if (stream) {
            stream.getTracks().forEach(function (t) { t.stop(); });
            stream = null;
          }
          if (chunks.length) {
            var blob = new Blob(chunks, { type: mediaRecorder.mimeType || 'audio/webm' });
            sendForTranscription(blob, mediaRecorder.mimeType);
          }
        };
        mediaRecorder.start();
      })
      .catch(function (err) {
        console.warn('Recording not available:', err);
        setRecording(false);
        if (window.alert) {
          window.alert('Microphone access is needed to record. Please allow the site to use your microphone and try again.');
        }
      });
  });
})();

/*
Below is the original code for scent composition from death_sentence/script.js, now modified to take in the transcription and composed a scent sequence based on the transcription. 
*/

// Base notes are loaded from scent_classification.json; file must exist
const baseNotes = [];
let scentsData = {};
let currentSequence = null; // Store the last generated sequence for playback

// Feedback loop session state
let sessionOriginalSentence = null;
let sessionOriginalSequence = null;
let sessionHistory = []; // Array of {feedback_text, changes_made, resulting_sequence}
let isInFeedbackMode = false;

// Attempt to load scent names dynamically from JSON (keys become base notes)
fetch('./scent_classification.json')
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

async function composeScent(sentence) {
  try {
    const res = await fetch(API_BASE + '/compose', {
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
    console.log('[Compose] Justification:', data.justification);
    return data.scent_sequence || null;
  } catch (err) {
    console.error(err);
    alert('Network error calling composition service. Is the backend running on :8000?');
    return null;
  }
}

async function feedbackScent(feedbackText) {
  try {
    const res = await fetch(API_BASE + '/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        original_sentence: sessionOriginalSentence,
        original_sequence: sessionOriginalSequence,
        prior_rounds: sessionHistory,
        latest_feedback: feedbackText
      })
    });
    if (!res.ok) {
      const msg = await res.text();
      alert(`Refinement failed: ${msg}`);
      return null;
    }
    const data = await res.json();
    if (data.scent_sequence) {
      sessionHistory.push({
        feedback_text: feedbackText,
        changes_made: data.changes_made || '',
        resulting_sequence: data.scent_sequence
      });
    }
    console.log('[Feedback] Justification:', data.justification);
    console.log('[Feedback] Changes made:', data.changes_made);
    return data.scent_sequence || null;
  } catch (err) {
    console.error(err);
    alert('Network error calling feedback service. Is the backend running on :8000?');
    return null;
  }
}

function resetSession() {
  sessionOriginalSentence = null;
  sessionOriginalSequence = null;
  sessionHistory = [];
  isInFeedbackMode = false;
}

function computeMortality(prompt) {
  const rng = mulberry32(hashString(prompt || 'default'));
  return Math.round(10 * (0.4 + rng() * 0.6)) / 1;
}

const NODE_ORDER = ['12', '130', '3', '430', '6', '730', '9', '1030'];

function setLoading(isLoading) {
  // No loader UI in business_demo; no-op
}

function renderProfile(sequence) {
  const nodes = NODE_ORDER.map(id => document.querySelector('.frequency-node-' + id)).filter(Boolean);
  nodes.forEach(node => {
    node.classList.remove('frequency-node-visible');
    const label = node.querySelector('.node-label');
    if (label) label.textContent = '';
  });

  sequence.slice(0, 8).forEach((item, i) => {
    const node = nodes[i];
    if (!node) return;
    const label = node.querySelector('.node-label');
    console.log(item.scent_name);
    if (label) label.textContent = item.scent_name || '';

    setTimeout(() => {
      node.classList.add('frequency-node-visible');
    }, i * 400);
  });
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

  // Convert scent names to scent_ids using the location field, skipping unknown scents
  const bleSequence = [];
  for (const item of currentSequence) {
    const meta = scentsData[item.scent_name];
    if (!meta || !meta.location) {
      console.warn(`Skipping scent with no device location: ${item.scent_name}`);
      continue;
    }
    const locId = parseInt(meta.location);
    if (locId < 1 || locId > 12) {
      console.warn(`Skipping scent outside device range (1-12): ${item.scent_name} (location=${locId})`);
      continue;
    }
    bleSequence.push({ scent_id: locId, duration: item.scent_duration });
  }

  if (bleSequence.length === 0) {
    alert('No playable scents in sequence (all scents are outside device range 1-12).');
    return;
  }

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
