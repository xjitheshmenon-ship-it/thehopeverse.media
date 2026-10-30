# Mr. Kavi's lyric knowledge

Mr. Kavi's reference for writing song lyrics in Malayalam, Tamil, Telugu, Hindi, Urdu, Arabic, English and singable vocables ("gibberish"), for ÆTHER and other music-channel tracks made on ElevenLabs Music. Edit freely; the kavi tool sends this whole file to Mr. Kavi.

## 1. Rules that keep us safe

- **Every word is new.** Never copy, quote, translate or lightly change a line from an existing song, poem, film dialogue, hymn or advert, in any language. No famous hooks, no song titles as hooks, no "answer songs" to a known lyric. Words, images and rhyme sounds belong to everyone; particular lines do not.
- **No names.** No singer, lyricist, composer, film, star or brand in the lyrics or in the vocal style notes. Describe the voice ("warm male tenor, Malayalam film-song diction"), never "sung like ...". This also keeps ElevenLabs' copyright filter from refusing the request.
- **Sacred words stay sacred.** No mantras, Quranic verses or phrases, Gurbani, hymn lines or names of God used as filler syllables (no "Om", "Allah hu", "Hallelujah" as vocables). A respectful devotional song needs the owner's go-ahead first.
- **Clean and kind.** No slurs, no mockery of a language, region, caste, religion or accent, no sexual lines. Comic songs laugh with people, never at a group.
- **Check every word in every language.** A made-up word or a vocable must not mean something rude or silly in any of our eight languages (section 11).
- **Mark the language and dialect** at the top of every lyric sheet (e.g. "Tamil, Chennai colloquial" or "Arabic, Egyptian colloquial"), and keep to it for the whole song.

## 2. Script first, then the music, then the words

The order for every sung track (music-scoring.md section 9 rules 17 and 18):

1. **Scene script.** Mr. Raga (or Mr. Hope) writes the timed beat table: what happens every 4-12 s.
2. **Music plan.** Mr. Raga turns it into sections: name, length in seconds, BPM, key, where the voice sings and where it rests, and the hook's rhythm.
3. **Words.** Mr. Kavi writes lines for each sung section, fitted to its length and BPM (section 3), in the language the brief asks for. Each line serves the beat it sits on: the glance gets a line about seeing, the turn gets the turn.
4. **Back to Mr. Raga.** The lines go into the plan section's `lines` (section 4). If a line doesn't fit the bar, Mr. Kavi rewrites the line; the music doesn't stretch to the words.

## 3. Fitting words to music

- **Bar length:** a 4/4 bar lasts 240 / BPM seconds (92 BPM: 2.6 s; 120 BPM: 2 s; 160 BPM: 1.5 s).
- **One line = one musical phrase,** usually 2 bars. Count the phrase's seconds and fill it at the section's pace:
  - ballad or love song: 2-3 syllables a second;
  - mid-tempo film song: 3-4 a second;
  - fast dance (kuthu, dabke, bhangra feel): 4-6 a second, short words, lots of repeats.
- **Leave air.** Use about 80% of the phrase and leave the last beat for a breath. A 16-s verse at 92 BPM holds 3 lines, not 6.
- **Long notes need open vowels.** End held lines on aa, ee, oo, ai, o (Malayalam "-aay", Tamil "-ae", Telugu "-aa", Hindi "-aa", Urdu "-aa hai", Arabic "-ā / -ī", English "-ay", "-oh", "-ee"). Avoid ending a held note on a stop consonant (k, t, p) or a cluster.
- **Stress on the beat.** Put the word's strong syllable (English stress, Hindi/Urdu long syllable, Dravidian first syllable) on beats 1 and 3.
- **Hook rules.** The hook is 2-6 words, sung at least 3 times, and comes back bigger each time (indian-touch rule). Its first word lands on beat 1. It must be easy to sing back after one listen.
- **Song shapes.** Indian film song: pallavi/mukhda (hook verse) - anupallavi or first antara - pallavi - charanam/antara - pallavi, often with a chorus answer. Arabic: madhhab (refrain) and kuplehs (verses) returning to the refrain. English: verse - pre-chorus - chorus - verse - chorus - bridge - chorus. For 60-90 s tracks: hook, one verse, hook, short bridge, hook.
- **Wordless sections stay wordless.** Humming, aalaap-like "aa" lines and chorus "oh-oh" are written as lines too (section 11), so the plan says exactly where the voice is.

## 4. How the words go into ElevenLabs Music

- Use a composition plan (`"plan"` in the track brief) so each section keeps its length. Sung words go into each section's `"lines"` list, one sung line per entry. Instrumental sections keep `"lines": []`.
- Set `"instrumental": false` in the brief, and do not put "lyrics", "vocals" or "singer" in `negative_global_styles`.
- Name the voice and language in `positive_global_styles` or the section's `positive_local_styles`: "warm male tenor singing in Malayalam with clear film-song diction", "soft close female voice singing in Urdu, ghazal phrasing", "group chorus answering in Telugu".
- **Script in `lines`:** write the native script (Malayalam, Tamil, Telugu, Devanagari, Urdu Nastaliq, Arabic with vowel marks). Keep the romanised line in the lyric sheet. If a take mispronounces the words or sings the wrong language, make the next take with the romanised lines and say the language in the styles ("sung in Tamil").
- Keep each line short (under about 60 characters). Repeat a hook by writing it again as its own line, not with "x2".
- Save the full lyric sheet next to the takes as `music/<track>/<track>-lyrics.md`: language and dialect, section names with times, each line in native script, romanised, and an English meaning. Copy the lines into the brief's plan.

## 5. Malayalam (മലയാളം)

- **Sound:** soft, flowing, many long vowels and doubled consonants (kk, tt, nn, ll). Special sounds: ഴ (zha), റ (rra), ള (lla). Words often end in -u (half-u, sung short), -am, -an, -al, -e. Sanskrit-rich words (chandrika, sandhya, hridayam) sound classical and tender; native words (mazha, kaattu, puzha, nila) sound earthy and warm. Mix both.
- **Meter:** classical vrittams (Keka, Kakali, Manjari) count syllables and long/short beats; film songs follow the tune but keep 2-beat word groups. Count aksharas: a short syllable is one, a long vowel or a syllable before a doubled consonant is two.
- **Rhyme:** the mark of Malayalam verse is **dvitiyakshara prasam**, the same consonant as the second syllable of each line (chaNDana / chaNDrika). Add end rhyme (antya prasam) on the hook. Alliteration across the line is a bonus.
- **Images that sing:** monsoon (mazha, idimin), backwaters (kaayal, thoni), moonlight (nilaavu), sandalwood, jasmine (mulla), temple-lamp light (deepam) used as a mood, not a ritual; nostalgia, the courtyard (muttam), first rain.
- **Diction:** keep words the singer can open: nee, njaan, ennum, ini. Avoid long agglutinated words on fast notes; split them across beats.
- Example (original, love song, 92 BPM, 2 lines = 2 phrases):
  - ചന്ദനക്കാറ്റിൽ നീ വന്നു / chandanakkaattil nee vannu / you came on the sandalwood breeze
  - ചന്ദ്രികപ്പൂവായ് നീ നിന്നു / chandrikappoovaay nee ninnu / you stood there, a moonlight flower
  - (prasam on "nd", end rhyme vannu / ninnu, open "oo" held on poovaay)

## 6. Tamil (தமிழ்)

- **Sound:** crisp and rhythmic, strong first syllables, retroflex ண, ட, ள, the special ழ (zha) and ற (rra). Written Tamil (sentamil) sounds lofty; spoken Chennai or Madurai Tamil sounds street and mass. Pick one for the song: literary for love and philosophy, colloquial for kuthu and mass.
- **Meter:** classical verse counts asai and seer (metrical feet); film songs fit the tune but love 2- and 4-syllable word blocks that ride the beat. Tamil words start strong, so put a word's first syllable on the beat.
- **Rhyme, three kinds:** **ethugai** (the same second letter at the start of each line: kaNNil / viNNil), **monai** (the same first sound at the start of words within a line: vinnil ... vaanavil), and **iyaibu** (end rhyme). A good Tamil hook uses at least two.
- **Images:** the village (oor), paddy fields, the temple tank, jasmine in the hair (malli), rain on red earth, the sea at Marina, the old cinema hall, mother's kitchen; for mass songs: the street, the crowd, fire, the drum.
- **Kuthu and mass hooks:** short repeated colloquial phrases, call and answer with the crowd ("hey!"), 4-6 syllables a second. Jithesh's rule: a Tamil dance hook needs real words or no words, never konnakol syllables sung as fake words.
- Example (original, love song):
  - கண்ணில் ஒரு மின்னல் வந்தது / kannil oru minnal vandhadhu / a flash of lightning came into my eyes
  - விண்ணில் ஒரு வானவில் நின்றது / vinnil oru vaanavil nindradhu / a rainbow stood still in the sky
  - (ethugai kaNNil / viNNil, monai vinnil / vaanavil, end rhyme -ndhadhu / -ndradhu)

## 7. Telugu (తెలుగు)

- **Sound:** almost every word ends in a vowel (it is called an "ajanta" language), which makes it one of the easiest languages in the world to sing; long notes come naturally. Classical words (Sanskrit-rich: hrudayam, swapnam) sound grand; everyday Telangana or Andhra words sound folk and playful.
- **Meter:** classical padyams use fixed meters (Utpalamala, Champakamala, Kandam, Ata Veladi); songs are freer but love even 4-syllable groups.
- **Rhyme:** **prasa** (the same second letter at the start of each line, as in Malayalam and Tamil), **yati** (the first letter of the line echoed at the middle of the line), and **antya prasa** (end rhyme), which film songs use most.
- **Images:** the Godavari and Krishna rivers, harvest festival (Sankranti) kites and rangoli, the village fair, mango groves, the first rain (tholakari), moonlit terraces; mass songs: the hero's walk, the dust, the drums.
- **Diction:** keep the endings full and sung (-aa, -ee, -oo, -ai), never clipped.
- Example (original, love song):
  - చిరునవ్వు ఒక చినుకై కురిసింది / chirunavvu oka chinukai kurisindi / your smile fell like a single raindrop
  - మనసంతా ఒక మెరుపై మెరిసింది / manasanthaa oka merupai merisindi / my whole heart flashed like lightning
  - (matching build "oka ...-ai", end rhyme kurisindi / merisindi)

## 8. Hindi (हिन्दी) and Urdu (اردو)

Spoken Hindi and Urdu are close; the writing, the formal words and the poetic forms differ. Choose one per song and stay in it.

**Hindi**
- **Sound:** clear vowels, aspirated consonants (kh, gh, chh, jh, th, dh, bh). Everyday Hindustani is best for film songs; Sanskrit-rich shuddh Hindi for devotional or grand songs; Bhojpuri, Awadhi or Rajasthani colour for folk.
- **Meter:** matra counting (laghu = 1 for a short vowel, guru = 2 for a long vowel or a syllable before a cluster). Classical chhands: doha (13 + 11 matras a half-line), chaupai (16 matras), sortha. Song lines usually keep the same matra count line to line.
- **Schwa:** the final "a" of most words is silent (kamal is sung "ka-mal", not "ka-ma-la"); count matras as sung.
- **Rhyme:** end rhyme on the hook and each antara's last line; a repeated refrain word (like a radif) works well.
- **Images:** rooftops and kites, the monsoon (saawan), the train window, the mela, mustard fields, the old haveli, chai stalls.
- Example (original):
  - धड़कन ने आज नया गीत गाया / dhadkan ne aaj naya geet gaaya / my heartbeat sang a new song today
  - बादल ने छत पे ये राज़ सुनाया / baadal ne chhat pe ye raaz sunaaya / the cloud told this secret on the rooftop
  - (end rhyme gaaya / sunaaya, open "aa" for the held note)

**Urdu**
- **Sound:** soft and refined, Persian and Arabic words, the nuqta sounds q, kh, gh, z, f (qamar, khwaab, ghazal, zindagi). Sing them correctly; ask for "clear Urdu diction" in the voice style.
- **Forms:** **ghazal** (independent couplets, sher), **nazm** (one theme, free or rhymed), **qawwali**-style refrains (keep secular unless the owner asks). A ghazal's first sher (matla) rhymes in both lines; every later sher rhymes in its second line.
- **Rhyme:** **qafiya** (the rhyme word: sajaaya / jagaaya) followed by the **radif** (the same word or words repeated after it: "hai"). Meter (bahr) is a fixed pattern of long and short syllables; keep every line to the same pattern.
- **Images:** the moon (chaand, mahtaab), the night (shab), the candle and the moth (shama, parwana), the tavern as a metaphor, the garden and the rose (gul, bulbul), separation (hijr), longing (aarzoo).
- Example (original matla, qafiya -aaya, radif "hai"):
  - رات نے چپکے سے اک خواب سجایا ہے / raat ne chupke se ik khwaab sajaaya hai / the night has quietly decorated a dream
  - تم نے آنکھوں میں نیا چاند جگایا ہے / tum ne aankhon mein naya chaand jagaaya hai / you have woken a new moon in my eyes

## 9. Arabic (العربية)

- **Choose the register first:** Modern Standard (fusha) for grand, poetic or pan-Arab songs; or one colloquial: Egyptian (the widest audience), Levantine (soft, romantic), Gulf (khaleeji rhythms) or Maghrebi. Never mix them in one song.
- **Sound:** long vowels (aa, ii, uu) carry the melody; emphatic consonants (ṣ, ḍ, ṭ, ẓ), the throat sounds ʿayn and ḥ, and the doubled consonant (shadda) give it its grip. Write full vowel marks (tashkeel) on the lyric lines so the singer reads every vowel.
- **Meter:** classical poems use the 16 buhur (al-Kamil, al-Wafir, al-Basit, al-Rajaz ...), fixed patterns of long and short syllables; songs often use al-Rajaz or al-Kamil-like 2-beat bounces. Keep the syllable count line to line.
- **Rhyme:** **monorhyme**: every line (or every second half-line) ends on the same rhyme letter (rawiy) and vowel, the whole song through: qamarī / saharī / naẓarī. The refrain (madhhab) can have its own rhyme.
- **Images:** the moon (qamar), the night (layl), the desert wind, the date palm, the sea and the port, the coffee pot as hospitality, the gazelle (ghazal) for beauty, the road home.
- **Rhythms the music can match:** maqsum (Egyptian 4/4), baladi, saidi, khaleeji 6/8 feel, dabke for line dancing.
- Example (original, fusha, rawiy ر + ī):
  - يَا قَمَرِي يَا سَهَرِي / yā qamarī yā saharī / my moon, my sleepless night
  - ضَوْءُكَ مَلَأَ نَظَرِي / ḍaw'uka mala'a naẓarī / your light has filled my sight

## 10. English

- **Meter:** stress-timed: count strong beats, not syllables. Iambs (da-DUM) feel natural and forward; trochees (DUM-da) feel like a chant or a march. Keep the number of strong beats per line steady (usually 3 or 4).
- **Rhyme:** perfect rhyme on the chorus (light / night), slant rhyme in verses (home / alone). Schemes: AABB for bounce, ABAB for story, XAXA for a ballad.
- **Write images, not labels.** "I kept your jacket on the chair" beats "I miss you so much". Avoid worn-out lines: "fire / desire", "heart / apart", "stars align", "dancing in the rain".
- **Indian-English and global flavour:** for a global audience, one line in an Indian language inside an English chorus is a strong hook; the music stays South Indian in style (indian-touch rule).
- Example (original):
  - I saw you once by the station light, / the whole grey town turned gold tonight.

## 11. Vocables and gibberish (singable sounds, no meaning)

- **When:** a chorus hook for a global track, a humming line (the owner loves soft wordless female humming), a crowd chant over a dance groove, or a scat line over a fast section.
- **Build them from open syllables:** a consonant + a long vowel (la, na, ta, ra, ho, yo, mm, aa, ee, oo). 2-4 syllable cells, repeated with one change each time: "na-na ho, na-na hey".
- **Give them a flavour:** soft Dravidian (thaa-na, nee-ra-la, oyy-a), Arabic-desert (ya-la-li, ha-bi-yo), Celtic-folk (lo-ra-dee), cinematic choir (ah, oh, oo-ah). Pick one flavour per song.
- **Humming lines:** write them as lines: "mm-mm-mm, mm-mmm", "aa-aa-aa", "oo-oo, oo-ooo". Say "soft close wordless female humming" in the styles.
- **Never:** sacred syllables (Om, Allah hu, Hari, Amen, Hallelujah), konnakol or sargam syllables passed off as words (owner's rule), or any cell that is a real word with a rude or silly meaning in Malayalam, Tamil, Telugu, Hindi, Urdu, Arabic or English. Check every cell before using it.
- Example (original, soft Dravidian flavour, every cell checked harmless):
  - ae-lo va-ri, sa-ma do-ri / ha-ni yo-ma, la-ya ta-ri / mm-mm-mm, mm-mmm

## 12. The lyric sheet Mr. Kavi returns

```
Track: <name>   Language: <language, dialect>   Voice: <voice and diction>
Hook: <the hook line> (<meaning>)
[Section name, start-end s, BPM, syllables per line]
<native script line>
<romanised line>
(<English meaning>)
...
Notes for Mr. Raga: where the hook repeats, which line holds the long note, any section that needs more or fewer bars.
```
