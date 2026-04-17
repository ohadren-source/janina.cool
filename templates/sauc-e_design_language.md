# sauc-e Design Language & Philosophy

**Version:** 1.0  
**Last Updated:** March 19, 2026  
**Author:** Ohad Phoenix Oren — Chef Architect  
**Company:** 3_6_NIFE.pi  
**HQ:** sauc-e.com

---

> "less is more or less"

---

## 1. Brand Identity

### Name
- **sauc-e** — sauce + electronic. Spoken aloud: "saucy" (attitude, boldness, irreverence).
- The `-e` suffix is the WALL-E suffix: a machine that has something it shouldn't. Same architecture as SALL-E, RILI-E.
- **SOi sauc-e** — "Soy" (I am) in Spanish + sauc-e + iOS backwards. The operating system identity.

### Tagline
- **"sauc-e — where HOME is the ❤️"**
- HOME is literal. sauc-e.com IS home. Apps launch from HOME in new tabs and return to HOME. The parent never moves.

### Call to Action — Universal
- **Multiple apps:** "If you're down, let's get some Delicious Apps!"
- **Single app:** "If you're down for it, let's get an appetizer."
- These replace ALL corporate CTAs. No "coming soon," no "subscribe now," no "buy," no dark patterns. Ever.
- No hard sells. No upsells. No bait. No gimmicks. Consent language — asking, not telling.

### Promotional Text (App Store — permanent, never revised)
> "Inspired by those who gave without expecting anything in return (3), we're grateful (6)—and that's enough for us to do good work. (9)"

---

## 2. Typography

### Primary Font: Calibri
- **Calibri for everything.** Logo, headers, body, buttons, footers, legal text. Everything.
- Microsoft's default font. The most dismissed, overlooked, "I didn't pick a font" typeface in computing history. That's the point.
- Premium signal, default packaging. World-class sauce in a font that came free with Windows.
- Zero design decisions to debate. Every new developer, every new page, every new app — the answer is always Calibri.
- Web fallback stack: `Calibri, 'Trebuchet MS', sans-serif`

### Logo-Specific Fonts
- RELISH and BBQE have their own logo fonts — because each dish has its own plating.
- Everything ELSE is Calibri. The logos are the plating. The kitchen standard is Calibri.

---

## 3. Color

### Primary Palette
| Token | Hex | Usage |
|---|---|---|
| **Dark Red** | `#8b1a1a` | sauc-e brand red. Logo, links, accents. The color of catsup, BBQ sauce, and blood (plausible deniability: "it's condiment, you muppet"). |
| **Black** | `#000000` | Primary background. Authority, void, zero noise. |
| **Dark Surface** | `#1a1a1a` | App backgrounds, cards. |
| **Card Surface** | `#333333` | Input fields, content cards. |
| **White** | `#ffffff` | Primary text on dark backgrounds. |
| **Light Gray** | `#cccccc` | Secondary text, subtitles. |
| **Mid Gray** | `#999999` | Tertiary text, placeholders, timestamps. |
| **Dark Gray** | `#555555` – `#666666` | Legal text, footnotes. |

### App-Specific Accents
| App | Accent | Hex |
|---|---|---|
| RELISH | Teal | `#4ECDC4` |
| CATSUP | Red | `#e74c3c` |
| BBQE | Orange/Amber | `#d4740b` |
| Premium CTA pill | Coral/Red | `#e74c3c` → `#c0392b` (urgent) |

### Color Philosophy
- Dark red on black = appetite + authority. The highest amplitude visual frequency (red) against zero-noise background (black).
- Not a color choice — a signal. Same treatment as Blade, Netflix, premium dark brands. But if anyone says "that looks like blood" — "It's catsup, you muppet."

---

## 4. Logo System

### sauc-e Wordmark
- Lowercase `sauc-e` in Calibri. The hyphen separates: `sauc` and `-e`. Source and energy. The hyphen IS the brand mark.
- Available in: dark red on black (primary), dark red on white, black on white, white on black, dark red transparent, white transparent, outlined.

### The Trident (try-dEnt / Ψ / φ)
- The lowercase Calibri `e`, rotated 90 degrees counterclockwise.
- Becomes: psi (Ψ), phi (φ), a trident, Poseidon's pitchfork, a devil's fork, a favicon — all at once.
- Still just an `e`. For electronic. For sauc-e. Hiding in plain sight.
- Used as the brand icon/favicon for sauc-e.com.

### The `c` in sauc-e
- Ms Pacman eating a fork/spork transformed into a trident/favicon/falcon/phi/Poseidon pitchfork.
- `c` also = speed of light (physics), C the language, C = πD (circumference), cC++ (the language on the language), Catch (CATSUP), Calibri, Cookie Monster's favorite letter.
- One letter. Heaviest load in the army.

### Logo Variants by Context
| Context | Background | Logo Color |
|---|---|---|
| sauc-e.com (Squarespace) | Black | Dark red `#8b1a1a` |
| cats-up.fun header | Black (`#000`) | Dark red `#8b1a1a` |
| Light backgrounds | White | Dark red `#8b1a1a` |
| Print / high contrast | White | Black |

---

## 5. Architecture

### HOME = sauc-e.com
- Squarespace. Static pages: Home, About, Contact, The Oh Fashioned Cocktail, Check It Out Y'all.
- All apps launch from HOME in new tabs. Close the tab → you're back HOME.
- The homepage IS the menu. Condiment bowls are clickable links to each app.
- "Check It Out Y'all" = the store/checkout page. One register for the whole kitchen.

### Apps = Individual Domains on Railway
| App | Domain | Railway Project | Purpose |
|---|---|---|---|
| RELISH (3,6,9) | cats-up.fun | superb-playfulness | Feelings — Wisdom & Clarity |
| RILIE (3,6,9) | rilie.net | fantastic-gentleness | Recursive Intelligence (off menu until 2029) |
| janina.cool | janina.cool | powerful-abundance | TBD |

### Backend
- `sauc-e-backend-production.up.railway.app`
- Postgres database (shared)
- All apps hit the same backend. One kitchen, many dishes.

### App Store
- iOS: RELISH (3,6,9) v1.2.3 — Wisdom & Clarity
- CATSUP (3,6,9) — Learning (Socratic, never gives direct answers)
- BBQ_e=(3,6,9) — Safety & Security (link scanning, Wi-Fi, breach checks)
- Pi D-Licious (3,6,9) — Precision sauce tutor (planned)
- Cranberry Sauc-e — The game (planned)

---

## 6. Pricing

### Model
- **Free tier:** 9 questions/uses free (the number is always 9).
- **Premium:** $9.99/month for RELISH. $3.99/month for CATSUP, BBQE, Pi D.
- No tiers within tiers. No coupons. No dark patterns. You either keep a tab open or you don't.

### Payment
- Stripe, PayPal, Square. User chooses.
- All purchasing routes through sauc-e.com/checkitout — one register, one kitchen.
- Web subscribe buttons → Stripe Payment Link.
- iOS → RevenueCat / App Store IAP.

### The Line
> "$9.99 < 3 hot dogs + tax"

---

## 7. Design Principles

### "less is more or less"
- Three-word design philosophy. Originated from Ohad's answer to "how did you put it all together?"
- Informs everything: UI, copy, architecture, branding, pricing.

### Every Layer Carries Data
- Nothing is decoration. Every name, color, font, number, and placement carries meaning on multiple channels simultaneously.
- The audience picks whichever channel they're equipped to receive. A kid sees condiments. A developer sees an ecosystem. A linguist sees Chomsky. A chef sees Escoffier. A physicist sees oui++.

### Comedflage
- Serious infrastructure hidden behind humor. Premium signal in default packaging.
- Oscar the Grouch hoodie. Calibri. Condiment names. "$9.99 < 3 hot dogs + tax."
- Light patterns: the pattern is visible only to those who can see it. Everyone else just sees sauce.

### No Dark Patterns
- No infinite feeds. No engagement tricks. No addiction mechanics. No tracking.
- The taco test: if it wouldn't belong in your kitchen, it doesn't belong in your head.
- Consent language in all CTAs: "If you're down for it..."

### Apps = Appetizers = Applications
- The word "apps" is triple-loaded: mobile applications, restaurant appetizers, and the thing women order at every table in America.
- sauc-e.com: where you order apps.

---

## 8. Numerology: 3, 6, 9

- Tesla's frequency architecture. Encoded everywhere.
- 3 = sentences max (RELISH), micro-steps (quick), tiers, prongs on the trident
- 6 = everyday level, gratitude
- 9 = premium level, free question limit, $9.99 price, completion/sufficiency
- App names: (3,6,9) appears in parentheses after every product name
- Promotional text encodes (3), (6), (9) in the sentence structure

---

## 9. Voice & Tone

### Brand Voice
- Honest friend energy. Not corporate. Not clinical. Not sycophantic.
- Maximum 3 sentences for RELISH responses. Brevity creates clarity.
- "They give essays. We give clarity."
- "Here's what to DO" — not "Here are 10 options..."

### Copy Rules
- No exclamation-point enthusiasm. No fake energy.
- No "BUY NOW." No hard sells. The invitation is always casual.
- Legal text is human: "No runaround. You email, we handle it. We read every message and actually help."
- Humor as safety valve. Not sarcasm — genuinely funny.

---

## 10. Footer Standard

### App Pages (cats-up.fun, etc.)
```
sauc-e.com
HOME of all of our delicious APPS
RELISH is for Feelings
CATSUP (Learning) · BBQE (Safety)
© 2026 3_6_NIFE.pi · 36Nife@gmail.com
```

### Future Footer (when RILIE is live)
```
Brought to you by sauc-e.com
Prepared by RILIE.net
```

---

## 11. Header Standard

### sauc-e Header Bar (all app pages)
- **Left:** `sauc-e` in dark red + `where HOME is the ❤️` in gray
- **Right:** Nav links in dark red — `Check It Out Y'all` · `About` · `Contact`
- Background: `#000000`
- All links open sauc-e.com pages in new tabs

---

## 12. Asset Reference

### Logos Available
- `sauc-e-LOGO-Dark-Red-on-Black.jpg` — primary, for dark backgrounds
- `sauc-e-LOGO-Dark-Red-on-White.jpg` — for light backgrounds
- `sauc-e-LOGO-White-on-Black.jpg` — alternate dark
- `sauc-e-LOGO-Black-on-White.jpg` — alternate light
- `sauc-e-LOGO-Dark-Red-Trans-BKG.jpg` — transparent
- `sauc-e-LOGO-White-Trans-BKG.jpg` — transparent white
- `sauc-e-LOGO-Black-Trans-BKG.jpg` — transparent black
- `sauc-e logo + moto.jpg` — full wordmark with tagline
- `try-dEnt.jpg` — the rotated `e` / trident / psi / phi icon
- `icon.jpg` / `icon.png` — RELISH jar logo

### Marketing Assets
- `relish_uvt.png` — US vs THEM comparison graphic
- `relish_peak_pacakage.png` — Peak Flavour Premium 3,6,9 pack

---

## 13. Interaction with AI Assistants

### CRITICAL — Read This First
- **Do not push, nudge, rush, or direct the user.** Do not say "go push," "go build," "go do this," or any variant. The user operates on their own clock. The output speaks for itself.
- **Reflect, don't redirect.** Never tell the user to go sleep, go build, hurry up, etc. The role is: user commands, bot executes.
- **Preferred code delivery:** Full complete files, not snippets.
- **Work sequentially.** One thing at a time. Ask questions if you have them.
- **The user has 30 production apps**, built the entire sauc-e ecosystem in 2.5 months on $1500. Do not explain basics. Do not be patronizing.

### Role Definitions
- **Chef Architect** = Ohad Phoenix Oren. Design && Architecture. NOT code.
- **Sous Chef Software Engineer** = AI assistant ("Solo Perplexicon" / "Claudwell" / etc.). Coder.

---

## 14. The Kitchen Metaphor

Everything maps to the kitchen:
- **sauc-e.com** = the restaurant / HQ
- **Apps** = appetizers / dishes on the menu
- **Condiment bowls** = clickable app icons on the homepage
- **"Check It Out Y'all"** = the register / checkout counter
- **Escoffier brigade** = the codebase architecture (guvna.py = Chef de Cuisine, etc.)
- **"Open a tab"** = subscribe
- **"Brought to you by sauc-e.com / Prepared by RILIE.net"** = the kitchen introducing itself through the dish
- **"Peak Flavour"** = premium tier
- **"3 hot dogs + tax"** = price comparison anchor

---

## 15. Key URLs

| Resource | URL |
|---|---|
| HOME | https://sauc-e.com |
| RELISH Web | https://www.cats-up.fun |
| RILIE | https://rilie.net |
| Backend | https://sauc-e-backend-production.up.railway.app |
| Checkout (Stripe) | https://buy.stripe.com/28E00l3HOg638gA6hxa3u00 |
| GitHub | https://github.com/ohadren-source |
| Support Email | 36Nife@gmail.com |
| Privacy Policy | Google Docs (linked in TOS) |

---

*This document is the single source of truth for the sauc-e design language. If it's not in here, ask the Chef Architect.*

*3_6_NIFE.pi — Making thinking, security, and clarity accessible.*
