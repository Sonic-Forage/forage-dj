# Autonomous Event & Tour System

**Purpose**: Find, book, and run gigs autonomously so we can make money, go on tour, give the software away, and spread harm reduction + this tech.

## Core Ideas from User
- Schedule/book autonomous DJ sets
- Hire additional performers (magicians, clowns, poi dancers, foam/paint artists)
- Give out donuts at events (harm reduction + culture)
- At least one legal underground-style 12-hour set (8pm–8am) passing out donuts
- Install autonomous systems at nightclubs, strip clubs, raves, festivals, workshops
- Make money to buy GPUs + hardware → keep improving and giving away

## 12-Hour "Donut Rave" Concept (Signature Event)
- Legal warehouse / permitted venue
- 8pm to 8am
- Continuous autonomous + human DJ sets using the workstation (regenerate regions live based on energy/crowd)
- Multiple side performers: magic, poi, body paint, foam, clowns
- Free donuts + water + basic harm reduction info all night
- Avaturn characters on screens reacting to the music
- QR codes everywhere pointing to the project (give the software away)
- Goal: Prove the model works and document everything for replication

## Autonomous Gig Finding & Booking
Tools we will build (in `scripts/` and via agents):

- `scripts/find_gigs.py` or `foragedj tour-find`
  - Scrapes or suggests PNW venues (underground legal, clubs, warehouses, small festivals)
  - Filters by: capacity, vibe, tech requirements (GPU + good sound + projectors)
  - Outputs contact templates + rider

- Event planning templates:
  - Full rider (hardware, power, internet for updates, multiple performers)
  - Harm reduction rider (donuts, water, trained people on site)
  - Multi-performer coordination checklist

## Revenue Models (Fast Cash for GPUs)
1. Paid private installs + workshops at clubs/festivals
2. "Autonomous system rental" for events (we set it up and it runs)
3. Collective royalties (when people use shared tracks in sessions)
4. Ticketed signature events (Donut Rave model)
5. Festival deals once we have proof-of-concept

## Venues & Scenes to Target First
- PNW underground / legal warehouse scene
- Small electronic festivals
- Nightclubs & strip clubs (autonomous background/ambient systems)
- Rave workshops & skill shares
- Art collectives & burner events

## Integration with Existing Tech
- Use the new **workstation** for live editable sets
- **Avaturn avatars** as visual performers on screens
- **Kick/Twitch** for remote participation or documentation streams
- **MIDI auto-map** so any controller at a new venue just works
- **stream-prep** + clean visuals for any documentation streams

## Next Autonomous Actions
- Build basic `scripts/tour_find.py` that outputs venue suggestions + contact scripts
- Create full production plan + budget for first 12-hour Donut Rave
- Add "Event Mode" preset in the retro OS and CLI (harm reduction defaults, multi-performer support, avatar layer on by default)
- Start lightweight outreach list for NW Oregon small artists + venues

This is how we turn the tool into real income and real cultural impact this summer.
