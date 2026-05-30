#!/usr/bin/env python3
"""
Autonomous Gig / Tour Finder + Event Planner for Sonic Forage

Run from inside the project (everything stays on Z: drive):
    uv run python scripts/tour_find.py --region "PNW" --type "12hour-donut-rave"

Generates leads + basic harm reduction event plan templates.
Future: real scraping, venue DB, automated outreach emails.

All output in /mnt/z/IMF2045/forage-dj/generated/tour-leads/
"""

import argparse
from datetime import datetime
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Autonomous gig finder and harm-reduction event planner for Sonic Forage")
    parser.add_argument("--region", default="PNW", help="Region (PNW, Oregon, Portland, etc.)")
    parser.add_argument("--type", default="12hour-donut-rave", help="Event type (12hour-donut-rave, club-install, workshop, festival)")
    parser.add_argument("--hours", type=int, default=12, help="Target event length in hours")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.resolve()
    output_dir = project_root / "generated" / "tour-leads"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    lead_file = output_dir / f"leads_{args.region}_{args.type}_{timestamp}.txt"
    plan_file = output_dir / f"harm_reduction_plan_{args.type}_{timestamp}.md"

    print("=== Sonic Forage Autonomous Tour Finder ===")
    print(f"Region: {args.region}")
    print(f"Event Type: {args.type}")
    print(f"Target Length: {args.hours} hours")
    print(f"Output dir: {output_dir}")
    print()

    # Placeholder leads (replace with real scraping later)
    leads = [
        {
            "venue": "Legal Warehouse Collective - Portland",
            "contact": "bookings@warehousecollective.org",
            "capacity": "150-300",
            "tech": "Good power, sound system, projectors OK",
            "vibe": "Underground but permitted, harm reduction friendly",
            "notes": "Has hosted 12+ hour events before. Interested in tech + art crossovers."
        },
        {
            "venue": "PNW Burner Campout Site",
            "contact": "events@pnwburners.net",
            "capacity": "200+",
            "tech": "Generator power available, need to bring GPU rig",
            "vibe": "Radical inclusion + harm reduction culture",
            "notes": "Perfect for donut giveaway + multi-performer autonomous set."
        }
    ]

    with open(lead_file, "w") as f:
        f.write(f"Sonic Forage Tour Leads — {args.region} — {args.type}\n")
        f.write(f"Generated: {timestamp}\n")
        f.write("=" * 70 + "\n\n")
        for i, lead in enumerate(leads, 1):
            f.write(f"LEAD #{i}\n")
            f.write(f"Venue: {lead['venue']}\n")
            f.write(f"Contact: {lead['contact']}\n")
            f.write(f"Capacity: {lead['capacity']}\n")
            f.write(f"Tech: {lead['tech']}\n")
            f.write(f"Vibe: {lead['vibe']}\n")
            f.write(f"Notes: {lead['notes']}\n")
            f.write("-" * 50 + "\n\n")

    # Harm reduction event plan template (12-hour donut rave style)
    plan = f"""# Harm Reduction Event Plan — {args.type.title()} ({args.hours} hours)

**Event Concept**: Legal underground-style rave with autonomous Sonic Forage DJ + multiple human performers. Free donuts + water all night. Give the software away.

## Core Values
- Harm reduction first (donuts, water, education, chill spaces)
- Autonomous tech + human magic together
- Give the tool away — no gatekeeping
- Make money to buy better hardware and do more events

## Performers & Roles (Example for 12-hour set)
- 1-2 Sonic Forage autonomous DJ operators (workstation + live region editing)
- Poi / flow artists
- Magicians / close-up magic
- Body paint / foam artists
- Clowns or comedic characters
- Avaturn reactive characters on screens (bobbing to the music)
- Harm reduction team (water, donuts, info, chill space monitors)

## Schedule Skeleton (8pm → 8am)
- 8pm-10pm: Warmup + meet & greet, free donuts start
- 10pm-2am: Peak energy autonomous sets + live performers
- 2am-6am: Deep / introspective sets + chill zones
- 6am-8am: Sunrise wind-down + giveaway of software + merch

## Tech Rider (Minimal Viable for First Events)
- 1 strong GPU machine (RTX 4090 or better)
- Good sound system + sub
- Projector(s) or LED wall for Avaturn avatars + visuals
- Multiple monitors for workstation view + chat (if streaming)
- Power distribution + UPS
- MIDI controllers (auto-map will handle discovery)

## Harm Reduction Elements (Non-Negotiable)
- Free donuts + water all night
- Chill space with seating, blankets, earplugs
- Trained harm reduction volunteers
- Info table with testing resources, consent, etc.
- "Donut Rave" branding for positivity and approachability

## Outreach Script (Copy-Paste Starting Point)
Subject: Legal 12-hour Donut Rave w/ Autonomous AI Music Workstation + Live Performers

Hi [Venue/Organizer],

We're putting together a legal, harm-reduction focused 12-hour overnight event featuring the Sonic Forage Music Diffusion Workstation (local AI that generates + lets you edit music live).

Concept: Continuous autonomous + human DJ sets + poi, magic, paint, clowns, reactive avatars — all while giving away free donuts and the software itself.

Would love to chat about [date range] at [your space].

Happy to send full rider + harm reduction plan.

Best,
[Your Name]

## Next Steps After Finding a Venue
1. Customize this plan
2. Run `foragedj stream-prep --obs` for any documentation streams
3. Use workstation for the actual sets
4. Document everything and feed back into the project (all in this repo)

This is how we tour, make money for better hardware, and spread the tech responsibly this summer.
"""

    with open(plan_file, "w") as f:
        f.write(plan)

    print(f"✅ Leads saved to: {lead_file}")
    print(f"✅ Full harm reduction event plan saved to: {plan_file}")
    print()
    print("Next autonomous actions:")
    print("  - Review and customize the plan")
    print("  - Start reaching out to the leads")
    print("  - Add real venue data to improve future runs of this script")
    print("  - Use the workstation + Avaturn + multi-performer model at the event")

if __name__ == "__main__":
    main()
