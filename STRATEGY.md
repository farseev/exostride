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

## The 30 guides added on 2026-11-08

Same verdicts, same rules: mostly W1 and W2, then W3 written as search answers, and only two W4 pieces, both on the measured-comparison angle. Each targets a different search question from the nine originals. Content lives in `content/guides/*.txt` and is rendered by `tools/build_guides.py`.

| Whitespace | Pillar | Guide | Primary keywords |
|---|---|---|---|
| W1 | Intelligent Rehabilitation | [A physiotherapist's guide to powered hip exoskeletons](https://exostride.sg/guides/physiotherapist-guide-powered-hip-exoskeleton/) | exoskeleton for physiotherapy patients, physiotherapist exoskeleton guide |
| W1 | Intelligent Rehabilitation | [After a hip or knee replacement: where a hip exoskeleton fits](https://exostride.sg/guides/exoskeleton-after-hip-or-knee-replacement/) | exoskeleton after hip replacement, exoskeleton after knee replacement |
| W1 | Intelligent Rehabilitation | [How to put on a hip exoskeleton seated: a calm routine](https://exostride.sg/guides/how-to-put-on-a-hip-exoskeleton/) | how to put on a hip exoskeleton, wearing an exoskeleton seated |
| W1 | Intelligent Rehabilitation | [Fear of falling: rebuilding walking confidence after a fall](https://exostride.sg/guides/fear-of-falling-walking-confidence/) | fear of falling elderly, walking confidence after a fall |
| W1 | Intelligent Rehabilitation | [Keeping a daily walk in your 70s and 80s in Singapore](https://exostride.sg/guides/daily-walking-routine-older-adults-singapore/) | daily walking routine elderly Singapore, walking exercise for seniors Singapore |
| W1 | Intelligent Rehabilitation | [Wearing a mobility aid without feeling old](https://exostride.sg/guides/wearing-a-mobility-aid-in-public/) | embarrassed to use walking aid, mobility aid stigma |
| W1 | Intelligent Rehabilitation | [Who a powered hip exoskeleton is not for: an honest checklist](https://exostride.sg/guides/who-should-not-use-powered-hip-exoskeleton/) | who should not use an exoskeleton, exoskeleton contraindications |
| W1 | Intelligent Rehabilitation | [Is it working? What to track in the first month with an exoskeleton](https://exostride.sg/guides/tracking-progress-with-a-powered-exoskeleton/) | is my exoskeleton working, exoskeleton progress tracking |
| W1 | Intelligent Rehabilitation | [Keeping up with the grandchildren: school runs and playgrounds](https://exostride.sg/guides/keeping-up-with-grandchildren-mobility/) | grandparent mobility keeping up with grandchildren, grandparents childcare Singapore walking |
| W1 | Intelligent Rehabilitation | [Walking together again: pacing outings with an older parent](https://exostride.sg/guides/walking-together-caregiver-and-parent/) | walking with elderly parent, outings with elderly parent Singapore |
| W1 | Intelligent Rehabilitation | [Getting the home ready for a powered exoskeleton: a checklist](https://exostride.sg/guides/exoskeleton-home-setup-checklist/) | exoskeleton home setup, preparing home for mobility aid |
| W2 | Smoother Commutes | [How to read an exoskeleton spec sheet: the numbers that matter](https://exostride.sg/guides/how-to-read-an-exoskeleton-spec-sheet/) | exoskeleton specifications explained, how to compare exoskeletons |
| W2 | Smoother Commutes | [Is 2.4 kg heavy for an exoskeleton? Where the weight sits](https://exostride.sg/guides/exoskeleton-weight-explained/) | how heavy is an exoskeleton, exoskeleton weight |
| W2 | Intelligent Rehabilitation | ["Up to 80%": how to read exoskeleton performance claims](https://exostride.sg/guides/how-to-judge-exoskeleton-performance-claims/) | exoskeleton claims, does an exoskeleton really work |
| W2 | For Outdoor Sports | [How exoskeleton energy savings are measured: metabolic cost](https://exostride.sg/guides/exoskeleton-metabolic-cost-explained/) | exoskeleton metabolic cost, how are exoskeleton energy savings measured |
| W2 | Smoother Commutes | [Powered vs passive exoskeletons: what is the difference?](https://exostride.sg/guides/powered-vs-passive-exoskeleton/) | powered vs passive exoskeleton, passive exoskeleton |
| W2 | Intelligent Rehabilitation | [Hip, knee or ankle exoskeleton: which joint should be assisted?](https://exostride.sg/guides/hip-vs-knee-vs-ankle-exoskeleton/) | hip vs knee exoskeleton, ankle exoskeleton vs hip exoskeleton |
| W2 | Smoother Commutes | [How does an exoskeleton know when to help? Gait sensing explained](https://exostride.sg/guides/how-exoskeletons-sense-gait/) | how does an exoskeleton work, exoskeleton gait detection |
| W2 | Intelligent Rehabilitation | [Medical vs consumer exoskeleton: what the label means in Singapore](https://exostride.sg/guides/medical-vs-consumer-exoskeleton-singapore/) | is an exoskeleton a medical device, medical exoskeleton Singapore |
| W2 | Smoother Commutes | [How a hip exoskeleton should fit: sizing, straps and pressure points](https://exostride.sg/guides/exoskeleton-fit-and-sizing/) | exoskeleton fit, exoskeleton sizing |
| W2 | Smoother Commutes | [Before you buy an exoskeleton: 12 questions to ask the seller](https://exostride.sg/guides/exoskeleton-buying-checklist-questions/) | exoskeleton buying guide, questions to ask before buying an exoskeleton |
| W3 | Smoother Commutes | [Walking in Singapore heat: pacing a hot, humid commute](https://exostride.sg/guides/walking-in-singapore-heat-commute/) | walking in Singapore heat, hot weather commute Singapore |
| W3 | Smoother Commutes | [When the HDB lift is down: getting up many floors safely](https://exostride.sg/guides/hdb-lift-down-climbing-stairs/) | HDB lift breakdown what to do, climbing many floors of stairs |
| W3 | Smoother Commutes | [Park connector walks with hip assist: planning longer routes](https://exostride.sg/guides/park-connector-walks-with-hip-assist/) | park connector walking Singapore, long walks Singapore |
| W3 | Smoother Commutes | [Steep slopes and ramps: what hip assist changes, up and down](https://exostride.sg/guides/steep-slopes-and-ramps-singapore/) | walking up steep slopes tips, exoskeleton for slopes |
| W3 | Smoother Commutes | [Travelling with a powered exoskeleton: airports and flights](https://exostride.sg/guides/travelling-with-a-powered-exoskeleton/) | travelling with an exoskeleton, can I bring an exoskeleton on a plane |
| W3 | Smoother Commutes | [On your feet all shift: hip assist for jobs with lots of walking](https://exostride.sg/guides/jobs-with-lots-of-walking/) | tired legs from walking at work, jobs with lots of walking |
| W3 | Smoother Commutes | [Sitting on the MRT or bus with an exoskeleton on](https://exostride.sg/guides/sitting-on-mrt-bus-with-exoskeleton/) | can you sit down wearing an exoskeleton, exoskeleton on MRT |
| W4 | For Outdoor Sports | [Bukit Timah Hill with and without hip assist: measure it yourself](https://exostride.sg/guides/bukit-timah-hill-with-and-without-hip-assist/) | Bukit Timah Hill climb, hiking exoskeleton test |
| W4 | For Outdoor Sports | [Knee brace vs powered hip assist for hiking: what each changes](https://exostride.sg/guides/knee-brace-vs-hip-exoskeleton-hiking/) | knee brace vs exoskeleton, knee brace for hiking |

Counts: W1 11 · W2 10 · W3 7 · W4 2.
