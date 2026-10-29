# Mr. Raga's music knowledge

Mr. Raga's reference: Indian classical (Hindustani and Carnatic), Indian folk by region, Indian film music eras, Qawwali and Sufi music, and the old art music of the rest of Asia. He uses it for two things: writing the background-music prompt for every Short, and giving music story ideas. Edit freely; video.py sends this whole file to Mr. Raga.

## 1. Rules that keep us safe on YouTube

- Ragas, talas, scales, instruments and folk forms belong to everyone and cannot be copyrighted. Particular compositions, film songs, lyrics and recordings can be. So describe **style, instruments, raga, tala, tempo and mood**, and never name a song, film, album, lyric line or famous tune, not even "like the song from ...".
- Never put a person's name in a music prompt: no singer, composer, band or "in the style of ...". The music models refuse to copy artists, and it is a copyright risk. Describe the era and sound instead ("1960s Bombay film orchestra: lush strings, mandolin and dholak"), not the composer.
- Instrumental only. Every prompt ends with "instrumental only, no vocals, no singing, no chanting, no spoken words". A Short already has a voice. No sung syllables either: no "aa" vocalise, no sargam, no bols, no alaap singing.
- Sacred sounds stay respectful. No mantras, Quranic recitation, Gurbani, church hymns or temple chants in background music. Devotional instruments and moods (shehnai, temple bells, Qawwali handclaps, singing bowls) are fine when the story is respectful. Never put devotional music under comedy that mocks a faith.
- Leave room for the voice. Background music sits under narration at low volume, so ask for a sparse, uncluttered middle (where the voice is), a steady pulse, no sudden loud hits, no big drop and no long silences.
- Tracks run 30 to 90 seconds. Ask for one clear arc: soft start, gentle build, a lift near the end.

## 2. How to write the prompt (for Google Lyria 3 Pro on fal, also fine for Stable Audio)

One paragraph of 60 to 120 words, in this order (and with the timed cues from music-scoring.md §5 woven into step 5):
1. Genre and tradition: "Hindustani classical fusion underscore", "Rajasthani folk", "Javanese gamelan-inspired ambient".
2. Two to four lead instruments, each named exactly: "bansuri flute, santoor, soft tabla", never "Indian instruments" or "ethnic sounds".
3. Raga, scale or mode, and its feel: "in the mood of Raga Yaman, serene evening devotion" (models know the big ragas by name; add the feel as well in case they don't).
4. Rhythm: tala or groove plus BPM. "slow Teentaal, 75 BPM", "Keherwa groove, 96 BPM".
5. Mood and arc: "starts as a calm drone, builds curiosity, hopeful lift in the last 10 seconds".
6. Production: "modern cinematic mix, warm tanpura drone bed, sparse midrange to leave room for narration".
7. The fixed ending: "instrumental only, no vocals, no singing, no chanting, no spoken words".

Example: "Hindustani classical fusion underscore with bansuri flute, santoor and soft tabla, in the mood of Raga Yaman, serene and wondering. Slow Teentaal at 76 BPM over a warm tanpura drone. Starts quiet, builds gentle curiosity, small hopeful lift near the end. Modern cinematic mix, sparse midrange to leave room for narration. Instrumental only, no vocals, no singing, no chanting, no spoken words."

Fusion is usually best for a global audience: one or two traditional lead instruments over a modern cinematic bed (soft pads, low piano, light electronic pulse). Go fully traditional only when the story is about that tradition or region.

## 3. Rasa: the Indian theory of mood

Bharata's Natyashastra (about 200 BCE to 200 CE) names eight rasas (moods). Later writers added a ninth, shanta (peace). Use it to match music to the story's feeling.

| Rasa | Feeling | Music that carries it |
| --- | --- | --- |
| Shringara | love, beauty, longing | Yaman, Khamaj, Kafi, Desh; sitar or sarangi, slow Keherwa |
| Hasya | humour, play | Khamaj or Pilu, bouncy Dadra or Keherwa, dholak, clarinet, brass-band toots, pizzicato |
| Karuna | sadness, compassion | Bhairavi, Todi, Jogiya; sarangi, slow shehnai, solo bansuri, very slow tempo |
| Raudra | anger, protest | Marwa or Puriya Dhanashri, fast tabla tihais, low dhol, dark strings |
| Veera | courage, pride, triumph | Desh, Durga, Hamsadhwani, Mohanam; shehnai, nadaswaram, dhol, brass, a march pulse |
| Bhayanaka | fear, danger | Marwa, Todi, low drones, sparse ghatam and mridangam hits, bowed metal |
| Bibhatsa | disgust (we avoid it) | stay neutral and tense instead |
| Adbhuta | wonder, surprise | Yaman, Hamsadhwani, Kirwani; santoor shimmer, bell tones, rising pads |
| Shanta | peace, calm | Bhupali, Bageshree, Malkauns at a slow tempo; tanpura drone, bansuri, rain-like santoor |

## 4. Hindustani classical (North India)

- Ten thaats (parent scales, as Bhatkhande grouped them): Bilawal (the major scale), Kalyan (raised 4th), Khamaj (flat 7th), Kafi (flat 3rd and 7th), Asavari (natural minor), Bhairavi (all flat: re, ga, dha, ni), Bhairav (flat re and dha), Marwa (flat re, raised ma), Purvi (flat re and dha, raised ma), Todi (flat re, ga and dha, raised ma).
- A raga is more than a scale: it has a rising and falling path, main notes (vadi and samvadi), signature phrases (pakad), and a time of day and season (the samay chakra).
- Ragas by time and mood:
  - Dawn: **Bhairav** (grave, devotional), **Lalit** (restless, dawn twilight), **Todi** (pathos, morning), **Ahir Bhairav** (gentle, folk-tinged).
  - Morning: **Jaunpuri**, **Bilawal** (bright, plain), **Bhairavi** (traditionally sung last at a concert; tender, bittersweet).
  - Afternoon: **Bhimpalasi** (longing), **Multani** (intense, golden), **Brindavani Sarang** (sunny, pastoral).
  - Dusk: **Marwa** (anxious, sunset unrest), **Puriya Dhanashri** (yearning), **Shree** (solemn).
  - Evening: **Yaman** (serene, devotional, the best all-rounder for wonder), **Bhupali** (pentatonic, calm, open), **Hamsadhwani** (bright, auspicious; from the Carnatic side), **Kedar** (stately), **Desh** (patriotic, monsoon warmth), **Khamaj** (light, romantic, playful).
  - Night: **Bageshree** (romantic waiting), **Darbari Kanada** (deep, regal, slow and grave), **Malkauns** (pentatonic, meditative, mysterious), **Chandrakauns** (mysterious, modern), **Jog** (bluesy), **Kirwani** (the harmonic minor; cinematic, emotional).
  - Seasons: **Megh** and **Miyan ki Malhar** for the monsoon and rain, **Basant** and **Bahar** for spring.
- Talas (rhythm cycles): Teentaal (16 beats, the most common), Ektaal (12, often very slow), Jhaptaal (10), Rupak (7, starts on an open beat), Keherwa (8, the light-music and film groove), Dadra (6, a swaying lilt), Deepchandi (14, thumri), Chautaal (12, for dhrupad on pakhawaj). Layas (tempos): vilambit is slow (about 30 to 60 BPM), madhya is medium (about 60 to 120), drut is fast (about 120 to 300 or more).
- How a performance unfolds (it maps neatly onto a Short's arc): alap (free, no beat, the raga revealed slowly) → jor (a pulse appears) → jhala (fast strummed climax) → gat or bandish (the composed piece, with tabla). For background music, ask for "alap-like opening, then tabla enters".
- Forms: dhrupad (oldest, austere, pakhawaj), khayal (the main vocal form), thumri, dadra and kajri (light, romantic), tarana (fast rhythmic syllables), ghazal (Urdu poetry, harmonium), bhajan (devotional), and the instrumental gat.
- Instruments: sitar (sympathetic strings, buzzing jawari tone), sarod (fretless, deep, metallic glides), surbahar (bass sitar), sarangi (bowed, closest to the human voice, sorrow), bansuri (bamboo flute, pastoral and Krishna imagery), shehnai (double reed, weddings and auspicious openings), santoor (hammered dulcimer from Kashmir, shimmering water), harmonium, tanpura (the drone behind everything), tabla (paired drums with a bass bend), pakhawaj (barrel drum, deep), swarmandal (a harp-like shimmer), and the jal tarang (tuned water bowls).

## 5. Carnatic classical (South India)

- The **melakarta** system arranges 72 parent scales in a grid (Venkatamakhin, 17th century; the names were settled later). Each has all seven notes. Janya ragas grow out of them.
- Ragas and moods:
  - **Mohanam** (pentatonic, joyful, same notes as Bhupali), **Hamsadhwani** (auspicious beginnings; the classic opener), **Kalyani** (majestic; Yaman's cousin), **Shankarabharanam** (the major scale; grand and complete), **Kharaharapriya** (Dorian; deep and versatile), **Todi** (Carnatic Todi; profound, heavy with gamaka).
  - **Abhogi** and **Hindolam** (night, meditative; Hindolam is like Malkauns), **Shivaranjani** (sorrow, longing), **Revati** (Vedic and spiritual, austere), **Sindhubhairavi** (emotional, folk-like), **Charukesi** (bittersweet, cinematic), **Keeravani** (harmonic minor; dramatic), **Madhyamavati** (closing, benediction), **Neelambari** (lullaby), **Vasantha** (spring), **Bilahari** (bright morning), **Kanada** and **Atana** (vigour).
- Talas: Adi (8 beats, the most common), Rupaka (3 or 6), Misra Chapu (7, uneven 3+4), Khanda Chapu (5, 2+3), plus the 35-tala Suladi system. Konnakol is rhythm spoken as syllables; avoid it, since it counts as voice.
- Gamaka: the oscillating ornaments that make Carnatic sound Carnatic. Ask for "rich gamaka ornamentation on veena or violin".
- Forms: varnam (etude), kriti (the main composed song; the Trinity is Tyagaraja, Dikshitar and Syama Sastri, all public domain as works, but don't copy known kritis), tillana (fast, dance-like, joyful), javali and padam (romantic), ragam-tanam-pallavi (improvised showpiece), thani avartanam (percussion solo).
- Instruments: Saraswati veena (rich and bending), mridangam (two-headed drum; the backbone), ghatam (clay pot, crisp), kanjira (frame drum with a jingle), morsing (jaw harp, a springy twang), violin (played seated, with heavy gamaka), venu (bamboo flute), nadaswaram (loud temple double reed) with thavil (temple drum), gottuvadhyam (slide veena), and the mandolin.

## 6. Folk music by region

Use a region's sound when the story is set there. All of these are traditional forms; only recordings and named songs are owned.

- **Punjab**: bhangra (dhol with its chaal groove, tumbi one-string twang, algoza double flute, chimta tongs, the "hoy" shout; we leave out the shouts), giddha for women's songs, boliyan. Energy, harvest, celebration.
- **Rajasthan**: the Manganiyar and Langa hereditary musicians; kamaicha (bowed, deep), khartal (wooden clappers), morchang (jaw harp), algoza, dholak, ravanhatta (ancient bowed fiddle), sarangi (the Sindhi sarangi). Forms: Maand (royal, desert), Panihari. Desert, forts, camels, vast space.
- **Gujarat**: garba and dandiya raas (circle-dance claps, dhol, a 6 or 8 groove), Navratri energy.
- **Bengal**: Baul (wandering mystics; ektara, dotara, khamak plucked drum, dubki), Bhatiali (river boatmen's songs, slow and wide), the Rabindra Sangeet melodic style (avoid copying songs). Rivers, mysticism, monsoon.
- **Assam and the Northeast**: Bihu (dhol, pepa buffalo-horn pipe, gogona bamboo jaw harp, toka clapper), the Manipuri pung drum and sankirtana, Naga and Mizo choral and log drums, Khasi duitara. Hills, harvest, spring festival.
- **Kashmir**: Sufiana kalam (santoor, setar, the Kashmiri saz, tumbaknari goblet drum, wasul), Chakri, Rouf. Lakes, snow, poetry.
- **Himachal and Uttarakhand (the Pahari sound; the home sound for Nima)**: Kullu nati (circle dance, a slow-to-fast 6 or 8 lilt), ransingha and narsingha (curved copper horns for processions), dhol-damau pair, hudka hourglass drum, bansuri and algoza-style flutes, Jagar (ritual, so avoid it), the Pahari raga (light and mountain-sweet). Mountains, mist, apple orchards, temples.
- **Maharashtra**: lavani (fast dholki and tuntuni, spirited), powada (heroic ballads), Koli fisherfolk songs, dhol-tasha (Ganesh festival drum lines).
- **Goa and the Konkan**: mando and dulpod (Portuguese-Konkani blend, guitar and ghumot drum).
- **Kerala**: chenda melam (huge cylindrical drum orchestras, the Panchari and Pandi melam), panchavadyam (five instruments: timila, maddalam, ilathalam, idakka, kombu horn), sopana sangeetham (temple steps singing; instrumental idakka only), the Kathakali percussion. Monsoon, temples, festival elephants.
- **Tamil Nadu**: parai (frame drum of resistance and celebration), nadaswaram with thavil (weddings, temples), oyilattam, the gaana street style of Chennai, and the kuthu dance-beat style. Energy, the street, pride.
- **Karnataka**: Yakshagana (chande drum, maddale, a high, theatrical sound), dollu kunitha (big drum dances), Janapada.
- **Andhra Pradesh and Telangana**: Burrakatha (tambura and drum storytelling), the Bonalu festival drums, the Kuchipudi rhythm.
- **Odisha**: Odissi (its own classical tradition, mardala drum), Sambalpuri folk (dhol, nisan, tasha, muhuri, the "dulduli" ensemble).
- **Bihar and Uttar Pradesh**: Bhojpuri folk (birha, chaita, kajri for the monsoon, sohar for births), the nautanki theatre band (nagada, shehnai), the Awadhi and Braj rasiya (Holi, Krishna).
- **Central and tribal India (Chhattisgarh, Jharkhand, Madhya Pradesh)**: mandar and nagara drums, Santhal flute and banam fiddle, Gond and Bhil songs, Pandavani epic storytelling. Forests, earth, community.
- **Sindh, Balochistan and the cross-border Punjab**: the Sindhi sarangi and borindo (clay flute), Baloch suroz fiddle and benju; share them, but avoid politics.

## 7. Indian film music, era by era (describe the era; never name a song or person in a prompt)

- **1930s-40s, the early talkies**: harmonium, tabla, small string groups, stage-musical feel, simple melodies.
- **1950s-60s, the golden age**: big orchestras (violins, mandolin, accordion, harmonium, dholak, bongos, flute), classical ragas in light songs, ghazal elegance, cabaret jazz for villains. A warm, nostalgic, black-and-white romance feel.
- **1970s**: funk, disco, rock guitar, brass, wah-wah, Latin percussion, bold experimental sounds (bottle and comb rhythms), qawwali-style film numbers. Retro swagger.
- **1980s**: disco synths, drum machines, electronic toms, synth-pop; South cinema blends Western classical counterpoint with Tamil folk (a symphonic strings-meet-village-drum sound).
- **1990s**: a melody revival (lush strings, santoor and flute, dholak love-song grooves) and the digital revolution from Madras (layered synths, Carnatic ornaments over world-music and reggae beats, airy reverb, big choirs).
- **2000s**: Sufi-rock (rock guitar under qawwali-style builds), the Punjabi bhangra-pop boom, item-song dhol-electro, rock bands.
- **2010s-2020s**: EDM drops, trap hi-hats with tabla samples, indie acoustic, lo-fi Bollywood (vinyl crackle, soft keys, old-film nostalgia), the pan-India South mass sound (thunderous drums, brass stabs, chant-like hooks), and Malayalam indie realism.
- Prompt phrases that work: "retro 1960s Indian film orchestra underscore", "1970s Bollywood funk with brass and wah guitar", "90s Indian romantic strings and santoor", "modern pan-India cinematic mass drums and brass", "lo-fi Bollywood nostalgia beat".

## 8. Qawwali and Sufi music

- Qawwali is the devotional music of Sufi shrines (dargahs) in the Chishti order of South Asia. The tradition credits Amir Khusrau (13th-14th century, Delhi) with shaping it; many qawwali families trace their line to him.
- The sound: harmonium lead, tabla and dholak, rhythmic group handclaps, a lead singer with a chorus answering. It starts slow and grows in waves, faster and louder, towards an ecstatic peak (wajd). Typical rhythm: Keherwa or a fast Teentaal.
- Song types: hamd (praise of God), naat (praise of the Prophet), manqabat (praise of saints), ghazal (love that is also divine), and qaul and rang (ceremonial).
- Since we are instrumental, use the **instrumental qawwali feel**: "Sufi qawwali-inspired instrumental: harmonium melody, dholak and tabla, rhythmic handclaps building in waves to an ecstatic peak, no vocals". This suits stories of devotion, unity, a slow build to a triumphant reveal, or Delhi and Ajmer history.
- Other Sufi strands: Kashmiri Sufiana kalam, Punjabi and Sindhi kafi (Bulleh Shah and Shah Abdul Latif poetry; instrumental only for us), Rajasthani Sufi songs by Manganiyar singers, and the Turkish Mevlevi ney with the whirling-ceremony feel.

## 9. Old art music of the rest of Asia

- **Persia (Iran)**: the radif repertoire organised into 7 dastgahs (Shur, Homayun, Segah, Chahargah, Mahur, Rast-Panjgah, Nava) plus derived avaz (Abu Ata, Bayat-e Tork, Afshari, Dashti, Bayat-e Esfahan, and others). Microtones (koron and sori). Instruments: tar, setar, santur (an ancestor of the Kashmiri santoor), kamancheh (spike fiddle), ney (reed flute), tombak (goblet drum), daf (frame drum). Free-rhythm avaz then rhythmic pieces. Mood: poetic, melancholy, mystical. It shares deep roots with Hindustani music through the Mughal courts.
- **The Arab world and Turkey**: the maqam system (Rast, Bayati, Hijaz, Saba, Nahawand, Kurd, Sikah, Ajam) with microtones and iqa rhythms (maqsum, wahda, samai thaqil). Oud, qanun, nay, riq, darbuka. The Turkish makam with ney and kanun, and the Ottoman court and Mevlevi traditions. Hijaz gives an instant "desert or ancient" colour; use it carefully, since it is a cliché.
- **Central Asia**: the Uzbek and Tajik Shashmaqam (six maqams), the Kazakh dombra and Kyrgyz komuz, the Afghan rubab (lute; also in Kashmir), Tuvan and Mongolian throat singing (voice, so we avoid it) and the morin khuur horsehead fiddle. Steppe, horses, the Silk Road.
- **China**: pentatonic modes (gong, shang, jue, zhi, yu). The guqin (seven-string zither, the scholar's instrument, over 3,000 years of tradition, meditative), guzheng (bright plucked zither with bends), pipa (lute, dramatic tremolo), erhu (two-string fiddle, a crying voice), dizi (bamboo flute with a buzzing membrane), xiao (soft end-blown flute), sheng (mouth organ). Kunqu opera (one of the oldest), the Jiangnan sizhu tea-house ensemble, Peking opera percussion (gongs and clappers, for drama).
- **Japan**: **gagaku** (imperial court music, one of the oldest orchestral traditions still played, from the Nara and Heian periods; sho mouth organ clusters, hichiriki oboe, ryuteki flute, biwa, gakuso zither, kakko and taiko drums; slow, timeless, ceremonial). The shakuhachi (Zen honkyoku; breathy and spacious), koto, shamisen (sharp and percussive), taiko ensembles (power), and the noh hayashi. Scales: hirajoshi, in (miyako-bushi), yo, ryukyu (Okinawa, the sanshin). The idea of **ma**: meaningful silence and space.
- **Korea**: gugak (traditional music), the court jongmyo jeryeak (ritual), sanjo (solo improvisation that speeds up), pansori (sung storytelling; voice, so avoid it). The gayageum (zither), geomungo (deep zither), haegeum (fiddle), daegeum (large flute with a buzzing membrane), piri, janggu (hourglass drum), buk. Jangdan rhythm cycles (jinyang slow, jungmori, gutgeori, jajinmori fast). Samul nori percussion for energy.
- **Indonesia, gamelan**: ensembles of bronze gongs and metallophones. Two tunings, **slendro** (5 near-equal notes) and **pelog** (7 uneven notes); every set is tuned to itself, so no two gamelans are exactly alike. Colotomic structure: a big gong (gong ageng) marks the end of each cycle, smaller gongs (kempul, kenong, ketuk) divide it. Javanese gamelan is slow, stately and meditative; Balinese gong kebyar is explosive and shimmering with interlocking kotekan patterns. Kendang drums lead. The Kecak monkey chant is voice, so avoid it. Sundanese kacapi suling (zither and flute) is gentle.
- **Mainland Southeast Asia**: the Thai piphat ensemble (ranat xylophone, khong wong gong circle, pi oboe), Cambodian pinpeat, the Vietnamese dan bau monochord (bending one-string sound) and dan tranh zither, Burmese saing waing drum-circle ensembles, the Philippine kulintang gongs.
- **The Himalayas, Tibet, Nepal and Bhutan**: Tibetan Buddhist ritual music (dungchen long horns, gyaling oboes, rolmo cymbals, damaru, singing bowls; avoid chant), the Nepali sarangi, madal drum and bansuri, Newar dhime drums. It fits Nima's mountain world when used gently and with respect.
- **Sri Lanka**: Kandyan drumming (geta bera), the Sinhala raban, the low-country yak bera drums, and the Tamil Sri Lankan nadaswaram traditions.

## 10. Our channels: the default sound for each

| Channel | Default sound | When to change it |
| --- | --- | --- |
| Hopeverse Media (global news, English) | modern cinematic news underscore: soft pulse, low piano, pads, 90-100 BPM, steady curiosity | Add one regional lead instrument when the story is set in a region (a bansuri for India, a guzheng for China, an oud for the Middle East, gamelan bells for Indonesia). Serious stories (war, disaster, death): sombre low strings only, never a regional cliché and never anything upbeat. |
| Instinct (French nature, animal behaviour) | warm nature-documentary score: strings, marimba, soft woodwinds, 80-100 BPM | Use the animal's homeland sound gently: an Indian tiger gets bansuri and a tabla pulse; an African animal gets kalimba and hand drums; an Arctic animal gets airy pads and a glassy celesta; Asian forests get gamelan or guzheng; a hunt gets tense taiko-like low drums with no gore implied. |
| Sankalp (Hindi, national pride, development) | uplifting Indian cinematic: shehnai or bansuri lead in the mood of Raga Desh or Durga, strings, dhol and a soft march pulse, 95-110 BPM | Science and space wins get a modern synth pulse plus sitar; heritage stories get pure classical (Yaman or Hamsadhwani). Never copy the national anthem, national song or any patriotic film song. |
| Sawaal (Hindi, the questions people ask) | tense investigative: low tanpura drone, a sparse tabla pulse, a dark pad in the mood of Raga Marwa or Todi, 80-90 BPM | Stay neutral and serious; no mocking or comic music under politicians. |
| Kissa (Hindi micro drama, paused) | K-drama-style piano and strings with an Indian colour (sarangi or bansuri), in the mood of Kirwani or Charukesi | Cliffhanger: rising strings that stop on an unresolved note. |
| Uno Reverse (Hinglish couple comedy) | playful light-comedy cue: pizzicato strings, dholak in a bouncy Dadra, clarinet or wedding-brass toots, Raga Khamaj, 105-120 BPM | Argument beats: quick tabla rolls and comic stingers. Make-up endings: a warm sitar or bansuri resolve. |
| Nima (Himalayan slice-of-life, English) | gentle Pahari folk: bansuri, santoor, a soft Kullu nati lilt, hand drum, the Pahari raga mood, 70-90 BPM, misty and warm | Festival days: dhol-damau and ransingha horns in the distance. Rain or snow: slower, more space. |

## 11. Mood recipes (mix and match)

- **Wonder or a discovery**: santoor shimmer, bansuri, soft pads, the Yaman or Hamsadhwani mood, rising arc, 85 BPM.
- **Suspense or mystery**: tanpura drone, sparse ghatam or tabla, low bowed sarangi, the Malkauns or Marwa mood, 70-80 BPM.
- **Triumph or a record broken**: shehnai or nadaswaram lead, dhol and thavil, brass, the Desh or Mohanam mood, 110 BPM, a big lift at the end.
- **Sadness or loss**: solo sarangi or bansuri, very sparse, the Bhairavi or Shivaranjani mood, 60 BPM, no drums.
- **Romance or tenderness**: sitar and strings, a soft Keherwa groove, the Khamaj or Bageshree mood, 80 BPM.
- **Comedy**: dholak in Dadra, pizzicato, clarinet, a light Pilu or Khamaj feel, 115 BPM.
- **Energy or a festival**: dhol bhangra chaal, or chenda melam, or a Bihu dhol and pepa, 120-130 BPM.
- **Devotion or calm**: harmonium and tabla in a qawwali-style slow build, or tanpura, bansuri and temple bells in the Bhupali mood, 70 BPM.
- **Nostalgia or history**: retro 1960s film orchestra, or vinyl lo-fi Bollywood, or gagaku-like sustained sho chords for ancient Asia.
- **Tech or the future**: a modern synth arpeggio and pulse with a sitar or veena hook on top, the Kirwani mood, 100 BPM.

## 12. Music story ideas (Shorts we can make, all facts checkable)

Each one is a 45-60 second Short. Mr. Focus must fact-check it before scripting. Label legends as legends.
1. Why Indian ragas have a time of day: the samay chakra, and why Bhairav belongs to dawn.
2. One grid holds 72 scales: how the Carnatic melakarta system works, like a periodic table of music.
3. The legend of Raga Deepak lighting lamps and Megh Malhar bringing rain (a legend, not a fact; say so).
4. The tabla's bass bend: how one hand changes pitch mid-beat, and the paste (syahi) that makes it ring.
5. No two gamelans are tuned the same: each set belongs to its village.
6. Gagaku: one of the world's oldest living orchestras, still played for Japan's imperial court.
7. The santoor's journey from Persia to Kashmir to film studios.
8. The Manganiyars: desert families who have sung for their patrons for generations.
9. Konnakol: drummers who speak rhythms faster than most people can clap (a fact Short; the music under it stays instrumental).
10. Qawwali's 700-year line back to medieval Delhi.
11. Why the sarangi is called the instrument closest to the human voice.
12. Mridangam and ghatam: South India's rhythm science in two drums.
13. The guqin: 3,000 years old, and listed by UNESCO.
14. Bihu: how a harvest festival's buffalo-horn pipe announces spring in Assam.
15. Bhangra began as a harvest dance in Punjab's fields before it went global.
16. The shehnai: why one reed instrument means "wedding" for a billion people.
17. Chenda melam: Kerala drum orchestras of 100+ drummers playing in sync.
18. The Persian roots of Indian court music under the Mughals.
19. Kullu nati, the Himalayan circle dance (a fit for Nima).
20. Why film songs in India switched from orchestras to computers in the 1990s.
21. Throat singing: one person, two notes at once (the science of overtones).
22. Indian Ocean trade routes that carried instruments from Africa to Indonesia.

UNESCO-listed traditions worth a Short (check the year each was listed before scripting): Vedic chanting, Kutiyattam Sanskrit theatre of Kerala, Ramlila, Chhau dance, the Kalbelia songs and dances of Rajasthan, the Sankirtana of Manipur, Buddhist chanting of Ladakh, Nowruz, gamelan (Indonesia, 2021), gagaku (Japan, 2009), the guqin (China, 2003/2008), pansori (Korea, 2003/2008), the Shashmaqom (Uzbekistan and Tajikistan, 2003/2008), and the radif of Iranian music (2009).

## 13. Composer sound profiles (owner's favourites, 28 Oct 2026)

The owner loves these composers. Mr. Raga cannot listen to audio, so these profiles come from what is written about each one's music. Use them to borrow a **sound**, never a tune. **Never put a composer's name, film or song in the music prompt**: ElevenLabs and Lyria refuse artist imitation, and copying a melody is a copyright strike. Write the traits instead. A brief may say internally "Raga-Rahman-90s sound"; the prompt says "1990s Madras digital-orchestral...".

**Early A.R. Rahman (1992-2005, the Madras digital era)**
- Sound: the first fully digital Indian film scores. Deep sub-bass, very wide reverb and stereo space, glossy layered synth pads under acoustic Indian instruments, and a clean, airy mix that sounded international.
- Melody: Carnatic and Hindustani ornaments (gamaka, meend) on simple, singable lines; ragas used freely, not strictly. Sufi and qawwali colours (harmonium, handclaps, waves of build), and Tamil folk inside world-music grooves (reggae, Latin, Arabic).
- Instruments he made famous in film: bansuri and shakuhachi-like breathy flutes, shehnai and nadaswaram over synths, the santoor, the mandolin, the veena, a single solo violin, and big frame drums and ghatam with drum machines.
- Structure: long, quiet intros (a solo flute over a pad, or silence), sudden key or texture shifts, and slow builds to a big release.
- Prompt traits: "1990s South Indian digital-orchestral film score: deep sub-bass, wide airy reverb, glossy synth pads under bansuri and nadaswaram, Carnatic-ornamented melody, frame drums with a soft world-music groove, slow build to a soaring release".

**Anirudh Ravichander (2011 onwards, the Tamil mass and pop sound)**
- Sound: high-energy Tamil pop and "mass" BGM. A punchy kick, 808 bass, trap hi-hats, brass and synth stabs, electric-guitar riffs, and whistled or chant-like hooks (we keep them as instruments: whistle, brass, synth lead). Often 120-140 BPM, in a minor key with a heroic lift.
- Hero BGM formula: a low, tense ostinato (pulsing synth or strings), a riser, one silent beat, then a huge drop with thundering drums, brass and a simple 3-4-note riff that repeats.
- Kuthu side: Tamil folk dance rhythms (thappu and parai patterns) under EDM synths.
- Thriller side: dark minimal electronics, a heartbeat kick, and detuned pads.
- Prompt traits: "modern Tamil mass-hero cinematic BGM: low pulsing synth ostinato, riser, one beat of silence, then a massive drop with thundering drums, brass stabs, a distorted guitar riff and a catchy 4-note synth hook, 128 BPM, minor key, triumphant".

**Sai Abhyankkar (2024 onwards, the new Tamil indie-pop sound)**
- Background: a Chennai composer, singer and multi-instrumentalist (keys, tabla, mridangam, piano, drums, guitar), son of playback singers Tippu and Harini. His indie singles "Katchi Sera" (Jan 2024) and "Aasa Kooda" (Jun 2024) went viral; his film scores include Balti (2025), Dude (2025) and Karuppu (2026).
- Sound: Tamil pop that mixes club-ready hooks with grand, cinematic arrangements. Jazz and blues touches in the chords, grooves built up in layers, a simple piano motif that grows with mandolin, nadaswaram-like reeds and brass, nostalgic layers of older Tamil music, and an unhurried build rather than rushing to the hook.
- Prompt traits: "modern Tamil indie-pop groove: a simple piano motif, warm bass groove, jazzy seventh chords, light mridangam and tabla patterns with a pop kick, mandolin and brass layers added one by one, nostalgic retro South Indian colour, unhurried build, 100 BPM, feel-good".

**Ilaiyaraaja (1976 onwards, the Maestro)**
- Sound: Western classical craft (counterpoint, fugue-like string writing, real orchestral harmony) fused with Tamil village folk and Carnatic ragas. He has scored well over 1,000 films and wrote a symphony for London's Royal Philharmonic.
- Signatures: melodic bass-guitar lines that move like a second melody, flute-and-violin interludes in counterpoint, pastoral village colour (the thavil, urumi, parai and nadaswaram, with the cycle of the folk 6/8), solo violin or flute leitmotifs in the background score, and a warm, analogue 1980s studio sound.
- Raga use: deep, often hidden inside a pop song; he is known for light-music songs built on classical ragas.
- Prompt traits: "1980s South Indian film orchestra in the classical-folk fusion tradition: a flute-and-violin counterpoint interlude, a melodic bass guitar line, string section harmony, village thavil and folk 6/8 rhythm, a warm analogue studio sound, pastoral and nostalgic, 90 BPM".

**Which channel gets which sound**: Sankalp gets an early-Rahman pride build or an Ilaiyaraaja pastoral sound for village stories. Uno Reverse gets the Sai Abhyankkar indie groove or an Anirudh kuthu sound for fights and making up. Hopeverse uses the Anirudh-style hero drop only for big wins (a record, a launch). Nima gets the Ilaiyaraaja pastoral flute-and-violin sound (Himalayan instruments instead of Tamil ones). Kissa gets early-Rahman romance. Never use the same composer sound on the same channel twice in a row.

## 14. The full raga catalogue

### The 72 Carnatic melakartas
Every melakarta has all seven notes (Sa, Ri, Ga, Ma, Pa, Dha, Ni) in a fixed order up and down. They come in 12 groups (chakras) of 6. 1-36 use the natural Ma (shuddha madhyamam); 37-72 use the raised Ma (prati madhyamam). In each chakra, Ri and Ga stay the same and Dha and Ni change.

| Chakra | Melakartas (number: name) |
| --- | --- |
| 1 Indu | 1 Kanakangi, 2 Ratnangi, 3 Ganamurti, 4 Vanaspati, 5 Manavati, 6 Tanarupi |
| 2 Netra | 7 Senavati, 8 Hanumatodi, 9 Dhenuka, 10 Natakapriya, 11 Kokilapriya, 12 Rupavati |
| 3 Agni | 13 Gayakapriya, 14 Vakulabharanam, 15 Mayamalavagowla, 16 Chakravakam, 17 Suryakantam, 18 Hatakambari |
| 4 Veda | 19 Jhankaradhwani, 20 Natabhairavi, 21 Keeravani, 22 Kharaharapriya, 23 Gourimanohari, 24 Varunapriya |
| 5 Bana | 25 Mararanjani, 26 Charukesi, 27 Sarasangi, 28 Harikambhoji, 29 Dheerasankarabharanam, 30 Naganandini |
| 6 Rutu | 31 Yagapriya, 32 Ragavardhini, 33 Gangeyabhushani, 34 Vagadheeswari, 35 Shulini, 36 Chalanata |
| 7 Rishi | 37 Salagam, 38 Jalarnavam, 39 Jhalavarali, 40 Navaneetam, 41 Pavani, 42 Raghupriya |
| 8 Vasu | 43 Gavambhodi, 44 Bhavapriya, 45 Shubhapantuvarali, 46 Shadvidamargini, 47 Suvarnangi, 48 Divyamani |
| 9 Brahma | 49 Dhavalambari, 50 Namanarayani, 51 Kamavardhini, 52 Ramapriya, 53 Gamanashrama, 54 Vishwambari |
| 10 Disi | 55 Shamalangi, 56 Shanmukhapriya, 57 Simhendramadhyamam, 58 Hemavati, 59 Dharmavati, 60 Neetimati |
| 11 Rudra | 61 Kantamani, 62 Rishabhapriya, 63 Latangi, 64 Vachaspati, 65 Mechakalyani, 66 Chitrambari |
| 12 Aditya | 67 Sucharitra, 68 Jyotiswarupini, 69 Dhatuvardhani, 70 Nasikabhushani, 71 Kosalam, 72 Rasikapriya |

The melakartas that have a Western or Hindustani match (useful, because music AIs know the Western names):
- 8 Hanumatodi: Phrygian mode; the Bhairavi thaat. Dark and devotional.
- 14 Vakulabharanam: Phrygian dominant, the Arabic Hijaz sound. Desert and ancient.
- 15 Mayamalavagowla: the double harmonic scale; the Bhairav thaat. Dawn, temples, the first scale every Carnatic student learns.
- 20 Natabhairavi: natural minor (Aeolian); the Asavari thaat. Sad and serious.
- 21 Keeravani: harmonic minor; Hindustani Kirwani. Dramatic and cinematic.
- 22 Kharaharapriya: Dorian mode; the Kafi thaat. Soulful, folk-like.
- 28 Harikambhoji: Mixolydian mode; the Khamaj thaat. Light and romantic.
- 29 Dheerasankarabharanam: the major scale (Ionian); the Bilawal thaat. Bright and grand.
- 45 Shubhapantuvarali: the Todi thaat. Grief and longing.
- 51 Kamavardhini (Pantuvarali): the Purvi thaat. Dusk, solemn.
- 53 Gamanashrama: the Marwa thaat. Restless sunset.
- 57 Simhendramadhyamam: the Hungarian minor scale. Exotic and dramatic.
- 59 Dharmavati: close to Hindustani Madhuvanti. Sweet, longing.
- 64 Vachaspati: Lydian dominant (the acoustic scale). Bright with a twist, a "sci-fi wonder" feel.
- 65 Mechakalyani (Kalyani): Lydian mode; the Kalyan thaat (Yaman). Serene, majestic.

### Carnatic janya ragas (derived ragas) by mood
- Joy, celebration: Mohanam, Hamsadhwani, Bilahari, Kadanakuthuhalam, Arabhi, Nattai, Behag (Carnatic).
- Devotion, peace: Revati, Sama, Ahiri, Saveri, Bhupalam (dawn), Malayamarutham (dawn), Shuddha Dhanyasi.
- Love, romance: Kapi, Kamas, Khamas, Hamir Kalyani, Yamuna Kalyani, Desh (Carnatic), Behag.
- Sadness, longing: Shivaranjani, Mukhari, Ahiri, Subhapantuvarali, Neelambari (lullaby), Huseni.
- Grandeur, heroism: Atana, Kanada, Darbar, Begada, Sri, Kambhoji, Nata.
- Mystery, night: Hindolam, Abhogi, Ranjani, Bhairavi (Carnatic).
- Folk-like, lilting: Sindhubhairavi, Anandabhairavi, Kurinji, Navroj, Punnagavarali (the snake-charmer sound).
- Closing, benediction: Madhyamavati, Surati, Sourashtram.

### More Hindustani ragas, by thaat
- **Bilawal**: Bilawal (Alhaiya), Durga (pentatonic, heroic and joyful), Deshkar, Hansadhwani (borrowed from Carnatic), Shankara (night, powerful), Bihag (night, romantic), Pahadi (mountain folk feel; the light-music favourite).
- **Kalyan**: Yaman, Yaman Kalyan, Bhupali, Shuddha Kalyan, Hameer, Kedar, Kamod, Chhayanat, Maru Bihag (yearning).
- **Khamaj**: Khamaj, Desh, Tilak Kamod, Jaijaiwanti (night, grand), Rageshree, Jhinjhoti, Tilang, Kalawati, Gara, Kafi-Khamaj mixes for thumri.
- **Kafi**: Kafi, Bageshree, Bhimpalasi, Dhanashree, Brindavani Sarang, Madhmad Sarang, Shuddha Sarang, Miyan ki Malhar, Megh, Gaud Malhar, Bahar, Pilu (light, playful), Barwa, Patdeep, Abhogi Kanada.
- **Asavari**: Asavari, Jaunpuri, Darbari Kanada, Adana, Kaunsi Kanada, Desi, Sindhu Bhairavi.
- **Bhairavi**: Bhairavi, Bilaskhani Todi, Malkauns, Komal Rishabh Asavari, Chandrakauns.
- **Bhairav**: Bhairav, Ahir Bhairav, Nat Bhairav, Ramkali, Jogiya (pathos), Kalingada, Gunakali, Basant Mukhari.
- **Marwa**: Marwa, Puriya, Sohini (late night, piercing), Lalit, Bhatiyar, Pancham, Vibhas.
- **Purvi**: Puriya Dhanashree, Shree, Basant, Paraj, Purvi, Gauri.
- **Todi**: Miyan ki Todi, Gurjari Todi, Multani, Madhuvanti (late afternoon, sweet).
- Outside the thaats: Kirwani (harmonic minor), Charukeshi (from Carnatic), Jog (bluesy, both Ga notes), Madhukauns, Hemant, Janasammohini.
- Seasons: Basant, Bahar and Hindol for spring; Megh, Miyan ki Malhar and Gaud Malhar for the monsoon; Hemant for early winter.

### Quick finder: from mood to raga
| Need | Hindustani | Carnatic |
| --- | --- | --- |
| Hope, a new dawn | Lalit, Ahir Bhairav, Bhatiyar | Malayamarutham, Bhupalam |
| Wonder, discovery | Yaman, Hansadhwani, Maru Bihag | Kalyani, Vachaspati, Hamsadhwani |
| Pride, victory | Durga, Desh, Shankara | Mohanam, Atana, Nattai |
| Love, tenderness | Bihag, Bageshree, Khamaj, Tilak Kamod | Kapi, Hamir Kalyani, Khamas |
| Loss, grief | Bhairavi, Jogiya, Todi, Marwa | Shivaranjani, Mukhari, Subhapantuvarali |
| Fear, danger | Marwa, Sohini, Puriya | Simhendramadhyamam, Gamanashrama |
| Calm, meditation | Malkauns, Bhupali, Chandrakauns | Hindolam, Abhogi, Revati |
| Fun, play | Pilu, Khamaj, Pahadi | Kadanakuthuhalam, Sindhubhairavi |
| Rain, monsoon | Megh, Miyan ki Malhar | Amritavarshini (a legend says it brings rain) |
| Night mystery | Darbari, Malkauns, Jog | Hindolam, Ranjani, Abhogi |
| Ancient, desert | Bhairav, Basant Mukhari | Vakulabharanam, Mayamalavagowla |
| Tech, future | Kirwani with synths, Madhuvanti | Vachaspati, Keeravani |

## 15. Scoring craft for Shorts (film-scoring technique)

- **Spotting**: decide where the music changes. In a Short there are usually 3 moments: the hook (0-3 s), the turn or reveal (around the middle) and the payoff (the last 5-10 s). Ask for the arc in those words: "quiet hook, builds through the middle, lifts at the reveal, warm resolve at the end".
- **Hit points**: the music is one track under the cuts, so don't ask for exact hits. Ask for a steady pulse whose BPM suits the cutting rate: cuts every 2-3 s suit 80-100 BPM (a cut every 4 or 2 beats); fast montages suit 120-130 BPM.
- **Ostinato and pedal**: a repeating figure (tabla theka, mridangam pattern, synth arpeggio) over a held drone (the tanpura is a natural pedal) keeps tension without fighting the voice. It is the safest bed for narration.
- **Leitmotif**: a short theme tied to a character or channel. For a recurring series (Nima, Uno Reverse) ask for the same lead instrument and the same raga each time, so the music becomes the channel's sound signature.
- **Under dialogue**: the voice lives at about 300 Hz-4 kHz. Ask for "sparse midrange, no busy lead melody during narration, low strings or drone plus light high percussion". Lead melodies belong in gaps (the intro and the outro).
- **Dynamics**: no sudden loud hits, no drop that buries a line, no long silence (a Short loses viewers in silence). A small riser into the payoff is fine.
- **Key and register**: low drones and bass give weight; a high bansuri, santoor or bells give wonder. Male narration (Arjun) sits low, so keep the bass clean; female narration (Meera, Nima) sits higher, so keep the upper midrange clear.
- **Avoid mickey-mousing** (music copying every action) in news and nature: underscore the feeling, not each event. Comedy (Uno Reverse) is the exception, where little stingers on the jokes work.
- **Stingers and transitions**: a tabla tihai, a mridangam korvai or a dhol roll makes a natural Indian "stinger" into the payoff, landing on sam.
- **Serious news**: no ragas with a festive colour, no festive percussion. Use low strings, a soft piano or a tanpura drone with a sombre raga (Bhairavi, Todi, Marwa) at a slow tempo.

## 16. Production basics Mr. Raga writes into briefs

- Mix words music AIs understand: "warm", "airy reverb", "close and intimate", "wide cinematic stereo", "lo-fi vinyl crackle", "clean modern mix", "analogue 1980s studio", "deep sub-bass", "punchy kick", "no harsh highs".
- Loudness: the background track is set to 12% under the voice by video.py, so ask for an even, steady level (little dynamic range), not a quiet intro that disappears under the voice.
- Length: ask for the Short's length or a bit more; video.py loops a short track, so an ending that resolves cleanly loops better.
- Always instrumental. ElevenLabs is also forced to instrumental by the code, but write it in the prompt anyway.

## 17. Romance in depth: how Indian music writes love (Jithesh, 29 Oct 2026)

Jithesh, after five "First Love" rounds: the takes had the wow factor but "these are not romantic". Our prompts asked for joy, a big chorus, a key lift and full drive, so they came out as **celebration**. The softened v5 was intimate but lost the rhythm. Romance is a journey through several feelings in one track, and the classical traditions already know how each one sounds.

### 17a. The theory (rasa)
- **Shringara** (love) has two halves: **sambhoga**, love in union, and **vipralambha**, love in separation and longing. A first-love track is **purvaraga**: "love born from sight or hearing before the lovers meet" (Sahityadarpana). Its first stage is **abhilasha**, longing to be near. The classical list goes on: chinta (thinking of her), smriti (replaying the moment), gunakathana (praising her), and then darker stages (agitation, fever) that a happy track never uses.
- **The body at first sight (sattvika bhava)**, and how each one sounds: stambha, freezing in place = one long held note with the rhythm hanging; vepathu, trembling = kampita gamaka (a fast oscillation on a note) or string tremolo; svarabhanga, the voice breaking = a breathy flute note that cracks or bends; romancha, goosebumps = a sparkle of swarmandal or santoor glints.
- The **sakhi** (her friend) teases and carries messages between the lovers. In music she is a third, playful voice (a tumbi or plucked line) that makes the love light and smiling, not heavy.

### 17b. Carnatic
- **Padam**: slow, tender love songs in mellow ragas (Anandabhairavi, Sahana, Nilambari, Ahiri, Mukhari, Huseni, Surati, Punnagavarali) on a subdued tala. The sangatis are gentle: each line comes back a little more ornamented, so the feeling grows line by line. Pallavi, anupallavi and charanam form the song.
- **Javali**: lighter, playful, flirtatious love songs at a medium tempo (Khamas, Kapi, Behag, Paras).
- **The film-romance ragas**: Reetigowla (its lilting zig-zag phrase G M N N S is the classic Tamil love-duet colour), Kapi (deep longing), Behag (romantic yearning), Kalyani (wonder: the raised 4th), Mohanam (bright, innocent, the pentatonic of duets), Hamsanandi, Keeravani, Abheri, Hamir Kalyani, Charukesi.
- **The gamakas carry the feeling**: kampita (trembling) = a trembling heart; jaru (slides) = reaching toward her; a held note that slides into the next = longing.

### 17c. Hindustani
- **Thumri, dadra**: the classical home of shringara, in Khamaj, Kafi, Pilu, Pahadi, Desh, Tilak Kamod, Jogiya and Bhairavi. The singer may touch notes outside the raga for colour (mishra); one "outside" note is the ache of longing.
- **The built-in romance structure**: a thumri begins in **bol banao**, slow and ornamented, with each phrase shaded again and again over a lilting tala (Deepchandi's 14 beats, Dadra's 6, Addha, Roopak's 7). It ends in a **laggi**, a switch to fast 8-beat Keherwa where the tabla plays freely. Slow longing that bursts into joyful release is exactly the first-love arc, and it is classical, not a Western build.
- **The evening love ragas**: Yaman (Kalyani), Bihag, Bageshree, Desh, Khamaj. The voice-like instruments are sarangi, violin and bansuri, with santoor and swarmandal for sparkle.

### 17d. Punjabi
- The love epics are Heer-Ranjha, Mirza-Sahiban and Sohni-Mahiwal. **Ranjha wins Heer with his flute** (as Krishna does Radha), so the flute is the lover's voice across North India.
- **The love song forms**: mahiya (short love verses on a fixed tune, longing but sweet), tappe (3-line ABA verses, call and response, romance and teasing, in Khamaj, Kafi, Bhairavi or Des, often on Punjabi taal), dhola (love as the main theme, loose structure), boliyan (teasing call-and-response lines), and Heer (free-time, deeply ornamented singing).
- **Sounds**: algoza (twin flutes, one holding a drone while the other sings: two lovers in one instrument), tumbi (a bright, high, playful pluck), sarangi, dholak, chimta. The dhol is for celebration only.
- **Rhythm**: simple and swinging, with a forward lilt (the chaal) that makes even a love song walk.

### 17e. The six parts of a first-love track (the map; use all six, in order)
1. **The glance (curiosity, stambha)**, about 8 s: free time over a soft drone. One flute or bansuri phrase with Kalyani's raised 4th held and left unresolved, swarmandal glints, no beat. Time freezes.
2. **Shyness (abhilasha)**, about 10 s: short, hesitant question-and-answer phrases (him on the flute, her on the violin or a hum) with breaths between them. A soft heartbeat on a low tabla starts here and never stops. The sakhi's tumbi teases.
3. **Attraction (the pull)**: the real melody in slow bol-banao style over a lilting 6-beat dadra. Long notes with kampita and slides, one aching outside note, and each phrase returns more ornamented (sangati).
4. **Togetherness (sambhoga begins)**: algoza-style, one voice holds while the other sings, then the two play in harmony. Strings warm up, and the rhythm becomes a steady Keherwa sway.
5. **Dream (gunakathana, the interlude)**: santoor cascades, soaring strings, a short solo showpiece and a gentle key lift.
6. **Bliss (the laggi)**: the tempo feels doubled, the tabla and dholak play freely, the tumbi bounces, the hums become a soft chorus. Joyful but still tender, never a festival. Then everything falls back to the part-1 phrase, now answered and resolved.

**Rules**: the rhythm, once it enters in part 2, never stops; it only changes (heartbeat, then dadra lilt, then Keherwa sway, then laggi). Celebration lives only in part 6. Write the parts in the prompt as a second-by-second timeline (the Neon Raja lesson). Pick one raga for the whole track so it stays one love story (Kalyani/Yaman for wonder, Reetigowla for the Tamil duet colour, Khamaj for Punjabi-thumri sweetness).

Sources: Sahityadarpana's definition of purvaraga (via wisdomlib), the Wikipedia articles on Thumri and Punjabi folk music, Scroll.in on Deepchandi, 4carnaticmusic on padams, and Shivpreet Singh on Punjabi tappe. The film-raga notes come from published Tamil film raga lists. Ragas and forms only, never a song's tune.
