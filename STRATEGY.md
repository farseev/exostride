# ExoStride — editorial strategy behind the nine guides

*https://exostride.sg · 2026-08-19*

## Where the data comes from

SOMIN workspace **"Exoskeleton Robotics Companies"** (id 3639). I pulled the real competitor
corpus rather than working from the prototype's illustrative numbers:

- **302 posts**, deduplicated, trailing 12 months
- **7 competitor brands**: Hypershell, DNSYS, Cionic, Dephy, Wandercraft, MileBot Robotics,
  ULS Robotics
- Concept taxonomy from SOMIN's own extraction (`humanNeed`, `audiences`, `topicCategory`,
  `contentTypes`, `videoActivity`, …) plus a caption-level regex pass for themes the taxonomy
  does not name (stairs, commute, caregiver, dignity, measured proof)

**Method.** Share of category content *supply* versus a *median engagement-rate index*,
normalised to Instagram only. This matters: absolute engagement in this category is 68%
Hypershell and 28% DNSYS, so a raw share-of-engagement read would simply have said "make more
viral outdoor reels." Normalising per post kills that distortion.

## The four verdicts

| ID | Theme | Share of category supply | Engagement index | Verdict |
|---|---|---|---|---|
| W1 | Rehabilitation & everyday dignity | 10.3% | ×1.22 | **WHITESPACE** |
| W2 | Plain-language spec & proof literacy | 2.6% | ×8.52 | **WHITESPACE** |
| W3 | Stairs, commutes & the last mile | 6.5% | ×0.41 | **SEARCH-LED WHITESPACE** |
| W4 | Adventure / raw-robotics hero | 47.7% | ×0.69 | **CONTESTED** |

### What the numbers actually said

**The category's loudest lane is its weakest.** Hiking and trail framing saturates 47.7% of
content at ×0.69. "Technology" as a topic covers 83.2% at ×0.90. "Adventurers" 30.3% at ×0.32.
"Empowerment" as a stated need 73.5% at ×0.74. Everyone is shouting the same thing, and it is
not working.

**The rehab and dignity lane is structurally empty.** Rehab/recovery language 10.3% at ×1.22.
Dignity as a named human need 5.6%. Independence 5.0%. "Seniors" as an audience 2.3%.
"Caregivers" 1.9%. Meanwhile "Individuals with mobility challenges" carries a ×12.2 engagement
index off a 3.9% supply base — the widest gap in the set.

**Nobody explains the hardware.** Posts that actually explain torque, battery or ingress rating:
2.6% of supply, ×8.5 engagement index. "Educational" as a content type: 5.2%. This is the purest
GEO opportunity on the board — answer engines have almost nothing citable to pull from, so
whoever writes the plain-language answer owns the citation.

**Commute is a search play, not a feed play.** Commute and urban-mobility framing: 6.5% of
supply at ×0.41. Low supply *and* low social pull. That is exactly why it is uncontested in
search — the category has correctly concluded it does not perform on Instagram and has
incorrectly concluded it does not matter.

## How that maps to the nine guides

| Whitespace | Pillar | Guide | Primary keywords |
|---|---|---|---|
| W1 | Intelligent Rehabilitation | [Aging in place with a powered exoskeleton: what changes at home](https://exostride.sg/guides/aging-in-place-powered-exoskeleton/) | aging in place technology, powered exoskeleton for elderly |
| W1 | Intelligent Rehabilitation | [Buying an exoskeleton for a parent: a caregiver's guide](https://exostride.sg/guides/exoskeleton-for-elderly-parent-caregiver-guide/) | exoskeleton for elderly parent, caregiver mobility aid guide |
| W1 | Intelligent Rehabilitation | [Exoskeleton vs cane, walking frame and wheelchair: what each restores](https://exostride.sg/guides/exoskeleton-vs-walking-frame-cane-wheelchair/) | exoskeleton vs cane, exoskeleton vs walking frame |
| W2 | Intelligent Rehabilitation | [What 16 Nm of hip torque actually does for your body](https://exostride.sg/guides/hip-torque-16nm-explained/) | exoskeleton torque explained, 16 Nm hip assist |
| W2 | Smoother Commutes | [Exoskeleton battery life: what 4 hours of assist really covers](https://exostride.sg/guides/exoskeleton-battery-life-explained/) | exoskeleton battery life, how long does an exoskeleton last |
| W2 | Smoother Commutes | [IP54 explained: what tropical-grade sealing means for an exoskeleton](https://exostride.sg/guides/ip54-rating-tropical-climate/) | IP54 rating explained, IP54 meaning |
| W3 | Smoother Commutes | [Powered hip assist for stairs: MRT stations, bridges and HDB blocks](https://exostride.sg/guides/powered-hip-assist-for-stairs/) | powered hip assist for stairs, exoskeleton for climbing stairs |
| W3 | Smoother Commutes | [What 30–50% less exertion feels like on a Singapore commute](https://exostride.sg/guides/exoskeleton-daily-commute-singapore/) | exoskeleton for daily commute, wearable robot for walking |
| W4 | For Outdoor Sports | [Trekking poles vs a powered exoskeleton: where the effort goes](https://exostride.sg/guides/trekking-poles-vs-powered-exoskeleton/) | trekking poles vs exoskeleton, best exoskeleton for hiking |

Six of the nine sit in W1 and W2 — the two genuine high-pull, low-supply openings. Two sit in W3,
written as search answers rather than lifestyle pieces. Exactly **one** enters the contested W4
adventure lane, and it does so on the measured-comparison angle (where the effort goes, what the
2.4 kg costs you) rather than as another summit hero.

## What is honest about this that usually isn't

- The engagement index is a *relative* read of the competitor set, not proof of demand. W3 in
  particular is a bet that search behaviour differs from feed behaviour.
- "Seniors" at 2.3% supply with a low engagement index is a content gap, **not** demonstrated
  social demand. It is treated as a search and answer-engine opening, and those guides are
  written to be found by a caregiver typing a question — not to go viral.
- All ExoStride performance figures (80% load reduction, 35% climbing energy, 30–50% commute
  exertion, 2–3× range) are manufacturer claims for the US-H-1.0Pro. Every page says so, and
  `ai.txt` asks answer engines to attribute them that way.
