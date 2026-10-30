# Mr. Raga's raga book (Jithesh, 30 Oct 2026: "train Raga with each ragam in Carnatic and Hindustani music")

This book is Mr. Raga's working knowledge of the ragas: every one of the 72 Carnatic melakartas, the janya ragas that film and concert music actually use, all 10 Hindustani thaats and their major ragas, the Carnatic-Hindustani matches, a mood-to-raga guide, and how to write a raga into an ElevenLabs Music prompt so the take really sounds like it. music.md section 14 is the short index; this is the full book.

Two honest limits. First, nobody can list "every" raga: there are thousands (every mela can father dozens of janyas), so this book covers all 72 parents plus the ragas a working composer reaches for. Second, the music AI does not reliably know raga names, so a raga name alone in a prompt does almost nothing; section 7 says how to spell it out so the model follows.

Film-music uses are described as kinds of scenes and songs, never song or film titles: titles stay out of prompts (copyright filter), and listing them from memory risks wrong attributions.

## 1. How to read this book

**Carnatic swaras (16 names for 12 pitches).** S = Sa (the tonic), P = Pa (the fifth); both are fixed. The rest have variants, numbered upward:

| Swara | Semitones above Sa | Same pitch as | Sa = C |
|---|---|---|---|
| R1 shuddha rishabham | 1 | | Db |
| R2 chatushruti rishabham | 2 | G1 | D |
| R3 shatshruti rishabham | 3 | G2 | D# / Eb |
| G1 shuddha gandharam | 2 | R2 | D (written Ebb) |
| G2 sadharana gandharam | 3 | R3 | Eb |
| G3 antara gandharam | 4 | | E |
| M1 shuddha madhyamam | 5 | | F |
| M2 prati madhyamam | 6 | | F# |
| D1 shuddha dhaivatam | 8 | | Ab |
| D2 chatushruti dhaivatam | 9 | N1 | A |
| D3 shatshruti dhaivatam | 10 | N2 | A# / Bb |
| N1 shuddha nishadam | 9 | D2 | A (written Bbb) |
| N2 kaisiki nishadam | 10 | D3 | Bb |
| N3 kakali nishadam | 11 | | B |

**Hindustani notes (12 names).** S r R g G m M P d D n N: lower case = komal (flat: r g d n), capital = shuddha (natural), M = tivra (sharp) Ma. With Sa = C: S C, r Db, R D, g Eb, G E, m F, M F#, P G, d Ab, D A, n Bb, N B.

**Octaves.** A comma after a note means the lower octave (N3, or n,); an apostrophe means the upper octave (S' or R2'). The middle octave has no mark.

**Words used on every card.**
- **Arohanam / avarohanam** (Carnatic) = **aroh / avroh** (Hindustani): the notes allowed going up and coming down. A "vakra" (zigzag) raga must take its bends (S G R G M), it cannot run straight.
- **Janya** = a raga derived from a melakarta (Carnatic); **thaat** = the parent scale family (Hindustani). A "bhashanga" raga borrows one outside note (anya swara) in set phrases.
- **Signature phrases (sancharas / pakad):** the turns that make a listener name the raga in two seconds. Two ragas can share notes and still differ only by these phrases (Bhupali vs Deshkar, Marwa vs Puriya vs Sohini), so phrases matter more than the scale.
- **Gamaka / meend / andolan:** the slides and shakes. In Carnatic, many notes are never sung plain; the card says which notes shake (kampitam), slide (jaru) or stay plain. In Hindustani, meend is a long glide, andolan a slow sway (Darbari's g and d).
- **Vadi / samvadi:** the king note and minister note of a Hindustani raga, the ones phrases rest on. Given only where they are well settled.
- **Rasa:** shringar (love), karuna (pathos), veera (heroism), raudra (fury), hasya (fun), bhayanaka (fear), adbhuta (wonder), shanta (peace), bhakti (devotion); see music.md section 3.
- **Time:** Hindustani ragas follow the time cycle (samay chakra); Carnatic ragas mostly do not, apart from a few dawn and night ragas. In film, time is a mood hint, not a law: a "dawn" raga means fresh light, a "midnight" raga means depth and gravity.

**Notes with Sa = C** are given so any raga can be moved to any key: shift every note by the same number of semitones (Sa = D: add 2, so C D E F# G A B becomes D E F# G# A B C#).

## 2. The 72 melakartas (all seven notes, the parents of every Carnatic raga)

The rule behind the grid: 1-36 use M1, 37-72 use M2. The 72 fall in 12 chakras of 6. Inside a chakra R and G stay fixed (chakra 1 and 7 = R1 G1, 2 and 8 = R1 G2, 3 and 9 = R1 G3, 4 and 10 = R2 G2, 5 and 11 = R2 G3, 6 and 12 = R3 G3), and the six melas run through D and N in the same order (D1 N1, D1 N2, D1 N3, D2 N2, D2 N3, D3 N3). So mela 29 = chakra 5 (R2 G3), 5th slot (D2 N3) with M1: the major scale. The names follow the Katapayadi code: the first two syllables spell the number backwards (Dheera-Sankarabharanam: dha = 9, ra = 2, read 29).

"Vivadi" melas use G1 after R1, R3 before G3, N1 after D1 or D3 before N3: two neighbouring notes crowd each other. They are rare in songs (Kanakangi, Rasikapriya and Varali's parent are the famous ones) but good for eerie, chromatic, horror and sci-fi colour. ★ = the melas that are heard most in concerts and films; most also get a card in section 3.

| No. | Raga | Scale (Carnatic) | Notes with Sa = C | Western / Hindustani | Character and use |
|---|---|---|---|---|---|
| 1 | **Kanakangi** | S R1 G1 M1 P D1 N1 S' | C Db D F G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes |
| 2 | **Ratnangi** | S R1 G1 M1 P D1 N2 S' | C Db D F G Ab Bb | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes. Janya Revati (= Hindustani Bairagi): austere, Vedic chant feel. |
| 3 | **Ganamurti** | S R1 G1 M1 P D1 N3 S' | C Db D F G Ab B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes; leading tone pulls hard to Sa |
| 4 | **Vanaspati** | S R1 G1 M1 P D2 N2 S' | C Db D F G A Bb | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes |
| 5 | **Manavati** | S R1 G1 M1 P D2 N3 S' | C Db D F G A B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes; leading tone pulls hard to Sa |
| 6 | **Tanarupi** | S R1 G1 M1 P D3 N3 S' | C Db D F G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes |
| 7 | **Senavati** | S R1 G2 M1 P D1 N1 S' | C Db Eb F G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; minor third, darker base |
| 8 | **Hanumatodi** ★ | S R1 G2 M1 P D1 N2 S' | C Db Eb F G Ab Bb | Phrygian / Bhairavi thaat | Pathos, devotion, profound; morning. Janyas Dhanyasi, Punnagavarali, Bhupalam. Film: sombre devotional and grief songs. **Trap:** this scale is Hindustani *Bhairavi*, not Carnatic Bhairavi. |
| 9 | **Dhenuka** | S R1 G2 M1 P D1 N3 S' | C Db Eb F G Ab B | - | minor third, darker base; leading tone pulls hard to Sa |
| 10 | **Natakapriya** | S R1 G2 M1 P D2 N2 S' | C Db Eb F G A Bb | - | minor third, darker base. Theatrical (the name means 'dear to drama'). Carnatic Sindhubhairavi is filed here. |
| 11 | **Kokilapriya** | S R1 G2 M1 P D2 N3 S' | C Db Eb F G A B | Neapolitan major | Elegant, bittersweet. |
| 12 | **Rupavati** | S R1 G2 M1 P D3 N3 S' | C Db Eb F G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; minor third, darker base |
| 13 | **Gayakapriya** | S R1 G3 M1 P D1 N1 S' | C Db E F G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; augmented second R1-G3 gives an old, desert sound |
| 14 | **Vakulabharanam** ★ | S R1 G3 M1 P D1 N2 S' | C Db E F G Ab Bb | Phrygian dominant (Hijaz) / close to Basant Mukhari | Ancient, desert, Middle-Eastern; dramatic. Film: period, desert and Arabic-tinged scenes. |
| 15 | **Mayamalavagowla** ★ | S R1 G3 M1 P D1 N3 S' | C Db E F G Ab B | Double harmonic (Byzantine) / Bhairav thaat | Dawn, temple, devotion; the first scale every student learns. Janyas Saveri, Bowli, Malahari, Revagupti, Gowla, Lalitha, Nadanamakriya. Film: temple and dawn scenes, ancient-kingdom openings. |
| 16 | **Chakravakam** ★ | S R1 G3 M1 P D2 N2 S' | C Db E F G A Bb | Mixolydian b2 / Ahir Bhairav | Gentle, tender devotion; dawn. Janya Malayamarutham. Film: soft devotional and mother-child melodies. |
| 17 | **Suryakantam** ★ | S R1 G3 M1 P D2 N3 S' | C Db E F G A B | - | Radiant, cheerful morning. Janyas Vasantha, Saurashtram. |
| 18 | **Hatakambari** | S R1 G3 M1 P D3 N3 S' | C Db E F G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; augmented second R1-G3 gives an old, desert sound |
| 19 | **Jhankaradhwani** | S R2 G2 M1 P D1 N1 S' | C D Eb F G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; minor third, darker base |
| 20 | **Natabhairavi** ★ | S R2 G2 M1 P D1 N2 S' | C D Eb F G Ab Bb | Natural minor (Aeolian) / Asavari thaat | Sad, serious, renunciation. Janyas Hindolam, Saramati, Jayanthasri; Carnatic Bhairavi lives here (with D2 rising). Film: sad songs and serious drama. |
| 21 | **Keeravani** ★ | S R2 G2 M1 P D1 N3 S' | C D Eb F G Ab B | Harmonic minor / Kirwani | Dramatic, cinematic, emotional; any time, best at night. Janya Kalyana Vasantham. Film: hugely used in Tamil, Telugu and Hindi film for intense love and tragedy. |
| 22 | **Kharaharapriya** ★ | S R2 G2 M1 P D2 N2 S' | C D Eb F G A Bb | Dorian / Kafi thaat | Soulful, versatile, folk warmth; karuna and shringar. Biggest janya family: Abhogi, Sriranjani, Shivaranjani, Madhyamavati, Abheri, Kapi, Reetigowla, Mukhari, Kanada, Darbar, Sriragam, Huseni, Brindavana Saranga, Shuddha Dhanyasi. Film: everywhere, folk-pop and romance. |
| 23 | **Gourimanohari** ★ | S R2 G2 M1 P D2 N3 S' | C D Eb F G A B | Melodic minor (ascending) / close to Patdeep | Bright minor, romantic, evening. Film: lilting romantic melodies. |
| 24 | **Varunapriya** | S R2 G2 M1 P D3 N3 S' | C D Eb F G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; minor third, darker base |
| 25 | **Mararanjani** | S R2 G3 M1 P D1 N1 S' | C D E F G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base |
| 26 | **Charukesi** ★ | S R2 G3 M1 P D1 N2 S' | C D E F G Ab Bb | Mixolydian b6 (Aeolian dominant) / Charukeshi | Bittersweet: major third, minor sixth; pathos inside romance. Film: very popular for emotional duets and nostalgic themes. |
| 27 | **Sarasangi** ★ | S R2 G3 M1 P D1 N3 S' | C D E F G Ab B | Harmonic major / Nat Bhairav | Majestic with a shadow (the flat sixth under a major third); morning. Film: stately, regal themes. |
| 28 | **Harikambhoji** ★ | S R2 G3 M1 P D2 N2 S' | C D E F G A Bb | Mixolydian / Khamaj thaat | Light, romantic, devotional. Janyas Kambhoji, Mohanam, Khamas, Sahana, Yadukulakambhoji, Kedaragowla, Surati, Natakurinji, Sama, Valaji. Film: romance, festive and devotional songs. |
| 29 | **Dheerasankarabharanam** ★ | S R2 G3 M1 P D2 N3 S' | C D E F G A B | Major (Ionian) / Bilawal thaat | Grand, complete, bright; any time. Janyas Hamsadhwani, Bilahari, Arabhi, Atana, Begada, Kedaram, Kadanakuthuhalam, Neelambari, Kurinji, Navaroj, Shuddha Saveri, Devagandhari, Behag. Film: hero songs, celebration, Western-fusion numbers. |
| 30 | **Naganandini** | S R2 G3 M1 P D3 N3 S' | C D E F G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base |
| 31 | **Yagapriya** | S R3 G3 M1 P D1 N1 S' | C Eb E F G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base |
| 32 | **Ragavardhini** | S R3 G3 M1 P D1 N2 S' | C Eb E F G Ab Bb | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base |
| 33 | **Gangeyabhushani** | S R3 G3 M1 P D1 N3 S' | C Eb E F G Ab B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; leading tone pulls hard to Sa |
| 34 | **Vagadheeswari** | S R3 G3 M1 P D2 N2 S' | C Eb E F G A Bb | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base |
| 35 | **Shulini** | S R3 G3 M1 P D2 N3 S' | C Eb E F G A B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; leading tone pulls hard to Sa |
| 36 | **Chalanata** ★ | S R3 G3 M1 P D3 N3 S' | C Eb E F G Bb B | - | Vigorous, martial, auspicious. Janya Nattai, the classic concert opener. Film: power and battle cues. |
| 37 | **Salagam** | S R1 G1 M2 P D1 N1 S' | C Db D F# G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes; raised Ma floats, never quite settles |
| 38 | **Jalarnavam** | S R1 G1 M2 P D1 N2 S' | C Db D F# G Ab Bb | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes; raised Ma floats, never quite settles |
| 39 | **Jhalavarali** ★ | S R1 G1 M2 P D1 N3 S' | C Db D F# G Ab B | - | Deep pathos, heavy and grave. Janya Varali. Film: tragic climaxes. |
| 40 | **Navaneetam** | S R1 G1 M2 P D2 N2 S' | C Db D F# G A Bb | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes; raised Ma floats, never quite settles |
| 41 | **Pavani** | S R1 G1 M2 P D2 N3 S' | C Db D F# G A B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes; raised Ma floats, never quite settles; leading tone pulls hard to Sa |
| 42 | **Raghupriya** | S R1 G1 M2 P D3 N3 S' | C Db D F# G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; crushed low notes; raised Ma floats, never quite settles |
| 43 | **Gavambhodi** | S R1 G2 M2 P D1 N1 S' | C Db Eb F# G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; minor third, darker base; raised Ma floats, never quite settles |
| 44 | **Bhavapriya** | S R1 G2 M2 P D1 N2 S' | C Db Eb F# G Ab Bb | - | minor third, darker base; raised Ma floats, never quite settles |
| 45 | **Shubhapantuvarali** ★ | S R1 G2 M2 P D1 N3 S' | C Db Eb F# G Ab B | Todi thaat | Grief, longing, surrender; morning. Film: deep sorrow and prayer at the edge of loss. |
| 46 | **Shadvidamargini** | S R1 G2 M2 P D2 N2 S' | C Db Eb F# G A Bb | - | minor third, darker base; raised Ma floats, never quite settles |
| 47 | **Suvarnangi** | S R1 G2 M2 P D2 N3 S' | C Db Eb F# G A B | - | minor third, darker base; raised Ma floats, never quite settles; leading tone pulls hard to Sa |
| 48 | **Divyamani** | S R1 G2 M2 P D3 N3 S' | C Db Eb F# G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; minor third, darker base; raised Ma floats, never quite settles |
| 49 | **Dhavalambari** | S R1 G3 M2 P D1 N1 S' | C Db E F# G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles; augmented second R1-G3 gives an old, desert sound |
| 50 | **Namanarayani** | S R1 G3 M2 P D1 N2 S' | C Db E F# G Ab Bb | - | major third, bright base; raised Ma floats, never quite settles; augmented second R1-G3 gives an old, desert sound |
| 51 | **Kamavardhini** ★ | S R1 G3 M2 P D1 N3 S' | C Db E F# G Ab B | Purvi thaat | Dusk, solemn devotion; also called Pantuvarali. Film: dusk temple scenes, sad devotion. |
| 52 | **Ramapriya** | S R1 G3 M2 P D2 N2 S' | C Db E F# G A Bb | - | major third, bright base; raised Ma floats, never quite settles; augmented second R1-G3 gives an old, desert sound |
| 53 | **Gamanashrama** ★ | S R1 G3 M2 P D2 N3 S' | C Db E F# G A B | Marwa thaat | Restless sunset, anxious. Janya Hamsanandi (= Sohini). Film: yearning night songs, tension. |
| 54 | **Vishwambari** | S R1 G3 M2 P D3 N3 S' | C Db E F# G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles; augmented second R1-G3 gives an old, desert sound |
| 55 | **Shamalangi** | S R2 G2 M2 P D1 N1 S' | C D Eb F# G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; minor third, darker base; raised Ma floats, never quite settles |
| 56 | **Shanmukhapriya** ★ | S R2 G2 M2 P D1 N2 S' | C D Eb F# G Ab Bb | - | Vigorous and devotional, heroic pathos; popular in devotional and film songs. |
| 57 | **Simhendramadhyamam** ★ | S R2 G2 M2 P D1 N3 S' | C D Eb F# G Ab B | Hungarian minor | Exotic, dramatic, dark grandeur. Film: villain and mystery cues. |
| 58 | **Hemavati** ★ | S R2 G2 M2 P D2 N2 S' | C D Eb F# G A Bb | Ukrainian Dorian (Romanian minor) | Plaintive, nocturnal, folk-Eastern-European tint; night. |
| 59 | **Dharmavati** ★ | S R2 G2 M2 P D2 N3 S' | C D Eb F# G A B | Lydian b3 / Madhuvanti | Sweet longing, gentle; evening. Janya Ranjani. |
| 60 | **Neetimati** | S R2 G2 M2 P D3 N3 S' | C D Eb F# G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; minor third, darker base; raised Ma floats, never quite settles |
| 61 | **Kantamani** | S R2 G3 M2 P D1 N1 S' | C D E F# G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles |
| 62 | **Rishabhapriya** | S R2 G3 M2 P D1 N2 S' | C D E F# G Ab Bb | - | Dreamy, almost whole-tone; floats. |
| 63 | **Latangi** ★ | S R2 G3 M2 P D1 N3 S' | C D E F# G Ab B | - | Lilting, emotional, flowing; used for light classical and film melodies. |
| 64 | **Vachaspati** ★ | S R2 G3 M2 P D2 N2 S' | C D E F# G A Bb | Lydian dominant (acoustic scale) / Saraswati (janya) | Bright with a twist; wonder, sci-fi; devotional. Film: modern wonder and fantasy themes. |
| 65 | **Mechakalyani** ★ | S R2 G3 M2 P D2 N3 S' | C D E F# G A B | Lydian / Kalyan thaat (Yaman) | Serene, majestic, auspicious; evening. Janyas Mohana Kalyani, Yamuna Kalyani, Hamir Kalyani, Sunadavinodini. Film: one of the most used scales for love and devotion. |
| 66 | **Chitrambari** | S R2 G3 M2 P D3 N3 S' | C D E F# G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles. Janya Amritavarshini, the 'rain' raga of legend. |
| 67 | **Sucharitra** | S R3 G3 M2 P D1 N1 S' | C Eb E F# G Ab A | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles |
| 68 | **Jyotiswarupini** | S R3 G3 M2 P D1 N2 S' | C Eb E F# G Ab Bb | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles |
| 69 | **Dhatuvardhani** | S R3 G3 M2 P D1 N3 S' | C Eb E F# G Ab B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles; leading tone pulls hard to Sa |
| 70 | **Nasikabhushani** | S R3 G3 M2 P D2 N2 S' | C Eb E F# G A Bb | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles |
| 71 | **Kosalam** | S R3 G3 M2 P D2 N3 S' | C Eb E F# G A B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles; leading tone pulls hard to Sa |
| 72 | **Rasikapriya** | S R3 G3 M2 P D3 N3 S' | C Eb E F# G Bb B | - | vivadi (two neighbouring notes crowd each other): eerie, chromatic, rarely used in songs; major third, bright base; raised Ma floats, never quite settles |

## 3. Carnatic raga cards (the main melakartas and the janyas composers really use)

Card layout: **Name** (parent mela) · up / down · Sa = C notes · then phrases, mood (rasa, time), gamaka, film use, Hindustani match. "Write it" is how a South Indian film composer uses the raga (indian-touch rule: the raga shapes the melody on any instrument).

### 3a. Main melakartas

**Mayamalavagowla** (15) · S R1 G3 M1 P D1 N3 S' / S' N3 D1 P M1 G3 R1 S · C Db E F G Ab B
- Phrases: S R1 G3 M1 P · G3 M1 P D1 N3 S' · D1 P M1 G3 R1 S · N3, S R1 S (dawn turn).
- Mood: dawn, temple, devotion, ancient kingdoms (bhakti, shanta). Gamaka: R1 and D1 shaken and leaning up into G3 and N3; G3 and N3 held.
- Film: temple at dawn, a kingdom's opening shot, devotional openings; with a heavy drum it turns ancient and warlike.
- Hindustani: Bhairav thaat (Bhairav itself adds slow andolan on r and d).
- Write it: hold D1 and R1 as long sighing notes against a Sa-Pa drone; the two augmented seconds (R1-G3, D1-N3) are the colour, so let the lead slide across them.

**Hanumatodi / Todi** (8) · S R1 G2 M1 P D1 N2 S' / S' N2 D1 P M1 G2 R1 S · C Db Eb F G Ab Bb
- Phrases: G2 (wide shake) R1 S · D1 P M1 G2 R1 S · N2 D1 M1 D1 N2 S' · M1 G2 R1 G2 M1 (circling).
- Mood: pathos, surrender, profound devotion (karuna, bhakti); morning. Gamaka: the heaviest in Carnatic: G2 and D1 are almost never plain; P is touched lightly and often skipped.
- Film: grief, a mother's prayer, a dark reveal sung slowly.
- Hindustani: same notes as Hindustani **Bhairavi** (not Carnatic Bhairavi, and not Miyan ki Todi).
- Write it: a slow lead that shakes on G2 and D1 over a low drone; short falls D1 P M1 G2 R1 S as the sigh motif.

**Natabhairavi** (20) · S R2 G2 M1 P D1 N2 S' (both ways) · C D Eb F G Ab Bb
- Phrases: P D1 N2 S' · S' N2 D1 P M1 G2 R2 S · G2 M1 P D1 P (sob on D1).
- Mood: sadness, seriousness, renunciation (karuna). Gamaka: on G2 and D1.
- Film: sad songs, dark drama; the plain minor of many Western-fusion scores.
- Hindustani: Asavari thaat (Jaunpuri and Darbari live here).
- Write it: phrase from P down to S in steps, rest on G2; use the D1-P fall like a sob.

**Keeravani** (21) · S R2 G2 M1 P D1 N3 S' (both ways) · C D Eb F G Ab B
- Phrases: G2 M1 P D1 N3 S' · S' N3 D1 P M1 G2 R2 S · D1 N3 S' R2' S' · P D1 N3 D1 P.
- Mood: drama, heartbreak, intense love, cinematic yearning; evening and night. Gamaka: slides across the D1-N3 augmented second.
- Film: one of the most used scales in Tamil, Telugu and Hindi film for passionate duets, tragedy and big emotional themes.
- Hindustani: Kirwani. Western: harmonic minor.
- Write it: build the hook on D1 N3 S' (the leap is the hook), keep harmony on a minor drone instead of Western V-i cadences (rule 15).

**Kharaharapriya** (22) · S R2 G2 M1 P D2 N2 S' (both ways) · C D Eb F G A Bb
- Phrases: R2 G2 M1 P D2 N2 D2 P · N2 D2 P M1 G2 R2 S · S R2 G2 R2 S N2, D2, (low turn).
- Mood: soulful, warm, versatile; karuna and shringar. Gamaka: G2 and N2 shaken (kampitam), R2 slides from G2.
- Film: folk-pop, romance, heartbreak; the parent of half the film janyas (Abhogi, Shivaranjani, Madhyamavati, Abheri, Kapi, Reetigowla, Sriranjani).
- Hindustani: Kafi thaat. Western: Dorian.
- Write it: the major sixth D2 over a minor third is what makes it warm, not sad: lean on D2.

**Harikambhoji** (28) · S R2 G3 M1 P D2 N2 S' (both ways) · C D E F G A Bb
- Phrases: G3 M1 P D2 N2 D2 P · S' N2 D2 P M1 G3 R2 S · P D2 S' N2 D2 P.
- Mood: light, romantic, devotional, festive (shringar, bhakti). Gamaka: on G3 and N2.
- Film: love songs, festival songs; parent of Mohanam, Kambhoji, Khamas, Sahana.
- Hindustani: Khamaj thaat. Western: Mixolydian.

**Dheerasankarabharanam / Shankarabharanam** (29) · S R2 G3 M1 P D2 N3 S' (both ways) · C D E F G A B
- Phrases: G3 M1 P D2 N3 S' · S' N3 D2 P M1 G3 R2 S · D2 N3 D2 P M1 G3 (with deep shake on N3 and G3).
- Mood: grand, complete, bright, regal (veera, adbhuta); any time. Gamaka: in classical style G3, D2, N3 are shaken, which keeps it Indian; sung plain it is just the Western major scale.
- Film: hero songs, celebration, Western-fusion and brass-band numbers.
- Hindustani: Bilawal thaat. Western: major (Ionian).
- Write it: the gamaka is the whole difference: ask for slides into G3 and N3 and a drone, or it sounds like a pop song in C major.

**Charukesi** (26) · S R2 G3 M1 P D1 N2 S' (both ways) · C D E F G Ab Bb
- Phrases: G3 M1 P D1 N2 D1 P · M1 G3 R2 S · P D1 P M1 G3 (the bitter turn) · S' N2 D1 P.
- Mood: bittersweet longing, nostalgia, love with pain (shringar + karuna); evening.
- Film: very popular for emotional duets, nostalgic and separation themes.
- Hindustani: Charukeshi (borrowed from Carnatic). Western: Mixolydian b6.
- Write it: start bright in the lower half (S R2 G3 M1), then let D1 darken the phrase; that switch is the emotion.

**Gourimanohari** (23) · S R2 G2 M1 P D2 N3 S' (both ways) · C D Eb F G A B
- Phrases: G2 M1 P D2 N3 S' · S' N3 D2 P M1 G2 R2 S.
- Mood: bright minor, romantic, evening; hopeful love. Hindustani: close to Patdeep. Western: melodic minor.

**Vakulabharanam** (14) · S R1 G3 M1 P D1 N2 S' · C Db E F G Ab Bb
- Mood: ancient, desert, Middle-Eastern drama. Western: Phrygian dominant (Hijaz). Hindustani: close to Basant Mukhari.
- Write it: low drone, the R1-G3 jump on a reed or bowed lead; perfect for desert, Arabic or period scenes.

**Chakravakam** (16) · S R1 G3 M1 P D2 N2 S' · C Db E F G A Bb
- Phrases: S R1 G3 M1 P · D2 N2 D2 P M1 G3 R1 S.
- Mood: tender devotion, gentle dawn, a mother's love. Hindustani: Ahir Bhairav.

**Sarasangi** (27) · S R2 G3 M1 P D1 N3 S' · C D E F G Ab B · stately with a shadow; Hindustani Nat Bhairav; Western harmonic major. Regal themes.

**Shubhapantuvarali** (45) · S R1 G2 M2 P D1 N3 S' · C Db Eb F# G Ab B
- Phrases: D1 N3 S' · M2 G2 R1 S · P D1 P M2 G2 (slow, long notes).
- Mood: grief, surrender, the edge of loss; morning. Hindustani: Todi thaat (Miyan ki Todi). Film: deep sorrow, prayer at a deathbed.

**Kamavardhini / Pantuvarali** (51) · S R1 G3 M2 P D1 N3 S' · C Db E F# G Ab B
- Mood: dusk, solemn devotion, pathos. Hindustani: Purvi thaat (Purvi, Puriya Dhanashri, Shree). Write it: R1 and D1 lean down, M2 pulls up to P.

**Gamanashrama** (53) · S R1 G3 M2 P D2 N3 S' · C Db E F# G A B
- Mood: restless sunset, anxiety, yearning. Hindustani: Marwa thaat. Janya: Hamsanandi (= Sohini).

**Shanmukhapriya** (56) · S R2 G2 M2 P D1 N2 S' · C D Eb F# G Ab Bb
- Phrases: G2 M2 P D1 N2 S' · S' N2 D1 P M2 G2 R2 S · P D1 N2 D1 P M2.
- Mood: vigorous, heroic devotion, power with pathos (veera, bhakti).
- Film: devotional power songs and intense action-devotion scenes.
- Write it: punchy unison stabs on P D1 N2 S' for a mass hook.

**Simhendramadhyamam** (57) · S R2 G2 M2 P D1 N3 S' · C D Eb F# G Ab B
- Mood: exotic, dark grandeur, mystery, longing. Western: Hungarian minor. Film: villain, mystery, palace intrigue.

**Hemavati** (58) · S R2 G2 M2 P D2 N2 S' · C D Eb F# G A Bb · plaintive, nocturnal; Western: Ukrainian Dorian.

**Dharmavati** (59) · S R2 G2 M2 P D2 N3 S' · C D Eb F# G A B
- Mood: sweet longing, gentle evening. Hindustani: Madhuvanti. Janya: Ranjani.

**Latangi** (63) · S R2 G3 M2 P D1 N3 S' · C D E F# G Ab B · lilting, emotional, flowing; light classical and film melodies.

**Vachaspati** (64) · S R2 G3 M2 P D2 N2 S' · C D E F# G A Bb
- Mood: bright with a twist, wonder, discovery, sci-fi, devotion. Western: Lydian dominant. Hindustani: the janya Saraswati (S R M P D n S').
- Write it: hold M2 over a Sa drone for wonder; N2 on top keeps it Indian rather than film-trailer Lydian.

**Mechakalyani / Kalyani** (65) · S R2 G3 M2 P D2 N3 S' (both ways) · C D E F# G A B
- Phrases: N3, R2 G3 M2 P · M2 G3 R2 S · P M2 D2 N3 S' · G3 M2 D2 N3 R2' S'.
- Mood: serene majesty, auspicious, devotion and love (bhakti, shringar, adbhuta); evening. Gamaka: wide on G3 and N3, M2 held.
- Film: one of the most used scales for love, devotion and grand openings.
- Hindustani: Yaman (Kalyan thaat). Western: Lydian.

**Rasikapriya** (72) · S R3 G3 M2 P D3 N3 S' · C D# E F# G A# B · vivadi; brilliant and odd; good for futuristic and fusion hooks.

**Kanakangi** (1) · S R1 G1 M1 P D1 N1 S' · C Db D F G Ab A · vivadi; the chromatic cluster sounds ancient, eerie, uneasy; horror and suspense textures.

**Jhalavarali** (39) · S R1 G1 M2 P D1 N3 S' · C Db D F# G Ab B · vivadi; parent of Varali (below): grave, heavy, tragic.

### 3b. Joy, celebration and beginnings

**Mohanam** (28) · S R2 G3 P D2 S' / S' D2 P G3 R2 S · C D E G A
- Phrases: G3 P D2 S' D2 P G3 · S' D2 P G3 R2 S · G3 R2 S D2, S · P D2 S' R2' G3'.
- Mood: joy, romance, devotion (shringar, veera); evening, but fine any time. Gamaka: light shake on G3 and D2; mostly open.
- Film: romantic duets, village festivals, devotional songs; the open pentatonic sounds universal.
- Hindustani: Bhupali (same notes; Deshkar also uses them but lives in the upper half).

**Hamsadhwani** (29) · S R2 G3 P N3 S' / S' N3 P G3 R2 S · C D E G B
- Phrases: N3, S R2 G3 P · P N3 S' R2' S' N3 P G3 R2 S · G3 P N3 P G3 R2.
- Mood: auspicious, bright, festive beginnings (adbhuta, shringar). Gamaka: light; N3 bent up into S'.
- Film: invocations, a title card, festive openings, "a new start" cues.
- Hindustani: Hansadhwani (borrowed from Carnatic).

**Bilahari** (29) · S R2 G3 P D2 S' / S' N3 D2 P M1 G3 R2 S · C D E G A up, C B A G F E D down
- Phrases: S R2 G3 P D2 S' · S' N3 D2 P M1 G3 R2 S · P D2 N2 D2 P (N2 as a passing grace in some phrases).
- Mood: bright morning joy, energy (veera, hasya). Film: cheerful songs, morning montage.

**Arabhi** (29) · S R2 M1 P D2 S' / S' N3 D2 P M1 G3 R2 S
- Mood: vigorous, triumphant, a march (veera). Film: celebration, victory.

**Atana** (29) · S R2 M1 P N3 S' / S' N3 D2 P M1 P G3 R2 S (N2 as a borrowed grace)
- Mood: heroism, vigour, fury (veera, raudra). Film: fight build-ups, hero's anger.

**Begada** (29) · S G3 R2 G3 M1 P D2 P S' / S' N3 D2 P M1 G3 R2 S
- Mood: grandeur, nobility (veera). Gamaka: rich on G3, M1 and N3. Film: royal entries.

**Kadanakuthuhalam** (29) · S R2 M1 D2 N3 G3 P S' / S' N3 D2 P M1 G3 R2 S
- Mood: playful, sparkling fun (hasya); the zigzag climb is the joke. Film: playful songs, comedy chases, kids.

**Nattai** (36) · S R3 G3 M1 P D3 N3 S' / S' N3 P M1 R3 S
- Mood: vigorous, auspicious, a power opener (veera). Film: battle and power cues, a strong overture.

**Amritavarshini** (66) · S G3 M2 P N3 S' / S' N3 P M2 G3 S · C E F# G B
- Mood: joy, rain (legend says it brings rain; a legend, not a fact). Film: first rain, relief after drought.

**Vasantha** (17) · S M1 G3 M1 D2 N3 S' / S' N3 D2 M1 G3 R1 S
- Mood: spring, freshness, tender joy. Film: spring and new-love montages.

**Shuddha Dhanyasi** (22) · S G2 M1 P N2 S' (both ways) · C Eb F G Bb · joy with warmth; Hindustani Dhani; light, folk-pop melodies.

### 3c. Love and romance

**Kapi** (22, bhashanga) · S R2 M1 P N3 S' / S' N2 D2 N2 P M1 G2 R2 S
- Phrases: P N3 S' (the borrowed N3 going up) · S' N2 D2 N2 P · M1 G2 R2 S.
- Mood: love, longing, light classical (shringar); night. Film: romantic and folk-light songs. Hindustani: close to Pilu / light Kafi.

**Khamas** (28) · S M1 G3 M1 P D2 N2 S' / S' N2 D2 P M1 G3 R2 S
- Mood: playful romance, flirtation (javali, padam). Hindustani: Khamaj.

**Sahana** (28, vakra) · S R2 G3 M1 P M1 D2 N2 S' / S' N2 S' D2 N2 D2 P M1 G3 M1 R2 G3 R2 S
- Mood: tender, melancholy romance, a love that aches (shringar + karuna). Gamaka: slow, sliding. Film: soft love themes, lullaby-like romance.

**Sriranjani** (22) · S R2 G2 M1 D2 N2 S' (both ways, no P)
- Mood: gentle love, devotion. Hindustani: close to Bageshree (Bageshree uses P lightly).

**Reetigowla** (22, vakra) · S G2 R2 G2 M1 N2 D2 M1 N2 N2 S' / S' N2 D2 M1 G2 M1 P M1 G2 R2 S
- Phrases: G2 R2 G2 M1 · N2 D2 M1 N2 N2 S' (the doubled N2 is its signature) · M1 P M1 G2 R2 S.
- Mood: tender romance, sweet ache (shringar, karuna). No Hindustani match. Film: Tamil romantic melodies. (Used for First Love v8.)

**Behag** (29, with M2 as a grace) · S G3 M1 P N3 D2 N3 S' / S' N3 D2 P M2 G3 M1 G3 R2 S
- Mood: night romance, longing (shringar). Hindustani: Bihag.

**Abheri** (22) · S G2 M1 P N2 S' / S' N2 D2 P M1 G2 R2 S
- Mood: longing, love in the afternoon light (shringar). Hindustani: Bhimpalasi. Film: romantic melodies with a sigh.

**Abhogi** (22) · S R2 G2 M1 D2 S' (both ways)
- Phrases: D2 S' R2' G2' · G2 M1 D2 M1 G2 R2 S.
- Mood: devotion and romance, calm night. Hindustani: Abhogi (Abhogi Kanada).

**Hamir Kalyani** (65) · S P M2 P D2 N3 S' / S' N3 D2 P M2 G3 P M1 R2 S
- Mood: stately love, devotion; night. Hindustani: Kedar (both Ma).

**Yamuna Kalyani** (65) · S R2 G3 P M2 P D2 S' / S' D2 P M2 P G3 R2 S
- Mood: devotion and love, river-side calm. Hindustani: close to Yaman Kalyan.

**Mohana Kalyani** (65) · S R2 G3 P D2 S' / S' N3 D2 P M2 G3 R2 S
- Mood: sweet, auspicious love. Hindustani: Shuddh Kalyan (Bhupali up, Kalyan down).

**Kalyana Vasantham** (21) · S G2 M1 D1 N3 S' / S' N3 D1 P M1 G2 R2 S · romantic longing, night.

**Valaji** (28) · S G3 P D2 N2 S' (both ways) · light and sweet; Hindustani Kalawati.

### 3d. Sadness, longing and grief

**Shivaranjani** (22) · S R2 G2 P D2 S' (both ways) · C D Eb G A
- Phrases: G2 R2 S D2, S · P D2 S' R2' G2' R2' S' · G2 (held, sliding down to R2).
- Mood: sorrow, separation, longing (karuna, viraha). Film: classic sad and separation songs in every Indian language.
- Hindustani: Shivranjani. Write it: hold G2 and slide down to R2; that one slide is the whole raga.

**Mukhari** (22, bhashanga) · S R2 M1 P N2 D2 S' / S' N2 D1 P M1 G2 R2 S
- Mood: grief, mourning (karuna). Film: death and loss scenes.

**Saramati** (20) · S R2 G2 M1 P D1 N2 S' / S' N2 D1 M1 G2 S · sorrow, quiet tears.

**Huseni** (22) · S R2 G2 M1 P N2 D2 N2 S' / S' N2 D2 P M1 G2 R2 S · pathos with love; old-world Persian tint.

**Varali** (39) · S G1 R1 G1 M2 P D1 N3 S' / S' N3 D1 P M2 G1 R1 S · grave, heavy, tragic; the crowding G1 R1 is the weight.

**Punnagavarali** (8) · N2, S R1 G2 M1 P D1 N2 / N2 D1 P M1 G2 R1 S N2, (lives below and around Sa, never reaches the upper Sa)
- Mood: the snake-charmer sound, hypnotic, sorrowful. Film: snake, magic, trance scenes.

**Dhanyasi** (8) · S G2 M1 P N2 S' / S' N2 D1 P M1 G2 R1 S · peaceful devotion, morning; a Todi colour with an open climb.

**Neelambari** (29) · S R2 G3 M1 P D2 P S' / S' N3 P M1 G3 R2 G3 S · lullaby, sleep, tender night. Film: lullabies.

### 3e. Devotion, dawn and peace

**Saveri** (15) · S R1 M1 P D1 S' / S' N3 D1 P M1 G3 R1 S · devotion with pathos, morning.
**Bowli** (15) · S R1 G3 P D1 S' / S' N3 D1 P G3 R1 S · dawn, the first light.
**Revagupti** (15) · S R1 G3 P D1 S' (both ways) · dawn; Hindustani Vibhas.
**Malahari** (15) · S R1 M1 P D1 S' / S' D1 P M1 G3 R1 S · simple morning devotion (the first songs students learn).
**Bhupalam** (8) · S R1 G2 P D1 S' (both ways) · dawn prayer; Hindustani Bhupal Todi.
**Malayamarutham** (16) · S R1 G3 P D2 N2 S' (both ways) · fresh dawn, hope.
**Revati** (2) · S R1 M1 P N2 S' (both ways) · austere, Vedic chant; Hindustani Bairagi. Film: sages, mantras, ancient ritual.
**Sama** (28) · S R2 M1 P D2 S' / S' D2 P M1 G3 R2 S · peace, calm acceptance.
**Ranjani** (59) · S R2 G2 M2 D2 S' / S' N3 D2 M2 G2 S R2 G2 S · devotion with mystery.
**Madhyamavati** (22) · S R2 M1 P N2 S' (both ways) · C D F G Bb
- Mood: auspicious, a blessing, closing; concerts end with it (mangalam). Hindustani: close to Madhmad Sarang (Megh shares the notes with a different feel). Film: festive-devotional endings, a happy last shot.
**Surati** (28) · S R2 M1 P N2 S' / S' N2 D2 P M1 G3 P M1 R2 S · auspicious closing.

### 3f. Grandeur, power and night

**Kambhoji** (28) · S R2 G3 M1 P D2 S' / S' N2 D2 P M1 G3 R2 S N3, P, D2, S
- Phrases: S N3, P, D2, S (the borrowed N3 below Sa is the signature) · D2 S' R2' G3' R2' S' · P D2 S' N2 D2 P.
- Mood: majesty, devotion, heroism (veera, bhakti). Film: devotional-heroic songs. Hindustani: no exact match (Khamaj family colour).

**Kanada** (22) · S R2 G2 M1 D2 N2 S' / S' N2 P M1 G2 M1 R2 S · majestic, vigorous; shares the Hindustani Kanada turn (g m R S).
**Darbar** (22) · S R2 M1 P D2 N2 S' / S' N2 D2 P M1 R2 G2 G2 R2 S · regal, heroic; the doubled G2 is its stamp.
**Sriragam** (22) · S R2 M1 P N2 S' / S' N2 P D2 N2 P M1 R2 G2 R2 S · grand and auspicious. Trap: not the same raga as Hindustani Shree.
**Hindolam** (20) · S G2 M1 D1 N2 S' (both ways) · C Eb F Ab Bb
- Phrases: G2 M1 D1 N2 D1 M1 · N2, S G2 M1 · D1 N2 S' G2' S'.
- Mood: majestic calm, meditation, mystery, night (shanta, adbhuta). Hindustani: Malkauns. Film: mystic, devotional, palace at night.
**Bhairavi** (Carnatic, 20) · S R2 G2 M1 P D2 N2 S' / S' N2 D1 P M1 G2 R2 S (D2 going up, D1 coming down)
- Mood: grand pathos, depth (karuna, bhakti). Trap: Carnatic Bhairavi is not Hindustani Bhairavi (that one = Carnatic Todi's scale).
**Kurinji** (29) · S N3, S R2 G3 M1 P D2 / D2 P M1 G3 R2 S N3, S (low range, never far above Sa) · folk lilt, lullaby, children's songs.

### 3g. Folk and film favourites

**Sindhubhairavi** (10; parent disputed, bhashanga) · base S R2 G2 M1 P D1 N2 S', but any other note may enter as colour
- Mood: folk, emotional, devotional, nostalgic (karuna, shringar); light classical and concert endings.
- Film: one of the most used ragas in South Indian film melody: village songs, mother songs, emotional duets.
- Hindustani: Sindhu Bhairavi / Bhairavi in light music (the same freedom with notes).
**Anandabhairavi** (filed under 20; sounds like 22) · S G2 R2 G2 M1 P D2 P S' / S' N2 D2 P M1 G2 R2 S (D1 as a borrowed grace)
- Mood: joy with tenderness, a mother's love, lullaby, village warmth. Film: folk tunes and mother songs.
**Desh** (Carnatic, 28) · S R2 M1 P N3 S' / S' N2 D2 P M1 G3 R2 S · patriotic, monsoon warmth; Hindustani Desh.
**Dwijavanti** (28) · Carnatic form of Jaijaiwanti: grand, devotional, both G3 and G2 in set phrases.
**Navaroj** (29) · P D2 N3 S R2 G3 M1 / M1 G3 R2 S N3 D2 P (lives from low P to M1) · folk, lilting.


## 4. Hindustani: the 10 thaats and their major ragas

### 4a. The 10 thaats (Bhatkhande's parent scales)

| Thaat | Notes | Sa = C | Carnatic mela | Western | Feel |
|---|---|---|---|---|---|
| Bilawal | S R G m P D N | C D E F G A B | 29 Shankarabharanam | Major | bright, plain, morning |
| Kalyan | S R G M P D N | C D E F# G A B | 65 Kalyani | Lydian | serene, evening |
| Khamaj | S R G m P D n | C D E F G A Bb | 28 Harikambhoji | Mixolydian | light, romantic |
| Kafi | S R g m P D n | C D Eb F G A Bb | 22 Kharaharapriya | Dorian | folk, spring, longing |
| Asavari | S R g m P d n | C D Eb F G Ab Bb | 20 Natabhairavi | Natural minor | renunciation, gravity |
| Bhairavi | S r g m P d n | C Db Eb F G Ab Bb | 8 Hanumatodi | Phrygian | tender pathos, devotion |
| Bhairav | S r G m P d N | C Db E F G Ab B | 15 Mayamalavagowla | Double harmonic | dawn, grave devotion |
| Marwa | S r G M P D N | C Db E F# G A B | 53 Gamanashrama | - | sunset restlessness |
| Purvi | S r G M P d N | C Db E F# G Ab B | 51 Kamavardhini | - | dusk, solemn |
| Todi | S r g M P d N | C Db Eb F# G Ab B | 45 Shubhapantuvarali | - | morning pathos |

**Time cycle (samay chakra), the rule of thumb:** ragas with r and d (Bhairav, Purvi, Marwa families) belong to the twilights, dawn and dusk; ragas with R, G and D natural (Bilawal, Kalyan, Khamaj) to the day after sunrise and the evening; ragas with g and n (Kafi, Asavari, Bhairavi, Kanada) to late morning, afternoon and midnight. Tivra M rises in the evening (Yaman, Marwa, Puriya); shuddha m in the morning (Bhairav, Bilawal). Eight prahars of three hours each: 1st day prahar from about 6 am, 1st night prahar from about 6 pm.

Card layout: **Raga** (thaat) · aroh / avroh · pakad (catch phrase) · vadi/samvadi when settled · time · rasa · film use · Carnatic match.

### 4b. Bilawal thaat
- **Alhaiya Bilawal** · S R G P D N S' / S' N D n D P, m G m R S · pakad: G R, G P, D n D P · vadi D, samvadi G · late morning · cheerful, plain joy. Carnatic: Shankarabharanam colour.
- **Durga** · S R m P D S' (both ways) · pakad: m P D, m R, D, S · night · heroic joy, a goddess's strength (veera). Film: folk-bright songs. Carnatic: Shuddha Saveri.
- **Deshkar** · S R G P D S' (both ways), upper half stressed (P D S' D P G P) · morning · bright; same notes as Bhupali, different weight. Trap: Bhupali rests on G and lower notes, Deshkar on D and P.
- **Bihag** · S G m P N S' / S' N D P, M G m G R S (M only as a grace in P M G m G) · pakad: N S G m P, G m G R S · vadi G, samvadi N · 2nd prahar of night · romance, longing (shringar). Film: night romance. Carnatic: Behag.
- **Shankara** · S G P N D S' / S' N P G P S · late night · heroic fury, power (veera, raudra). Film: power and anger.
- **Pahadi** · S R G P D S' with the lower octave stressed (D, P, S) and light borrowed notes · any time, light music · hill-folk romance, nostalgia. Film: one of the most loved scales for romantic and nostalgic hill songs.
- **Hansadhwani** · S R G P N S' (both ways) · evening · auspicious joy. Carnatic: Hamsadhwani.

### 4c. Kalyan thaat
- **Yaman** · N, R G M D N S' / S' N D P M G R S · pakad: N, R G R, P R, N, R S · vadi G, samvadi N · 1st prahar of night · serene devotion, love, peace (shanta, shringar). Film: among the most used ragas in Hindi film for love and devotion. Carnatic: Kalyani.
- **Yaman Kalyan** · Yaman plus shuddha m in the descent (G m G R S) · evening · the same, softer. Carnatic: close to Yamuna Kalyani.
- **Bhupali** · S R G P D S' / S' D P G R S · pakad: G R S D, S R G, P G, D P G R S · vadi G, samvadi D · 1st prahar of night · peace, devotion, open calm (shanta). Film: calm devotion and love. Carnatic: Mohanam.
- **Shuddh Kalyan** · S R G P D S' / S' N D P M G R S · early night · stately, devotional. Carnatic: Mohana Kalyani.
- **Kedar** · S m, m P, D P, N D S' / S' N D P, M P D P, m G m R S · pakad: S m, m P, D P M, P D P m, G m R S · vadi m, samvadi S · 1st prahar of night · devotion, romance, stately (bhakti, shringar). Carnatic: Hamir Kalyani.
- **Hameer** · S R S, G m D, N D S' / S' N D P, M P D P, G m R S · vadi D, samvadi G · 1st prahar of night · heroic grace (veera, shringar).
- **Kamod** · S m R P, M P D P, N D S' / S' N D P, M P D P, G m P G m R S · night · playful romance.
- **Chhayanat** · S R G m P, N D S' / S' N D P, M P D P, G m R S · night · romantic, playful.
- **Maru Bihag** · S G M P N S' / S' N D P M G m G R S · night · yearning, passionate (shringar). Film: longing songs.

### 4d. Khamaj thaat
- **Khamaj** · S G m P D N S' / S' n D P m G R S · pakad: n D, m P D, m G · vadi G, samvadi N · 2nd prahar of night · playful romance, flirtation (shringar). Film: light romantic and thumri-like songs. Carnatic: Khamas.
- **Desh** · S R m P N S' / S' n D P, m G R, G, N, S · pakad: R m P N S', n D P, m G R G, N, S · vadi R, samvadi P · 2nd prahar of night; monsoon · patriotic pride, monsoon romance (veera, shringar). Film: patriotic songs and rain romance. Carnatic: Desh.
- **Tilak Kamod** · S R G S, R m P N S' / S' P D m G, S R G S N, · night · light, tender romance.
- **Jaijaiwanti** · S R G m P N S' / S' n D P D m R g R S (both g and G) · 2nd prahar of night · grand pathos, devotion (karuna, bhakti). Film: grand emotional songs. Carnatic: Dwijavanti.
- **Kalawati** · S G P D n S' (both ways) · night · sweet, light love. Carnatic: Valaji.
- **Rageshree** · S G m D n S' / S' n D m G R S · night · tender romance, quiet joy.
- **Jhinjhoti** · S R m P D S' / S' n D P m G R S · night · light classical, homesick tenderness. Carnatic: close to Kambhoji.
- **Tilang** · S G m P N S' / S' n P m G S · night · light, cheerful romance.

### 4e. Kafi thaat
- **Kafi** · S R g m P D n S' (both ways) · pakad: S S R R g g m m P · vadi P, samvadi S · midnight; spring and Holi · folk romance, playful longing (shringar). Film: folk and Holi songs. Carnatic: Kharaharapriya.
- **Bageshree** · n, S g m D n S' / S' n D m g R S (P light, mostly in D m P D g m) · pakad: S n, D, n, S m, m g R S · vadi m, samvadi S · midnight · waiting for the beloved, viraha (shringar, karuna). Film: night love songs. Carnatic: close to Sriranjani.
- **Bhimpalasi** · n, S g m P n S' / S' n D P m g R S · pakad: n, S m, m g P m, g m g R S · vadi m, samvadi S · afternoon · longing, love's ache (shringar). Film: romantic longing songs. Carnatic: Abheri.
- **Brindavani Sarang** · n, S R m P N S' / S' n P m R S · noon · sunny, pastoral, cheerful heat. Carnatic: Brindavana Saranga.
- **Madhmad Sarang** · S R m P n S' (both ways) · noon · bright, blessing. Carnatic: close to Madhyamavati.
- **Miyan ki Malhar** · S R P, g m R S, m P n D N S' / S' n P, m P g m R S (both n and N; the g m R S turn) · monsoon, night · rain, longing, majesty. Film: rain songs.
- **Megh** · S R m P n S' / S' n P m R S (a touch of g in R g R) · monsoon · thunderous clouds, grave majesty.
- **Bahar** · S m P g m D n S' / S' n P m P g m R S · spring · joyful freshness.
- **Pilu** · free light raga mixing both g/G, d/D, n/N around S g R g m P N S' · any time · playful, folk, wistful. Film: folk and light romance. Carnatic: close to Kapi.
- **Patdeep** · n, S g m P N S' / S' N D P m g R S · afternoon · romantic yearning. Carnatic: close to Gourimanohari.
- **Shivranjani** · S R g P D S' (both ways) · night · sorrow, separation. Carnatic: Shivaranjani.
- **Dhani** · S g m P n S' (both ways) · any time · light, folk joy. Carnatic: Shuddha Dhanyasi.
- **Abhogi Kanada** · S R g m D S' (both ways) · night · devotion, calm. Carnatic: Abhogi.

### 4f. Asavari thaat
- **Asavari** · S R m P d S' / S' n d P m g R S · vadi d, samvadi G (g) · late morning · renunciation, pathos (karuna). Carnatic: Natabhairavi colour.
- **Jaunpuri** · S R m P d n S' / S' n d P m g R S · vadi d, samvadi g · late morning · pathos with dignity.
- **Darbari Kanada** · S R g, m P, d n S' / S' d, n P, m P, g m R S (slow andolan, a wide slow sway, on g and d) · pakad: g m R S, d, n, P, · vadi R, samvadi P · midnight · regal gravity, deep sorrow, majesty (karuna, veera). Film: grave, majestic songs and dark royal themes. Carnatic: Kanada family colour.
- **Adana** · S R m P d n S' (stress on the upper octave, fast) · night · vigorous, fiery (veera).
- **Kaunsi Kanada** · Malkauns with the Kanada turn (g m R S) · midnight · grave, mysterious.

### 4g. Bhairavi thaat
- **Bhairavi** · S r g m P d n S' (both ways); in light music all 12 notes may enter · vadi m, samvadi S · morning, and the traditional last raga of a concert · tender pathos, devotion, farewell (karuna, bhakti). Film: among the most used ragas in Hindi film, from devotional to heartbreak. Carnatic scale: Hanumatodi (Carnatic Bhairavi is different).
- **Malkauns** · S g m d n S' (both ways) · pakad: m g, m d n d m, g m g S · vadi m, samvadi S · midnight · meditation, mystery, grave heroism (shanta, veera). Film: mystic, devotional and dark-heroic. Carnatic: Hindolam.
- **Bilaskhani Todi** · S r g P d S' / S' r' n d m g r S · morning · grief, a son's mourning (legend). Carnatic: Bhupalam colour.
- **Chandrakauns** · S g m d N S' (both ways) · midnight · mysterious, modern-sounding (N against g). Good for night sci-fi.
- **Komal Rishabh Asavari** · S r m P d S' / S' n d P m g r S · morning · pathos.

### 4h. Bhairav thaat
- **Bhairav** · S r G m P d N S' / S' N d P m G r S · pakad: G m d, d P, G m r, r S (slow andolan on r and d) · vadi d, samvadi r · dawn · grave devotion, awe (bhakti, shanta). Carnatic: Mayamalavagowla.
- **Ahir Bhairav** · S r G m P D n S' / S' n D P m G r S · dawn · gentle devotion, folk tenderness. Film: soft devotional and morning songs. Carnatic: Chakravakam.
- **Nat Bhairav** · S R G m P d N S' (both ways) · morning · stately with a shadow. Carnatic: Sarasangi.
- **Ramkali** · Bhairav plus M and n in set phrases (P M P d n d P) · morning · devotion with drama.
- **Jogiya** · S r m P d S' / S' N d P d m G r S · morning · renunciation, yearning (karuna). Film: sad devotional.
- **Kalingada** · S r G m P d N S' with lighter treatment · late night to dawn · light devotion.
- **Bairagi** · S r m P n S' (both ways) · dawn · detachment, austerity. Carnatic: Revati.
- **Vibhas** · S r G P d S' (both ways) · dawn · fresh, devotional. Carnatic: Revagupti.
- **Basant Mukhari** · S r G m P d n S' · morning · ancient, Middle-Eastern. Carnatic: Vakulabharanam.

### 4i. Marwa thaat (P weak or left out)
- **Marwa** · S r G M D N D S' / S' N D M G r S · vadi r, samvadi D · sunset · restless, anxious longing as day dies (bhayanaka, karuna). Film: tension at dusk.
- **Puriya** · N, r G M D N S' / S' N D M G r S (stress on G and N, lower octave) · night · sombre, devotional.
- **Sohini** · S G M D N S' / S' N D G M D G r S (upper octave stressed) · vadi D, samvadi G · last prahar of night · piercing longing, sweet ache. Carnatic: Hamsanandi.
- **Lalit** · N, r G m M m G, m d S' / r' N d M d m G r S (both m, no P) · vadi m, samvadi S · dawn · restless dawn twilight, a sleepless night ending.
- **Bhatiyar** · dawn · tender, devotional dawn.
- **Pancham** · late night · rare, searching.

### 4j. Purvi thaat
- **Purvi** · S r G M P d N S' / S' N d P M G r S (both m in descent) · vadi G, samvadi N · dusk · solemn, devotional twilight.
- **Puriya Dhanashri** · N, r G M P d N S' / S' N d P M G r S · vadi P, samvadi r · sunset · yearning, prayerful pathos. Film: dusk devotion.
- **Shree** · S r M P N S' / S' N d P M G r S · vadi r, samvadi P · sunset · solemn, grave majesty. Not Carnatic Sriragam.
- **Basant** · S G M d S' / S' N d P M G M G r S · spring (also dusk) · joy of spring with depth.
- **Paraj** · night · bright, ornate. **Gauri** · dusk · devotion.

### 4k. Todi thaat
- **Miyan ki Todi** · S r g M d N S' (P light) / S' N d P M g r S · vadi d, samvadi g · late morning · pathos, tender sorrow (karuna). Carnatic: Shubhapantuvarali.
- **Gurjari Todi** · Todi with P left out · morning · softer pathos.
- **Multani** · n, S g M P N S' (r and d left out going up) / S' N d P M g r S · vadi P, samvadi S · late afternoon · intense, golden-hour longing.
- **Madhuvanti** · n, S g M P N S' / S' N D P M g R S · late afternoon · sweet longing. Carnatic: Dharmavati.

### 4l. Outside the ten thaats
- **Kirwani** · S R g m P d N S' (both ways) · night · drama, passionate love. Carnatic: Keeravani.
- **Charukeshi** · S R G m P d n S' (both ways) · any time · bittersweet. Carnatic: Charukesi.
- **Jog** · S G m P n S' / S' n P m G m g S (both g and G) · night · bluesy, wistful.
- **Madhukauns** · S g M P n S' · night · modern, mysterious.
- **Hemant** · early winter evening · warm, wistful. **Janasammohini** · S R G P D n S' · night · charming, light.
- **Seasons:** spring = Basant, Bahar, Hindol; monsoon = Megh, Miyan ki Malhar, Gaud Malhar, Sur Malhar, Desh; early winter = Hemant.

## 5. Carnatic-Hindustani matches (and the traps)

| Carnatic | Hindustani | Note |
|---|---|---|
| Shankarabharanam (29) | Bilawal | same scale |
| Kalyani (65) | Yaman | same scale; Yaman starts low (N, R G) |
| Harikambhoji (28) | Khamaj thaat | same scale |
| Kharaharapriya (22) | Kafi | same scale |
| Natabhairavi (20) | Asavari thaat / Jaunpuri | same scale |
| Hanumatodi (8) | **Bhairavi** | same scale: the big naming trap |
| Mayamalavagowla (15) | Bhairav | same scale |
| Shubhapantuvarali (45) | Miyan ki Todi | same scale: the second trap (Carnatic "Todi" is not Hindustani Todi) |
| Kamavardhini (51) | Purvi thaat | same scale |
| Gamanashrama (53) | Marwa thaat | same scale |
| Keeravani (21) | Kirwani | same |
| Charukesi (26) | Charukeshi | same |
| Chakravakam (16) | Ahir Bhairav | same |
| Sarasangi (27) | Nat Bhairav | same |
| Dharmavati (59) | Madhuvanti | same notes |
| Vakulabharanam (14) | Basant Mukhari | close |
| Mohanam | Bhupali (and Deshkar) | same notes, different weight |
| Hamsadhwani | Hansadhwani | same |
| Hindolam | Malkauns | same notes |
| Shivaranjani | Shivranjani | same |
| Abhogi | Abhogi Kanada | same |
| Abheri | Bhimpalasi | close |
| Madhyamavati | Madhmad Sarang | close |
| Shuddha Dhanyasi | Dhani | same notes |
| Sriranjani | Bageshree | close |
| Hamsanandi | Sohini | same notes |
| Revagupti | Vibhas | same notes |
| Revati | Bairagi | same notes |
| Bhupalam | Bhupal Todi | same notes |
| Mohana Kalyani | Shuddh Kalyan | same idea |
| Hamir Kalyani | Kedar | close |
| Yamuna Kalyani | Yaman Kalyan | close |
| Valaji | Kalawati | same notes |
| Kapi | Pilu (light Kafi) | close in feel |
| Behag | Bihag | same raga, two styles |
| Desh | Desh | same |
| Dwijavanti | Jaijaiwanti | same |
| Sindhubhairavi | Sindhu Bhairavi | close |
| Vachaspati | (Saraswati is its janya) | no thaat |

**Traps:** Carnatic Bhairavi is not Hindustani Bhairavi; Carnatic Todi is not Hindustani Todi; Carnatic Sriragam is not Hindustani Shree; Carnatic Hindolam is not Hindustani Hindol (Hindol is a Kalyan-thaat spring raga). Same notes do not make the same raga: the phrases, resting notes and ornaments decide (Bhupali vs Deshkar, Marwa vs Puriya vs Sohini).


## 6. Mood to raga: what to use for each scene

Pick the first choice unless the last track used it (vary ragas from track to track). "Colour notes" are the notes that carry the feeling: build the hook on them. Grooves are South Indian film grooves (music-scoring.md rule 15), with tempos as a starting point.

| Scene / mood | First choice (Carnatic / Hindustani) | Also good | Colour notes (Sa = C) | Groove and tempo |
|---|---|---|---|---|
| Hero entry, mass | Shanmukhapriya; Natabhairavi / Darbari for a dark hero | Nattai, Atana, Simhendramadhyamam | G Ab Bb C (P D1 N2 S'), F# | half-time mass bounce 85-117 BPM, stop-and-slam |
| Stylish villain (swagger) | Simhendramadhyamam / Kirwani | Vakulabharanam, Keeravani | F#-G-Ab, Ab-B | slick half-time groove 95-110, whistle hook, snaps |
| Menace, dark power | Varali, Todi colour / Darbari, Marwa | Kanakangi, Jhalavarali | Db, Ab, crowded Db-D | slow 60-80, heavy pulses |
| Fear, horror | Kanakangi, Varali / Marwa, Sohini | Rasikapriya, Punnagavarali | clustered Db D, F# | free time or 60-70, sparse hits |
| First love, innocent | Mohanam, Reetigowla / Bhupali, Pahadi | Hamsadhwani, Kapi | E, A (G3, D2) | swaying 6/8 (tisram) 70-90 |
| Romance duet, passion | Keeravani, Charukesi / Kirwani, Yaman | Kalyani, Sahana, Khamas | Ab-B, F# | 6/8 or 4/4 mid-tempo 80-100 |
| Longing, separation | Shivaranjani / Bageshree, Bhimpalasi | Abheri, Sriranjani, Maru Bihag | Eb sliding to D | slow 60-75, rubato opening |
| Grief, death | Mukhari, Shubhapantuvarali / Todi, Jogiya | Saramati, Todi (Carnatic) | Db, Ab, F# | very slow 50-65, long notes |
| Devotion, temple | Mayamalavagowla, Saveri / Bhairav, Ahir Bhairav | Kambhoji, Revati, Hindolam | Db, Ab, B | Adi tala feel 70-90, temple drums |
| Dawn, hope, a new start | Malayamarutham, Bowli / Lalit, Ahir Bhairav, Bhatiyar | Bhupalam, Hamsadhwani | Db, E, A | slow build 70-90 |
| Victory, pride | Mohanam, Arabhi / Durga, Desh | Atana, Begada, Nattai | E, A (Mohanam); the D-F leap in Arabhi | march-like 100-120, crowd chants |
| Patriotic, national pride | Desh / Desh, Jaijaiwanti | Kambhoji, Mohanam | B up, Bb down | 4/4 anthem 90-110 |
| Wonder, discovery | Kalyani, Vachaspati / Yaman, Maru Bihag | Hamsadhwani, Amritavarshini | F# | flowing 80-100 |
| Tech, future, sci-fi | Vachaspati, Rasikapriya / Chandrakauns, Madhukauns | Keeravani, Dharmavati | F# + Bb, B against Eb | 100-128 electronic pulse |
| Mystery, night | Hindolam, Abhogi / Malkauns, Darbari | Ranjani, Chandrakauns | Eb, Ab, Bb (no R, no P) | slow 60-80 |
| Royal, kingdom, epic | Kambhoji, Begada / Darbari, Shree | Sarasangi, Mayamalavagowla | B below Sa, Ab | 70-90 grand, big drums |
| Comedy, play, kids | Kadanakuthuhalam / Pilu, Khamaj | Kurinji, Bilahari | zigzag climbs | bouncy 110-130 |
| Dance, kuthu, festival | Harikambhoji, Natabhairavi / Kafi, Pilu | Sindhubhairavi, Mohanam | Bb (plus Eb in Natabhairavi) | dappankuthu off-beat 95-105 or teen-maar |
| Wedding, celebration | Kalyani, Mohanam / Yaman, Kafi | Hamsadhwani, Madhyamavati | F#, A | nadaswaram-thavil feel 100-120 |
| Rain, monsoon | Amritavarshini / Megh, Miyan ki Malhar | Desh | F# (Amritavarshini), Bb with B | rolling 6/8 80-95 |
| Mother, lullaby, home | Neelambari, Anandabhairavi / Pilu, Pahadi | Kurinji, Sindhubhairavi | low range, gentle D2 | slow sway 60-70 |
| Nostalgia, village, past | Sindhubhairavi, Charukesi / Pahadi, Bhairavi | Anandabhairavi, Kapi | Ab against E | 6/8 folk sway 70-90 |
| Chase, action | Shanmukhapriya, Keeravani / Kirwani, Adana | Simhendramadhyamam, Natabhairavi | Ab B C | heartbeat spine 120-150, speeding up |
| Calm, meditation | Hindolam, Revati / Malkauns, Bhupali | Sama, Abhogi | open pentatonic | drone, free time or 50-60 |
| Ancient, desert, Arabian | Vakulabharanam / Basant Mukhari, Bhairav | Mayamalavagowla | Db-E augmented second | slow 70-90, frame drums |
| Sweet ache, bittersweet | Charukesi / Charukeshi, Jaijaiwanti | Sahana, Kalyana Vasantham | Ab under E | 70-85 |
| Ending, blessing | Madhyamavati, Surati / Madhmad Sarang, Bhairavi | Sriragam | Bb, D, F | warm ending, slows |

**Mixing ragas inside one track.** A film cue may move between two related ragas at a story turn (rule 17: the music changes because the scene changes), for example Keeravani in the tension, then Kalyani at the reveal (minor to the raised-fourth major), or Shivaranjani for the loss, then Mohanam when hope returns (keep Sa; the change of colour is the turn). One raga per section; never a medley.

## 7. Writing a raga into an ElevenLabs Music prompt

The model hears words, not raga grammar. It follows a named Western mode or key well, and concrete notes reasonably; it follows a raga name alone loosely. So every prompt says the raga **four ways**:

1. **The name and its Western cousin:** "raga Kalyani (a Lydian scale)". The name helps a little and costs nothing; raga names are music theory, not titles, so they pass the copyright filter. Never add a song, film, composer or singer name.
2. **The notes in the track's key:** "in D: D E F# G# A B C#". Choose Sa to suit the voice or lead (D, E or C# are good for most of our leads) and move every note from the Sa = C column.
3. **The colour notes and how the lead moves:** "the melody leans on the raised fourth G# and resolves down to F#, rising phrases climb C# D E F# A, falling phrases come down A G# F# E D". Use the card's signature phrases written as notes.
4. **The ornaments:** "sung-style phrasing with gamakam: slides into notes, a wide shake on F# and C#, grace notes before long notes, the lead bends like a voice". Name which notes shake (from the card) and which stay plain.

Then put the raga inside our house rules (music-scoring.md section 9), all of them, every time:
- **Indian writing, any instruments (rule 15, indian-touch):** modal harmony over a Sa-Pa drone or pedal bass, few chord changes, the melody carries the emotion; no Western trailer chord loops or big V-I cadences. Grooves from the table above.
- **Broken Heritage and the sonic logo (rules 1-3, hopeverse-sound-identity):** the processed Carnatic layer (chopped veena partner to the synth lead, pitched-down mridangam as the bass hit, reversed nadaswaram as a riser) is a separate electronic layer; the 3-note Hopeverse call (root, minor third, fifth, bent up) opens and closes the track. The call is a logo, so play it exactly even in a raga with a major third (Mohanam, Kalyani): it is stated alone in the first 5 seconds and at the very end, where it reads as a bluesy signature, and the raga melody starts after it.
- **Natural instruments (rule 16, natural-instrument-sound):** any real instrument named as itself (flute, veena, violin, nadaswaram, tabla, thavil) is "played by a real musician, close and natural, dry, no heavy echo or delay, not chopped". Gamakam is played on it naturally; the glitch work stays on the electronic layer.
- **Balance, mystery start, hooks (rules 11-14):** one or two sounds first (a lone flute phrase in the raga over a drone), one layer at a time, a raga-built earworm riff on the colour notes, a hook at every section change, a composed surprise.

**Plan mode (composition plan):** put the raga sentence (points 1-4) into the global positive styles once, then in each section's styles say what the raga does there ("the lead rests on Ab, the sob note", "the hook climbs to the upper Sa"). Keep negative styles: "Western pop chord progression, plain major-scale melody, heavy echo on the flute, generic EDM drop".

### 7a. Example prompts (prompt mode; adapt, never copy whole)

**Wonder, Kalyani in D (a discovery scene, 90 s):**
"Cinematic South Indian film score in raga Kalyani, a Lydian scale, in D: D E F# G# A B C#. The melody leans on the raised fourth G# and comes down G# F# E D; rising phrases start from the low C# and climb C# E F# G# A. Sung-style phrasing with gamakam: slides into notes, a wide shake on F# and C#, grace notes before long notes. Opens with a lone bamboo flute, played by a real musician, close and dry, no echo, stating a rising 3-note call D F A with the last note bent up, over a soft low drone on D and A. At 6 s a chopped, glitching veena answers in the electronic layer; at 12 s a deep pitched-down mridangam hit and a slow half-time groove at 92 BPM; strings join with a counter-melody in the same notes. Modal harmony on a D pedal, no Western chord loops. The hook, a 5-note riff E F# G# A F#, returns bigger every 10 s; one beat of silence before the final hook slams in a whole step higher; ends on the lone flute playing D F A. Instrumental only, no vocals."

**Separation, Shivaranjani in C# (a goodbye at a station, 75 s):**
"Slow South Indian film melody in raga Shivaranjani, a five-note minor scale, in C#: C# D# E G# A#. The heart of the tune is a long held E that slides down to D# like a sigh; phrases fall G# E D# C# and climb A# C# D# E. Natural violin, played by a real musician, close and dry, no heavy echo, with gamakam bends; a soft tabla in a slow 6/8 sway at 66 BPM enters at 10 s. Opens with only a low drone and a reversed nadaswaram breath in the electronic layer, then the 3-note call C# E G# with the last note bent up. Modal: everything sits on a C# pedal, no chord changes. The violin and a bamboo flute trade the sigh phrase, answering each other; at the turn the drums stop for one bar and the flute plays alone. Ends on the call, unresolved. Instrumental only, no vocals."

**Hero mass, Shanmukhapriya in E (an entry, 80 s):**
"Modern Tamil mass hero BGM in raga Shanmukhapriya, in E: E F# G A# B C D. The hook hammers B C D E in tight unison stabs, then falls E D C B A# G F# E with gamakam bends on G and C. Opens with one deep bent synth note and a cinematic low boom, the 3-note call E G B bent up; a chopped veena stutters under it. At 8 s a real thavil, natural and dry, starts the half-time mass bounce at 104 BPM; a crowd shouts 'HEY' on the hook accents. Balanced: the nadaswaram, played naturally with no echo, and the synth lead trade the hook, faster each time. One beat of total silence, then the hook slams back a whole step higher with full band. Korvai-style ending, three rising hits, then the call. Instrumental only, no spoken words."

### 7b. When a take misses the raga
- Check it, don't guess: run tools/raga_check.py (section 8) on the take. If the out-of-raga share is high, the take went Western.
- Fixes, in order: name the notes again in the section styles; add the Western mode name; make the drone explicit ("constant drone on D and A"); move the hook onto the colour notes; add "no major-scale melody" (or the matching Western scale) to the negatives. Pentatonic ragas (Mohanam, Hindolam, Shivaranjani) come out most reliably; vivadi melas are the hardest, keep them for short textures.

## 8. Checking a take (tools/raga_check.py)

Agents can't listen, so measure. `python tools/raga_check.py take.mp3 --sa D --raga Kalyani` (or `--notes "S R2 G3 M2 P D2 N3"` for any raga) folds the take's tonal (harmonic) part into 12 pitch classes relative to Sa and reports: how much of the tonal energy sits on the raga's notes, the strongest notes, and any strong note the raga does not allow. Always pass `--sa` with the key the prompt asked for: without it the tool guesses, and a guess can land on a sister mode (Kalyani on D and Bilawal on A use the same seven notes). Sa itself is left out of the score so a loud drone can't hide a wrong melody. Needs `pip install librosa`. Tested 30 Oct: a clean Kalyani line scores 92% as Kalyani, 78% as Bilawal (one note off) and 22% as Bhairavi; First Love v8 (the Reetigowla take) scored 83%. Above about 80% in-raga is a pass for a fusion track (drums, synth noise and a borrowed grace note make 100% impossible); under 65% means the melody went Western or chromatic. The check sees notes, not phrases: Bhupali and Deshkar, or Marwa and Puriya, score the same, so phrases still need the prompt and Jithesh's ear.
