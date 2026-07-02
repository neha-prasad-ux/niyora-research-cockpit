"""Research lane config for the Niyora bank.

Each lane = a Europe PMC query + its axis + tags + a per-lane cap.
Axes: core | modulator | impact | context
Tags carry cross-cutting meaning (mechanism, safety, gap-map, myth-bust, needs-triage...).
Firehose lanes (hormonal, reproductive, environmental) are anchored to mood/premenstrual
so they return the relevant slice, not general endocrinology.
"""

LANES = [
    # ---- CORE (the subject) ----
    ("PMS", "core", 'TITLE_ABS:"premenstrual syndrome"', 80, "pms"),
    ("PMDD", "core", 'TITLE_ABS:"premenstrual dysphoric disorder"', 80, "pmdd"),
    ("Symptoms / cycle mood", "core",
     'TITLE_ABS:premenstrual AND TITLE_ABS:(mood OR irritability OR anxiety OR symptom)', 80, "symptoms"),

    # ---- MODULATORS (why yours differs -> personalization) ----
    ("Hormonal", "modulator",
     'TITLE_ABS:(premenstrual OR luteal) AND TITLE_ABS:(estrogen OR progesterone OR allopregnanolone) AND TITLE_ABS:(mood OR symptom OR anxiety OR depression)',
     80, "hormonal,mechanism"),
    ("Reproductive physiology", "modulator",
     'TITLE_ABS:(ovarian OR uterus OR endometrium) AND TITLE_ABS:(brain OR neural OR "nervous system") AND TITLE_ABS:(mood OR premenstrual OR menstrual)',
     60, "reproductive,mechanism"),
    ("Nutrition", "modulator",
     'TITLE_ABS:(premenstrual OR "menstrual cycle") AND TITLE_ABS:(diet OR nutrition OR calcium OR magnesium OR vitamin)',
     80, "nutrition"),
    ("Genetic", "modulator",
     'TITLE_ABS:premenstrual AND TITLE_ABS:(genetic OR heritability OR gene OR GWAS)', 100, "genetics,gap-map"),
    ("Ethnic / cultural", "modulator",
     'TITLE_ABS:premenstrual AND TITLE_ABS:(ethnic OR cultural OR "cross-cultural" OR socioeconomic OR race)',
     100, "ethnic,gap-map,flag-confounded"),
    ("Geographical", "modulator",
     'TITLE_ABS:"premenstrual syndrome" AND TITLE_ABS:prevalence AND TITLE_ABS:(country OR geographical OR region OR global)',
     100, "geographical,gap-map"),
    ("Seasonal", "modulator",
     'TITLE_ABS:(premenstrual OR menstrual) AND TITLE_ABS:(seasonal OR season OR "light therapy" OR photoperiod)',
     80, "seasonal,gap-map"),
    ("Environmental", "modulator",
     'TITLE_ABS:(premenstrual OR menstrual) AND TITLE_ABS:("endocrine disruptor" OR pollution OR phthalate OR BPA) AND TITLE_ABS:(mood OR symptom OR premenstrual)',
     60, "environmental,gap-map,needs-triage"),
    ("Occupational", "modulator",
     'TITLE_ABS:(premenstrual OR menstrual) AND TITLE_ABS:("shift work" OR occupational OR "work stress" OR nurses)',
     60, "occupational,gap-map"),
    ("Relationship status", "modulator",
     'TITLE_ABS:premenstrual AND TITLE_ABS:(marital OR partner OR married OR "relationship status")',
     100, "relationship-status,gap-map"),
    ("Inflammation", "modulator",
     'TITLE_ABS:(premenstrual OR luteal OR "menstrual cycle") AND TITLE_ABS:(inflammation OR inflammatory OR "C-reactive protein" OR CRP OR cytokine OR interleukin OR TNF)',
     80, "inflammation,mechanism"),
    ("Insulin resistance", "modulator",
     'TITLE_ABS:(premenstrual OR luteal OR "menstrual cycle") AND TITLE_ABS:("insulin resistance" OR insulin OR HOMA OR glycemic OR glucose OR "blood sugar")',
     80, "insulin-resistance,metabolic,mechanism"),

    # ---- IMPACTS (why it matters -> motivation + safety) ----
    ("Confidence / self-esteem", "impact",
     'TITLE_ABS:premenstrual AND TITLE_ABS:("self-esteem" OR "self esteem" OR confidence)', 100, "confidence,gap-map"),
    ("Self-harm / suicidality", "impact",
     'TITLE_ABS:(premenstrual OR PMDD) AND TITLE_ABS:(suicide OR suicidal OR "self-harm" OR "self harm")',
     100, "safety"),
    ("Relationships / partners", "impact",
     'TITLE_ABS:premenstrual AND TITLE_ABS:(relationship OR marital OR interpersonal OR conflict)', 80, "relationships"),
    ("Workplace / productivity", "impact",
     'TITLE_ABS:(premenstrual OR menstrual) AND TITLE_ABS:(workplace OR productivity OR absenteeism OR presenteeism OR "work performance")',
     80, "workplace"),

    # ---- CONTEXT / WONDER (content fuel) ----
    ("History of PMS", "context",
     'TITLE_ABS:(premenstrual OR menstrual) AND TITLE_ABS:(history OR historical OR medicalization OR "cultural history")',
     80, "context,history"),
    ("PMS in animals", "context",
     'TITLE_ABS:(premenstrual OR "luteal phase" OR "menstrual cycle") AND TITLE_ABS:(nonhuman OR primate OR macaque OR baboon OR animal OR mammal)',
     80, "context,animals"),
    ("Evolution of menstruation", "context",
     'TITLE_ABS:(menstruation OR premenstrual) AND TITLE_ABS:(evolution OR evolutionary OR adaptive OR "spontaneous decidualization")',
     100, "context,evolution,contested"),
    ("Menstrual synchrony (myth)", "context",
     'TITLE_ABS:("menstrual synchrony" OR "menstrual synchronization")', 100, "context,myth-bust"),
    ("Lunar / moon myth", "context",
     'TITLE_ABS:(menstrual OR menstruation) AND TITLE_ABS:(lunar OR moon)', 100, "context,myth-bust"),
    ("Positive / luteal upside", "context",
     'TITLE_ABS:("menstrual cycle" OR luteal) AND TITLE_ABS:(creativity OR cognitive OR olfaction OR sensory OR positive)',
     80, "context,counter-narrative,needs-triage"),
    ("Gut microbiome x cycle", "context",
     'TITLE_ABS:(menstrual OR estrogen OR premenstrual) AND TITLE_ABS:(microbiome OR microbiota OR gut OR estrobolome)',
     60, "context,emerging"),
    ("Pain across cycle", "context",
     'TITLE_ABS:("menstrual cycle" OR luteal OR premenstrual) AND TITLE_ABS:(pain OR "pain threshold" OR nociception)',
     60, "context"),
    ("Sleep / dreams across cycle", "context",
     'TITLE_ABS:(premenstrual OR "menstrual cycle" OR luteal) AND TITLE_ABS:(sleep OR insomnia OR dream)', 60, "context,sleep"),
    ("Cravings science", "context",
     'TITLE_ABS:(premenstrual OR menstrual) AND TITLE_ABS:(craving OR chocolate OR appetite OR carbohydrate)', 60, "context,myth-nuance"),
    ("Athletes / performance", "context",
     'TITLE_ABS:("menstrual cycle" OR luteal) AND TITLE_ABS:(athlete OR "sports performance" OR "exercise performance" OR training)',
     60, "context,trendy"),
    ("Spending / decisions", "context",
     'TITLE_ABS:("menstrual cycle" OR luteal OR premenstrual) AND TITLE_ABS:(spending OR financial OR "decision making" OR "risk taking")',
     100, "context"),
]

AXIS_ORDER = ["core", "modulator", "impact", "context"]
