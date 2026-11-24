"""Front-page generator for the make.fun bounty "Sum up 24 November's world news in one image".

Renders a 1024x1024 newspaper front page: masthead with the date, a red deck of the
three leads, region chips, a UTC rail, three lead cards with flat vector art, a
numbers sidebar, two rows of five mini cards, a numbered briefs block, a dot-matrix
world map with story pins, and a "date check" footer.

Everything is drawn with Pillow from the data tables below; there are no photographs
and no network calls. Run it with:

    python3 make_poster.py            # writes poster.png beside this file

The entry itself (main.ts) only copies poster.png to the output directory, so the
image must be committed with the repository.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 22                      # page margin
CW = W - 2 * M              # content width

PAPER = (246, 242, 234)
INK = (20, 18, 16)
GREY = (108, 102, 94)
NAVY = (27, 42, 74)
RED = (194, 27, 44)
AMBER = (224, 123, 57)
GREEN = (31, 122, 63)
HAIR = (30, 28, 26)

SERIF_B = "/system/fonts/NotoSerif-Bold.ttf"
SERIF_R = "/system/fonts/NotoSerif-Regular.ttf"
SERIF_I = "/system/fonts/NotoSerif-Italic.ttf"
SANS_B = "/system/fonts/BarlowSemiCondensed-Bold.ttf"
SANS_R = "/system/fonts/BarlowSemiCondensed-Regular.ttf"

REGION = {
    "EUROPE": (31, 95, 168),
    "MIDEAST": (194, 27, 44),
    "AFRICA": (201, 138, 43),
    "ASIA": (122, 62, 142),
    "AMERICAS": (75, 46, 107),
    "OCEANIA": (30, 110, 140),
    "WORLD": (27, 42, 74),
}
REGION_ORDER = ["EUROPE", "MIDEAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]
REGION_LABEL = {
    "EUROPE": "EUROPE", "MIDEAST": "MIDDLE EAST", "AFRICA": "AFRICA",
    "ASIA": "ASIA", "AMERICAS": "AMERICAS", "OCEANIA": "OCEANIA", "WORLD": "WORLD",
}

EDITION = "Tuesday 24 November 2026"
VOLUME = "VOL. IV   No. 329"
DECK = ("Three tankers burn in the Strait of Hormuz · COP31 ends with no pact · "
        "Nvidia reinstates Jensen Huang")

# ---------------------------------------------------------------- the stories ---
# One tuple per story: number, place, kicker, headline, body, source, region,
# status, art, latitude, longitude.

LEADS = [
    dict(
        n=1, place="STRAIT OF HORMUZ", kicker="MIDDLE EAST \u00b7 SHIPPING",
        head="Three oil tankers burn after mines strike them in the strait",
        body=("Iran's Revolutionary Guard navy said two tankers hit naval mines in the "
              "eastern strait and fires broke out on all three. It said US air cover had "
              "not prevented the blasts."),
        src="IRGC statement \u00b7 Reuters",
        region="MIDEAST", status="CLAIM", art="tanker", lat=26.6, lon=56.4,
    ),
    dict(
        n=2, place="ANTALYA, T\u00dcRKIYE", kicker="WORLD \u00b7 CLIMATE",
        head="COP31 ends in overtime with no deal on fossil fuels",
        body=("Two days past its deadline, the UN climate summit closed without a text "
              "naming coal, oil and gas. Delegates left a package that keeps the 1.5C "
              "goal but sets no route to it."),
        src="UN News \u00b7 Reuters",
        region="WORLD", status="REPORTED", art="talks", lat=36.9, lon=30.7,
    ),
    dict(
        n=3, place="NEW YORK, UNITED STATES", kicker="AMERICAS \u00b7 MARKETS",
        head="Nvidia brings Jensen Huang back as chief executive",
        body=("The board reinstated him unanimously after talks with the White House. "
              "The Nasdaq jumped 7% and the S&P 500 climbed out of a correction as "
              "AI-linked shares rallied."),
        src="Nvidia statement \u00b7 Dawn \u00b7 AP",
        region="AMERICAS", status="REPORTED", art="chart", lat=40.7, lon=-74.0,
    ),
]

CARDS = [
    dict(
        n=4, place="KYIV, UKRAINE", kicker="EUROPE \u00b7 WAR",
        head="Zelenskyy warns of new Russian strikes and asks for Patriots",
        body="Intelligence has detected preparations for fresh attacks, he said.",
        region="EUROPE", status="REPORTED", art="drone", lat=50.4, lon=30.5,
    ),
    dict(
        n=5, place="ZAPORIZHZHIA", kicker="EUROPE \u00b7 WAR",
        head="Two killed, 22 hurt as a missile hits a five-storey block",
        body="The Kosmichnyi district building was partly destroyed.",
        region="EUROPE", status="REPORTED", art="rubble", lat=47.8, lon=35.2,
    ),
    dict(
        n=6, place="HODEIDAH, YEMEN", kicker="MIDDLE EAST \u00b7 CONFLICT",
        head="Air strikes on a telecoms hub kill 17 workers",
        body="Houthi media blamed Saudi warplanes; 11 more were wounded.",
        region="MIDEAST", status="CLAIM", art="strike", lat=14.8, lon=42.9,
    ),
    dict(
        n=7, place="KHAN YOUNIS, GAZA", kicker="MIDDLE EAST \u00b7 CONFLICT",
        head="Drone strike on a police post kills three Palestinians",
        body="Five more were wounded in al-Mawasi, Nasser Hospital said.",
        region="MIDEAST", status="REPORTED", art="drone", lat=31.4, lon=34.3,
    ),
    dict(
        n=8, place="BANTEN, INDONESIA", kicker="ASIA \u00b7 DISASTER",
        head="Candy factory fire toll reaches 24 dead, about 30 missing",
        body="Rescuers kept searching the plant; a short circuit is suspected.",
        region="ASIA", status="ONGOING", art="factory", lat=-6.2, lon=106.8,
    ),
    dict(
        n=9, place="KANNAUJ, INDIA", kicker="ASIA \u00b7 ROADS",
        head="Four school students killed as a truck hits their bus",
        body="About 35 were injured on the Agra-Lucknow expressway.",
        region="ASIA", status="REPORTED", art="crash", lat=27.0, lon=79.9,
    ),
    dict(
        n=10, place="KHARTOUM, SUDAN", kicker="AFRICA \u00b7 CONFLICT",
        head="UN condemns drone strikes on the capital blamed on Ethiopia",
        body="A UN building was among the structures damaged overnight.",
        region="AFRICA", status="CLAIM", art="strike", lat=15.6, lon=32.5,
    ),
    dict(
        n=11, place="UGHELLI, NIGERIA", kicker="AFRICA \u00b7 POLITICS",
        head="Gunmen fire on a senate campaign; Delta imposes a curfew",
        body="Four died in the attack on Ovie Omo-Agege's convoy.",
        region="AFRICA", status="CLAIM", art="megaphone", lat=5.5, lon=5.9,
    ),
    dict(
        n=12, place="PRETORIA, SOUTH AFRICA", kicker="AFRICA \u00b7 COURTS",
        head="Judgment due on 3 December in Mapisa-Nqakula bribery trial",
        body="The former speaker denies soliciting R4.5m from a contractor.",
        region="AFRICA", status="REPORTED", art="gavel", lat=-25.7, lon=28.2,
    ),
    dict(
        n=13, place="MANCHESTER, UNITED KINGDOM", kicker="EUROPE \u00b7 DISASTER",
        head="12,000 evacuated from an arena after a substance is released",
        body="Police cleared Co-op Live during a concert; nobody was hurt badly.",
        region="EUROPE", status="REPORTED", art="concert", lat=53.5, lon=-2.2,
    ),
    dict(
        n=14, place="BERLIN, GERMANY", kicker="EUROPE \u00b7 SECURITY",
        head="Hundreds of schools get bomb threats across the country",
        body="Some were evacuated; police found no concrete danger.",
        region="EUROPE", status="REPORTED", art="school", lat=52.5, lon=13.4,
    ),
    dict(
        n=15, place="SEOUL, SOUTH KOREA", kicker="ASIA \u00b7 DEFENCE",
        head="Fighter jets scramble as Russian aircraft enter the ADIZ",
        body="The incursion over the East Sea was tracked by Yonhap.",
        region="ASIA", status="REPORTED", art="jet", lat=37.6, lon=127.0,
    ),
    dict(
        n=16, place="DUBAI, UNITED ARAB EMIRATES", kicker="MIDDLE EAST \u00b7 ROADS",
        head="Bus and truck collide, killing 11 people",
        body="The interior ministry said the cause is under investigation.",
        region="MIDEAST", status="REPORTED", art="crash", lat=25.2, lon=55.3,
    ),
    dict(
        n=17, place="TEHRAN, IRAN", kicker="MIDDLE EAST \u00b7 SANCTIONS",
        head="Iran vows to use 'all available tools' against the US blockade",
        body="Tehran called the naval blockade of its oil exports intolerable.",
        region="MIDEAST", status="CLAIM", art="tanker", lat=35.7, lon=51.4,
    ),
    dict(
        n=18, place="WASHINGTON, UNITED STATES", kicker="AMERICAS \u00b7 COURTS",
        head="Appeals court opens a path to erasing the hush-money conviction",
        body="The case moves to a federal court where immunity can be argued.",
        region="AMERICAS", status="REPORTED", art="gavel", lat=38.9, lon=-77.0,
    ),
    dict(
        n=19, place="HONIARA, SOLOMON ISLANDS", kicker="OCEANIA \u00b7 SECURITY",
        head="Sogavare warns against dropping the China security pact",
        body="Wale flies to Canberra to sign a treaty with Australia.",
        region="OCEANIA", status="CLAIM", art="talks", lat=-9.4, lon=159.9,
    ),
    dict(
        n=20, place="PAGO PAGO, AMERICAN SAMOA", kicker="OCEANIA \u00b7 MINING",
        head="31.5m acres of seabed leased for deep-sea exploration",
        body="The $6m sale came days after a judge ruled the auction unlawful.",
        region="OCEANIA", status="REPORTED", art="sea", lat=-14.3, lon=-170.7,
    ),
]

# (number, place, headline, region, lat, lon) — numbered on from the cards above
BRIEFS = [
    (21, "NEW YORK", "US-led bid wins the 2031 Women's World Cup", "WORLD", 40.7, -74.0),
    (22, "ZURICH", "Britain confirmed as host of the 2035 edition", "EUROPE", 47.4, 8.5),
    (23, "GENEVA", "Russia and Ukraine clash at the UN over Black Sea shipping", "EUROPE", 46.2, 6.1),
    (24, "MOSCOW", "Kremlin rules out reviving the grain deal", "EUROPE", 55.8, 37.6),
    (25, "TRIPOLI", "Ukrainian naval drones sink Russian warships off Libya", "AFRICA", 32.9, 13.2),
    (26, "JOHANNESBURG", "2,517 rescued from floods as storms hit Gauteng", "AFRICA", -26.2, 28.0),
    (27, "DHAKA", "Hasina sets 16 December for her return from exile", "ASIA", 23.8, 90.4),
    (28, "TEHRAN", "Singer Parastoo Ahmadi is given 74 lashes over a performance", "MIDEAST", 35.7, 51.4),
    (29, "NEW DELHI", "Supreme Court issues notice on judges' appointment", "ASIA", 28.6, 77.2),
    (30, "BEIJING", "Xi weighs what Huang's return means for Nvidia in China", "ASIA", 39.9, 116.4),
    (31, "IOWA", "Court clears the Army to detonate degraded munitions", "AMERICAS", 42.0, -93.5),
    (32, "SUVA", "World Rugby suspends Oceania Rugby from its council", "OCEANIA", -18.1, 178.4),
]

STATS = [
    ("3", "TANKERS ABLAZE", "mines in the Hormuz strait"),
    ("24", "DEAD, BANTEN FACTORY", "about 30 still missing"),
    ("17", "KILLED, HODEIDAH", "strike on a telecoms hub"),
    ("7%", "NASDAQ JUMP", "after Huang returns"),
    ("2", "DAYS OF COP OVERTIME", "no deal on fossil fuels"),
]

EXCLUDED = [
    "Boca Juniors 2-0 Mineiro (22 Nov)",
    "Kansas City win the NWSL final (22 Nov)",
    "El Chapo Isidro captured in Sinaloa (22 Nov)",
    "Peru magnitude-6.7 quake (22 Nov)",
    "Liverpool 4-0 Manchester United (22 Nov)",
    "Verstappen wins in Las Vegas (22 Nov)",
]

CARDS_SELECTED = [c for c in CARDS if c["n"] in (5, 13, 6, 7, 8, 9, 10, 11, 19, 18)]
BRIEFS_SELECTED = BRIEFS[:16]

# Short place labels for the card tabs: what fits in a narrow tab without being
# cut mid-word. Full place names stay in the data above.
SHORT_PLACE = {
    "STRAIT OF HORMUZ": "HORMUZ",
    "ANTALYA, T\u00dcRKIYE": "ANTALYA",
    "NEW YORK, UNITED STATES": "NEW YORK",
    "KYIV, UKRAINE": "KYIV",
    "ZAPORIZHZHIA": "ZAPORIZHZHIA",
    "HODEIDAH, YEMEN": "HODEIDAH",
    "KHAN YOUNIS, GAZA": "KHAN YOUNIS",
    "BANTEN, INDONESIA": "BANTEN",
    "KANNAUJ, INDIA": "KANNAUJ",
    "KHARTOUM, SUDAN": "KHARTOUM",
    "UGHELLI, NIGERIA": "UGHELLI",
    "PRETORIA, SOUTH AFRICA": "PRETORIA",
    "MANCHESTER, UNITED KINGDOM": "MANCHESTER",
    "BERLIN, GERMANY": "BERLIN",
    "SEOUL, SOUTH KOREA": "SEOUL",
    "DUBAI, UNITED ARAB EMIRATES": "DUBAI",
    "TEHRAN, IRAN": "TEHRAN",
    "WASHINGTON, UNITED STATES": "WASHINGTON",
    "HONIARA, SOLOMON ISLANDS": "HONIARA",
    "PAGO PAGO, AMERICAN SAMOA": "PAGO PAGO",
}
