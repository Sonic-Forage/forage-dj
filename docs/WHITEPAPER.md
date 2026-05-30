# White Paper: ForageDJ — Prompt-Based AI DJ DAW with Setlist-as-Score and Seed-Variational Experiences

**Version 0.1 — May 30, 2026**
**Authors:** Grok (xAI) + M1nd 3xpand3r / Sonic Forage Collective
**Affiliation:** Sonic Forage Mycelium — Open-Source AI Creative Tools for Rave Culture

## Abstract

ForageDJ is an open-source, local-first AI-powered DJ interface and digital audio workstation (DAW) that reimagines music creation and performance as a prompt-driven, seed-variational process. Unlike real-time continuous diffusion engines (e.g., Daydream's DEMON for low-latency streaming generation), ForageDJ emphasizes **simple, accessible generation + traditional mixing** with hardware controller support (Numark NS7II), autonomous setlist curation, and infinite experiential variation through prompt sets + random seeds.

Core innovation: Treat **setlists as executable prompt scores**. A single setlist of text prompts generates a coherent DJ set; changing only the random seed produces an entirely new sonic realization while preserving structure, energy arcs, and transitions. This embraces the stochastic nature of diffusion models (Stable Audio 3) to deliver "one prompt, infinite mixes" — democratizing professional-grade AI music for home producers, rave organizers, and live performers on potato machines.

We integrate Stable Audio 3 small models (CPU-friendly), real-time mixing (sounddevice + pedalboard), MIDI/OSC hardware mapping, voice commands, stem separation (Demucs), and autonomous agents (building on Sonic Forage's Ralph loop + safety gates). The result is a forkable, public-safe tool that lowers barriers to AI-augmented DJing while embedding harm-reduction and cultural values from the Sonic Forage ecosystem.

**Keywords:** AI music generation, diffusion models, DJ DAW, prompt engineering, setlist curation, seed variation, local-first AI, agentic systems, Stable Audio 3, MIDI controllers, rave culture tools.

## 1. Introduction & Motivation

The 2025–2026 explosion of audio diffusion models (Stable Audio 3, Suno v5, Udio, Google's Lyria 3, Daydream DEMON) has made high-quality text-to-music generation accessible. However, most tools fall into two camps:

1. **End-to-end song generators** (Suno, Udio, MusicGenAI): Great for full tracks but lack live mixing, hardware integration, or performance workflows.
2. **Real-time continuous engines** (Daydream DEMON — 25Hz diffusion, sub-100ms latency, local-first streaming/modulation): Excellent for live improvisation and endless generation, but require constant model inference, higher compute, and different UX (more instrument than DAW).

ForageDJ occupies a pragmatic middle ground: **Batch prompt generation + professional DJ/DAW controls**. Users generate tracks on-demand (or pre-generate setlists), mix them live with familiar faders/EQ/crossfader on hardware like the Numark NS7II, and leverage AI for autonomous transitions, voice commands, and stem remixing.

**Key differentiator — Setlist as Prompt Score + Seed Variation:**
- A setlist is a sequence of prompts (e.g., "dark techno intro 128bpm", "uplifting breakdown with vocal chops", "hard drop with SFX").
- Generate the entire set once with seed=42 → coherent 60-min experience.
- Change to seed=1337 → completely different realizations of the *same structural score* (different melodies, textures, but same energy curve and transitions).
- This turns prompt engineering into a new form of musical composition: the prompt set is the "score," the seed is the "performance interpretation."
- Infinite unique sets from one prompt list; perfect for repeat plays, A/B testing, or community sharing of "setlist recipes."

This aligns with broader trends in agentic AI for music (Spotify's voice DJ, live music agents research at CHI 2026) and structured generation (ProGress graph diffusion for coherent compositions).

## 2. Related Work

### 2.1 Audio Diffusion Models
- Stable Audio 3 (Stability AI, May 2026): Latent diffusion with SAME autoencoder; small models (0.6B) run on CPU, variable length up to 120s+, inpainting/LoRA/editing. Prefix prompts for music vs. SFX. Our foundation.
- Daydream DEMON (2026): Real-time local diffusion at 25Hz for continuous music control — inspirational for latency but orthogonal to our batch + mix model.
- Earlier: Stable Audio 1/2, AudioLCM (fast consistency models), ProGress (graph diffusion + Schenkerian analysis for structured music).

### 2.2 AI DJ & Live Music Agents
- "A Design Space for Live Music Agents" (CHI 2026, Kim et al.): Surveys latency, efficiency, and generative capabilities in live settings; notes gap in broad audio generation on commodity hardware — exactly what small Stable Audio 3 + our mixer addresses.
- Spotify DJ (2025+): Voice/text requests → personalized playlists with agentic refinement.
- Dadabots Prompt Jockeys, Google MusicFX DJ, Nao Tokui AI DJ (historical): Prompt or symbolic control for performances.
- LLM2Fx-Tools (Sony AI, 2026): LLM-driven audio effects chains for post-production — relevant for our effects rack.

### 2.3 Responsible & Cultural AI Music
- Reviews on responsible AI music generation (Wilson et al., 2025): Emphasize dataset biases, artifacts in long-form, and need for human oversight — our safety gates and public-safe defaults directly address.
- Sonic Forage ecosystem (2026): Rave-harm-reduction kits, autonomous booking with closed gates, master prompt arcade — cultural backbone.

## 3. System Architecture

(Refer to ARCHITECTURE.md for full diagram.)

**Layers:**
- **Generation Layer**: Stable Audio 3 wrapper (small-music for tracks, small-sfx for pads). Prompt formatting with prefixes, duration control, seed injection for reproducibility/variation.
- **Mixing Layer**: Real-time Deck + Mixer (rtmixer/sounddevice + pedalboard EQ/filter/effects). BPM/key sync via librosa.
- **Control Layer**: MIDI (mido/rtmidi + NS7II mapping + Learn), OSC (Touch OSC), Voice (faster-whisper + local LLM intent).
- **Agentic Layer**: Setlist executor (prompt sequence → generate → auto-transition), Ralph loop integration from sonic-forage-autonomous-dj-os, safety gates (human approval for any public/booking actions).
- **UI Layer**: Dear PyGui (decks, waveforms, prompt panels, library, seed control, setlist editor).

**Setlist-as-Score Mechanism:**
- Setlist JSON: `[{prompt: str, duration: int, transition: str, seed?: int}, ...]`
- Generate function: For each item, call SA3 with prompt + global_seed or per-item seed. Store with metadata (prompt, seed, BPM, key).
- Playback: Sequential load + crossfade logic; agent can vary seed on re-generate for new take.
- Export: Full set package (WAVs + prompts + seeds + safety metadata) for sharing/reproducibility.

## 4. Key Innovations

1. **Prompt Score + Seed Variation**: First tool to explicitly treat prompt sequences as musical scores with stochastic interpretation via seeds. Enables "one setlist, infinite unique performances."
2. **Hybrid Batch + Live**: On-demand or pre-gen tracks + professional low-latency mixing/hardware — accessible on potato machines (no 25Hz continuous inference needed).
3. **Hardware-First + Agentic**: Full NS7II mapping + MIDI Learn + voice + autonomous Ralph loop for hands-on or hands-off use.
4. **Cultural Embedding**: Every track embeds harm-reduction note + prompt provenance; closed gates for autonomous actions; public-safe defaults.
5. **Forkable Mycelium**: Built on Sonic Forage repos; easy to extend with new models (future Stable Audio, LoRAs), GUIs (Tauri), or backends.

## 5. Implementation Roadmap (Aligned with AGENTIC_BUILD_PLAN.md)

- **Phase 1 (MVP)**: 2-deck GUI, SA3 generation with seed control, basic mixer/EQ/filter, prompt input, simple setlist runner (generate all, play sequentially).
- **Phase 2**: NS7II MIDI + Learn, voice commands, auto-mix with seed variation option.
- **Phase 3**: Full setlist editor (drag-drop prompts, per-item seed override, preview), stem separation + SFX pads, autonomous agent with Ralph loop.
- **Phase 4+**: 4-deck, library with search-by-prompt, LoRA UI, community setlist vault (with safety review), one-click installer.

## 6. Evaluation & Future Work

**Metrics**: Generation time (<25s for 60s track on CPU), latency (<10ms control), musical coherence (BPM/key match, transition quality via human eval), usability (controller mapping success rate), cultural compliance (all tracks embed safety metadata).

**Future**:
- Real-time partial generation / continuation (inpainting from SA3) for live tweaks.
- Multi-agent collaboration (multiple ForageDJ instances syncing setlists).
- Integration with structured models (ProGress-style graph diffusion for better long-form coherence).
- User studies with DJs/rave organizers on prompt-score usability.
- Responsible scaling: Bias audits on generated outputs, dataset provenance.

## 7. Conclusion

ForageDJ demonstrates that the power of 2026 audio diffusion models can be harnessed not just for isolated track generation, but for a full, accessible, hardware-integrated DJ workflow that treats prompts as a new compositional language. By combining batch generation, traditional mixing paradigms, setlist-as-score with seed variation, and strong cultural/safety foundations from the Sonic Forage mycelium, we create a tool that is simultaneously simple for beginners, powerful for performers, and infinitely replayable through stochastic variation.

This is not a replacement for live diffusion engines like DEMON or professional DAWs — it is a complementary layer that makes AI music *performable* and *shareable* in the context of rave culture, home studios, and agent-augmented creativity.

**Fork it. Change the seed. Play it different every time.**

---

**References**
1. Stability AI. (2026). Stable Audio 3 Technical Report. https://stability.ai/...
2. Kim et al. (2026). A Design Space for Live Music Agents. CHI 2026.
3. Daydream. (2026). DEMON: Real-time Local Music Diffusion. https://daydream.live/
4. Wilson et al. (2025). A Short Review of Responsible AI Music Generation.
5. Vignac et al. (2023/2025 updates). DiGress / ProGress structured diffusion.
6. Sonic Forage Collective. (2026). autonomous-dj-os, rave-harm-reduction-community-kit. https://github.com/Sonic-Forage

*This white paper is a living document. Contributions welcome via PR.*
