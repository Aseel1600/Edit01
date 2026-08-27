# 🎬 Wild Mechanics — Master Production Pipeline Specification

**Official Channel Production Standard**  
*Validated & Battle-Tested on Scarface Jaguar (2k+ views), Great Grey Owl, and Grizzly Bear.*

---

## 🎙️ 1. Original Audio & Visual Transformation Mandate

* **Original Voice & Sound Rule:** The narration voiceover and background sound **MUST be the authentic original documentary audio** (original narrator + natural synchronized wildlife ambience). Do **NOT** replace the main story with synthetic robotic AI TTS.
* **Audio Pitch & Frequency Modulation (Anti-Fingerprint):** Apply subtle pitch shifting ($\sim \pm 0.5$ to $1.0$ semitones) and acoustic filtering (`asetrate`, `atempo`, or EQ) to alter the audio fingerprint so it sounds distinct from the raw TV broadcast master while preserving the narrator's natural vocal depth and crisp sound effects.
* **Visual Transformation:** The video must look visually distinct from real TV broadcast footage through:
  1. **4:5 Ghost Blur framing** (`1080x1350` floating over `1080x1920` ambient blur).
  2. **Color & contrast punch** (`saturation=1.12`, `contrast=1.04`).
  3. **On-screen comic action badges** (`👀 THE AMBUSH 👀`, `🎯 THE HIGH GROUND 🎯`, `💥 AIRBORNE STRIKE 💥`).
  4. **Top header branding** with curiosity-led titles.
  5. **Word-level kinetic yellow karaoke subtitles**.

---

## ⚠️ STRICT MINIMUM DURATION MANDATE
> **NO video produced for Wild Mechanics must EVER be less than 60.0 seconds total.**  
> Videos under 60.0s harm algorithmic push, watch-time monetization eligibility, and audience retention.

---

## 📌 2. Duration Policy & Minimum Thresholds

### 1. Source Footage Ingestion & BBC Naming Standard

> [!IMPORTANT]
> **Strict Duration & Source Tagging Mandate:**
> To prevent automated YouTube Content-ID claims/blocks, all downloaded footage MUST explicitly declare its provider via filename prefix:
> 
> * **BBC Footage (`bbc_*.mp4`):**
>   * **Naming Pattern:** `assets/documentaries/<animal>/bbc_<title>_source_01.mp4`
>   * **Story Duration:** Strictly **$57.0\text{s} - 58.0\text{s}$** ($< 60\text{s}$ continuous footage threshold).
>   * **Outro CTA:** **$2.5\text{s} - 3.0\text{s}$** (ElevenLabs voiceover + boosted BGM).
>   * **Total Master Short:** Exactly **$60.0\text{s} - 61.0\text{s}$**.
>
> * **Non-BBC Footage (`nonbbc_*.mp4` / Love Nature / NatGeo / Smithsonian):**
>   * **Naming Pattern:** `assets/documentaries/<animal>/nonbbc_<title>_source_01.mp4`
>   * **Story Duration:** **$87.0\text{s} - 95.0\text{s}$** (unhurried narrative arc).
>   * **Outro CTA:** **$2.5\text{s} - 3.0\text{s}$**.
>   * **Total Master Short:** **$90.0\text{s} - 98.0\text{s}$**.
>
> **The pipeline automatically inspects the filename and applies the exact duration threshold without manual intervention.**

### ✂️ C. Smart Trimming (AI Sentence Boundaries & Duration Snapping):
* **Sentence Boundary Detection:** Uses Whisper word-level timestamps to detect natural punctuation periods (`.`, `!`, `?`) and speech pauses ($>350\text{ms}$).
* **Duration Target Snapping:** Smart Trimmer must snap to the nearest completed sentence boundary right at the target ceiling ($58.0\text{s} – 60.0\text{s}$ for BBC / $70.0\text{s} – 85.0\text{s}$ for Non-BBC). It must **NEVER truncate prematurely into a 40s or 50s clip**.
* **Zero Mid-Sentence Cuts:** Guarantees narrator voice never gets sliced off mid-word or mid-thought.

---

## 🏷️ 3. On-Screen Branding & Curiosity-Driven Titles

* **Header Positioning (Breathing Room):**
  * The top branding header must sit comfortably in the upper blur zone above the 4:5 video boundary ($Y=285$).
  * **Brand Anchor:** `WILD MECHANICS` placed at **$Y=105$** (`MarginV=105`).
  * **Title Anchor:** Episode Title placed at **$Y=165$** (`MarginV=165`).
  * **Safe Buffer:** Leaves an **$80\text{px}$ clean buffer** above the 4:5 video box so it never touches or overlaps the active video boundary.
* **Distinct Header Font Colors:**
  * `WILD MECHANICS`: **Diamond White (`#FFFFFF` / `&H00FFFFFF&`)**, Arial Bold, FontSize=38, black stroke.
  * Episode Title: **Electric Yellow (`#FFFF00` / `&H0000FFFF&`)**, Impact Bold, FontSize=52, black stroke.
* **Curiosity-Driven Title Strategy:**
  * Titles must **NEVER be dry educational facts** (e.g. ❌ `"THE SALMON RUN | GRIZZLY BEAR"`).
  * Titles must create **intense curiosity, intrigue, or emotional stakes**:
    * ✅ `"WHY SALMON JUMP INTO A BEAR'S MOUTH 😱"`
    * ✅ `"THEY WAITED 10 MONTHS FOR THIS 1-SECOND STRIKE 💥"`
    * ✅ `"THE DEADLIEST 3 FEET IN THE RIVER 🐻"`

---

## 📐 4. Canvas & Framing (4:5 Ghost Blur)

* **Foreground Viewbox:** **4:5 Aspect Ratio (`1080x1350`)** keeping the animal protagonist centered in the primary viewport ($Y=285$ to $Y=1635$).
* **Background:** Ambient **`1080x1920` blurred background (`boxblur=30:5`, `brightness=-0.08`, `saturation=1.15`)** rendered from the active frame.
* **Color & Contrast Punch:** Subtle saturation boost (`1.12x`) and contrast punch (`1.04x`) to make wildlife visuals vibrant and immersive on mobile screens.
* **Zero Letterbox:** No plain black letterbox bars allowed anywhere.
* **100% Watermark Elimination:** The 4:5 center zoom/crop `(iw-1080)/2:(ih-1350)/2` automatically crops out all corner broadcaster watermarks (`PBS`, `BBC`, `Smithsonian`, `NatGeo`).

---

## 📝 5. Subtitle Styling & YouTube Shorts Safe Zones

* **Vertical Safe Zone (`MarginV=460`):** Subtitles must be anchored at **$Y \approx 1460$** (`MarginV=460` from bottom). This places them in the lower third of the 4:5 video box while staying **safely ABOVE all YouTube Shorts bottom overlay buttons** (channel handle, subscribe, audio title at $Y > 1550$).
* **Format:** Advanced ASS Subtitles with millisecond **`\k` karaoke timing tags**.
* **Typography:** Heavy Condensed Bold (`Impact` / `Montserrat ExtraBold`, `FontSize=58`).
* **Active Word Highlight:** **Electric Yellow (`#FFFF00` / `&H0000FFFF&`)** on the currently spoken word, transitioning back to clean white.
* **Outline & Legibility:** Solid 4–5px black outline (`OutlineColour=&H00000000`) for maximum legibility over dynamic animal motion.
* **100% Time-Sync:** Directly extracted from Whisper millisecond word timestamps.

---

## 📣 6. Dynamic Topic-Matched CTA (Reference: `u0TVV-v1Skg`)

* **Duration:** Dedicated **2.5s – 3.0s Outro Clip** stitched at the end of the video.
* **Topic-Matched Video Background:** Sourced from **100% clean, watermark-free high-resolution stock video** specifically matching the featured animal.
* **Voiceover Script:** Punchy closing biological superpower statement + channel follow invite:
  > *"Nature is full of hidden biological superpowers, just like this one. Follow Wild Mechanics for more."*
* **Visual Typography (`u0TVV-v1Skg` Style):** Centered, bold kinetic word bursts in Electric Yellow (`FOLLOW` $\rightarrow$ `WILD MECHANICS` $\rightarrow$ `FOR MORE.`) without static boxed cards.

---

## 🔍 7. Production Quality Assurance (QA) Checklist

* [ ] **Total Duration Check:** Is the master video $\ge 61.0\text{s}$? (If $< 60.0\text{s}$, the render fails QA and must be re-rendered).
* [ ] **Header Breathing Room:** Is the title cleanly positioned above the 4:5 boundary without touching the edge? ($Y=165$ vs video $Y=285$).
* [ ] **Subtitle Safe Zone:** Are subtitles positioned high enough ($Y \approx 1460$) to avoid YouTube Shorts bottom UI?
* [ ] **Curiosity Title Check:** Does the title evoke strong curiosity rather than presenting a dry fact?
* [ ] **Watermark Check:** Are all broadcaster logos 100% cropped out in the 4:5 viewbox?
