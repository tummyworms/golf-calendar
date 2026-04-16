from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
import json, os, re
from datetime import date, timedelta
from dateutil import parser as dateparser

app = Flask(__name__)

EVENTS_FILE   = os.path.join(os.path.dirname(__file__), 'data', 'events.json')
UPCOMING_FILE = os.path.join(os.path.dirname(__file__), 'data', 'upcoming.json')

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ── Courses  (only verified real websites) ────────────────────────────────────
# lat/lng used for the map
COURSES = [
    {
        "id": "3_lakes",
        "name": "3 Lakes Golf Course",
        "address": "6700 Saltsburg Rd, Pittsburgh, PA 15235",
        "phone": "(412) 793-7111",
        "website": "https://3lakesgolf.com/",
        "tee_time_url": "https://www.chronogolf.com/club/3-lakes-golf-course",
        "lat": 40.4592, "lng": -79.8312,
    },
    {
        "id": "boyce_park",
        "name": "Boyce Park Golf Course",
        "address": "Duff Road, Plum, PA 15239",
        "phone": "(724) 733-4656",
        "website": "https://www.golfalleghenycounty.com/",
        "tee_time_url": "https://www.golfalleghenycounty.com/",
        "lat": 40.4914, "lng": -79.7609,
    },
    {
        "id": "north_park",
        "name": "North Park Golf Course",
        "address": "Pearce Mill Rd, Allison Park, PA 15101",
        "phone": "(724) 935-1967",
        "website": "https://www.golfalleghenycounty.com/",
        "tee_time_url": "https://www.golfalleghenycounty.com/",
        "lat": 40.5738, "lng": -79.9826,
    },
    {
        "id": "south_park",
        "name": "South Park Golf Course",
        "address": "Buffalo Drive, Library, PA 15129",
        "phone": "(412) 835-3545",
        "website": "https://www.golfalleghenycounty.com/",
        "tee_time_url": "https://www.golfalleghenycounty.com/",
        "lat": 40.3054, "lng": -80.0199,
    },
    {
        "id": "meadowink",
        "name": "Meadowink Golf Course",
        "address": "4076 Bulltown Rd, Murrysville, PA 15668",
        "phone": "(724) 327-8243",
        "website": "https://www.meadowinkgolf.com/",
        "tee_time_url": "https://www.meadowinkgolf.com/",
        "lat": 40.4478, "lng": -79.6618,
    },
    {
        "id": "murrysville_gc",
        "name": "Murrysville Golf Club",
        "address": "3804 Sardis Rd, Murrysville, PA 15668",
        "phone": "(724) 327-0726",
        "website": "https://www.724golf.com/",
        "tee_time_url": "https://www.724golf.com/",
        "lat": 40.4524, "lng": -79.6794,
    },
    {
        "id": "rolling_fields",
        "name": "Rolling Fields Golf Club",
        "address": "4138 Hankey Church Rd, Murrysville, PA 15668",
        "phone": "(724) 204-2626",
        "website": "https://www.rollingfieldsgolfclub.com/",
        "tee_time_url": "https://www.rollingfieldsgolfclub.com/",
        "lat": 40.4599, "lng": -79.6571,
    },
    {
        "id": "grand_view",
        "name": "Grand View Golf Club",
        "address": "1000 Clubhouse Dr, North Braddock, PA 15104",
        "phone": "(412) 351-5390",
        "website": "https://pittsburghgolf.com/",
        "tee_time_url": "https://www.chronogolf.com/club/grand-view-golf-club-pennsylvania",
        "lat": 40.4013, "lng": -79.8619,
    },
    {
        "id": "westwood",
        "name": "Westwood Golf Club",
        "address": "825 Commonwealth Ave, West Mifflin, PA 15122",
        "phone": "(412) 462-9555",
        "website": "https://www.golfnow.com/tee-times/facility/3952-westwood-golf-club/search",
        "tee_time_url": "https://www.golfnow.com/tee-times/facility/3952-westwood-golf-club/search",
        "lat": 40.3612, "lng": -79.9064,
    },
    {
        "id": "butlers",
        "name": "Butler's Golf Course",
        "address": "800 Rock Run Rd, Elizabeth, PA 15037",
        "phone": "(412) 751-9121",
        "website": "https://www.butlersgolf.com/",
        "tee_time_url": "https://www.butlersgolf.com/golf/tee-times",
        "lat": 40.2758, "lng": -79.8901,
    },
    {
        "id": "glengarry",
        "name": "Glengarry Golf Links",
        "address": "117 Glengarry Dr, Tarentum, PA 15084",
        "phone": "(724) 274-4659",
        "website": "https://www.glengarrygolflinks.com/",
        "tee_time_url": "https://www.glengarrygolflinks.com/",
        "lat": 40.6062, "lng": -79.7398,
    },
    {
        "id": "diamond_run",
        "name": "Diamond Run Golf Club",
        "address": "100 Diamond Run Blvd, Sewickley, PA 15143",
        "phone": "(412) 749-0600",
        "website": "https://www.diamondrungolf.com/",
        "tee_time_url": "https://www.diamondrungolf.com/",
        "lat": 40.5382, "lng": -80.1738,
    },
    {
        "id": "maple_crest",
        "name": "Maple Crest Golf Course",
        "address": "Monroeville, PA 15146",
        "phone": "",
        "website": "https://www.golfnow.com/courses/1036039-maple-crest-golf-course-details",
        "tee_time_url": "https://www.golfnow.com/courses/1036039-maple-crest-golf-course-details",
        "lat": 40.4229, "lng": -79.7795,
    },
    {
        "id": "lindenwood",
        "name": "Lindenwood Golf Club",
        "address": "1003 N Race Track Rd, Canonsburg, PA 15317",
        "phone": "(724) 745-9889",
        "website": "https://www.lindenwoodgolf.com/",
        "tee_time_url": "https://lindenwood-golf-club.book.teeitup.com/",
        "lat": 40.2567, "lng": -80.1826,
    },
    {
        "id": "quicksilver",
        "name": "Quicksilver Golf Club",
        "address": "2000 Quicksilver Rd, Midway, PA 15060",
        "phone": "(724) 796-1594",
        "website": "https://www.quicksilvergolf.com/",
        "tee_time_url": "https://www.golfnow.com/tee-times/facility/10124-quicksilver-golf-club/search",
        "lat": 40.3668, "lng": -80.2679,
    },
    {
        "id": "cranberry_highlands",
        "name": "Cranberry Highlands Golf Course",
        "address": "5190 Poplar Dr, Cranberry Township, PA 16066",
        "phone": "(724) 776-8189",
        "website": "https://www.cranberryhighlandsgolf.com/",
        "tee_time_url": "https://www.cranberryhighlandsgolf.com/",
        "lat": 40.6876, "lng": -80.1063,
    },
    {
        "id": "yough_cc",
        "name": "Youghiogheny Country Club",
        "address": "Elizabeth Township, PA 15037",
        "phone": "(412) 384-7518",
        "website": "https://www.youghioghenycountryclub.com/",
        "tee_time_url": "https://www.youghioghenycountryclub.com/",
        "lat": 40.2943, "lng": -79.8664,
    },
    {
        "id": "green_oaks",
        "name": "Green Oaks Country Club",
        "address": "Verona, PA 15147",
        "phone": "(412) 793-0259",
        "website": "https://www.greenoakscc.com/",
        "tee_time_url": "https://www.greenoakscc.com/",
        "lat": 40.5085, "lng": -79.8391,
    },
]

# ── Data helpers ──────────────────────────────────────────────────────────────

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

def next_id(events):
    ids = [e.get("id", 0) for e in events if isinstance(e.get("id"), int)]
    return max(ids, default=0) + 1

# ── 3 Lakes scraper — uses their verified WordPress REST API ──────────────────
SKIP_3LAKES = [
    "closed", "food truck", "bar at the pavilion", "bar opens", "open interviews",
    "rates begin", "daylight savings", "cancelled", "vets, police",
    "junior league", "junior clinic", "get golf ready", "women's group golf clinic",
    "league kickoff", "resurrection sunday", "easter", "zeus bbq", "pastrami",
    "passholder appreciation",  # members-only
]

def scrape_3lakes():
    """Fetch events from 3 Lakes Golf Course via their WordPress REST API."""
    events = []
    url = (
        "https://3lakesgolf.com/wp-json/tribe/events/v1/events"
        f"?per_page=100&start_date={date.today().isoformat()}"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for ev in data.get("events", []):
            title = ev.get("title", "").strip()
            if not title:
                continue
            if any(s in title.lower() for s in SKIP_3LAKES):
                continue
            raw_start = ev.get("start_date", "")
            parsed_date, time_str = None, ""
            if raw_start:
                try:
                    dt = dateparser.parse(raw_start)
                    parsed_date = dt.date().isoformat()
                    time_str = dt.strftime("%-I:%M %p")
                except Exception:
                    pass
            if not parsed_date:
                continue
            desc_html = ev.get("description", "") or ""
            desc = BeautifulSoup(desc_html, "lxml").get_text(" ", strip=True)[:200]
            events.append({
                "title": title,
                "course": "3 Lakes Golf Course",
                "address": "6700 Saltsburg Rd, Pittsburgh, PA 15235",
                "date": parsed_date,
                "time": time_str,
                "description": desc or "Public event at 3 Lakes Golf Course.",
                "event_url": ev.get("url", "https://3lakesgolf.com/events/"),
                "tee_time_url": "https://www.chronogolf.com/club/3-lakes-golf-course",
                "source": "3lakes_scrape",
                "type": "outing",
            })
        print(f"[3lakes] {len(events)} events scraped")
    except Exception as exc:
        print(f"[3lakes] scrape error: {exc}")
    return events


# ── Butler's calendar scraper — fetches HTML calendar page ────────────────────
SKIP_BUTLERS = [
    "aerification", "fitting", "burgercraft", "pizza =", "patio party",
    "memorial day", "good friday", "between two rivers", "bp acoustics",
    "acoustic fingers", "regular joes", "sarah williams",
]

def scrape_butlers_month(month, year):
    """Scrape one month from Butler's Golf Course HTML event calendar."""
    events = []
    url = f"https://www.butlersgolf.com/events/calendar?month={month}&year={year}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "lxml")
        for ev in soup.select(
            "article.type-tribe_events, "
            ".tribe-events-calendar-list__event, "
            "li.tribe_events_cat"
        ):
            title_el = ev.select_one(
                ".tribe-event-url, .tribe-events-list-event-title a, h2 a, h3 a"
            )
            date_el = ev.select_one(
                "abbr.tribe-events-abbr, time[datetime], "
                ".tribe-event-date-start, .tribe-events-start-datetime"
            )
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if any(s in title.lower() for s in SKIP_BUTLERS):
                continue
            raw_date = None
            if date_el:
                raw_date = (date_el.get("datetime") or date_el.get("title")
                            or date_el.get_text(strip=True))
            parsed_date = None
            if raw_date:
                try:
                    parsed_date = dateparser.parse(raw_date, fuzzy=True).date().isoformat()
                except Exception:
                    pass
            if not parsed_date:
                continue
            link_el = ev.select_one("a[href]")
            href = link_el["href"] if link_el else "https://www.butlersgolf.com/events/calendar"
            time_el = ev.select_one(".tribe-events-start-datetime, .tribe-event-time, time")
            time_str = ""
            if time_el:
                m = re.search(r'\d{1,2}:\d{2}\s*[AP]M', time_el.get_text(), re.IGNORECASE)
                if m:
                    time_str = m.group(0)
            events.append({
                "title": title,
                "course": "Butler's Golf Course",
                "address": "800 Rock Run Rd, Elizabeth, PA 15037",
                "date": parsed_date,
                "time": time_str,
                "description": "Public golf outing on Butler's official event calendar.",
                "event_url": href,
                "tee_time_url": "https://www.butlersgolf.com/golf/tee-times",
                "source": "butlers_scrape",
                "type": "outing",
            })
    except Exception as exc:
        print(f"[butlers] {month}/{year} error: {exc}")
    return events


def run_scrape():
    """Scrape both 3 Lakes (REST API) and Butler's (HTML calendar)."""
    scraped = []

    # 3 Lakes via REST API
    scraped += scrape_3lakes()

    # Butler's via HTML calendar for next 7 months
    today = date.today()
    for delta in range(7):
        d = today.replace(day=1) + timedelta(days=delta * 31)
        scraped += scrape_butlers_month(d.month, d.year)

    existing = load_json(EVENTS_FILE)
    manual   = [e for e in existing if e.get("source") == "manual"]

    seen, unique = set(), []
    for ev in scraped:
        key = (ev["title"].lower().strip(), ev["date"])
        if key not in seen:
            seen.add(key)
            unique.append(ev)

    counter = max([e.get("id", 0) for e in manual] or [0]) + 1
    for ev in unique:
        ev["id"] = counter; counter += 1

    merged = manual + unique
    save_json(EVENTS_FILE, merged)
    print(f"[scrape] {len(unique)} total scraped + {len(manual)} manual = {len(merged)}")
    return merged

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", courses=COURSES)

@app.route("/api/events")
def get_events():
    events = load_json(EVENTS_FILE)
    events.sort(key=lambda e: e.get("date") or "9999")
    return jsonify(events)

@app.route("/api/events", methods=["POST"])
def add_event():
    data = request.get_json(force=True)
    for f in ["title", "date", "course"]:
        if not data.get(f):
            return jsonify({"ok": False, "error": f"Missing: {f}"}), 400
    events = load_json(EVENTS_FILE)
    ev = {
        "id": next_id(events),
        "title": data["title"].strip(),
        "course": data["course"].strip(),
        "address": data.get("address", "").strip(),
        "date": data["date"],
        "time": data.get("time", "").strip(),
        "description": data.get("description", "").strip(),
        "event_url": data.get("event_url", "").strip(),
        "tee_time_url": data.get("tee_time_url", "").strip(),
        "source": "manual",
        "type": data.get("type", "outing"),
    }
    events.append(ev)
    save_json(EVENTS_FILE, events)
    return jsonify({"ok": True, "event": ev})

@app.route("/api/events/<int:eid>", methods=["DELETE"])
def delete_event(eid):
    events = [e for e in load_json(EVENTS_FILE) if e.get("id") != eid]
    save_json(EVENTS_FILE, events)
    return jsonify({"ok": True})

@app.route("/api/upcoming")
def get_upcoming():
    return jsonify(load_json(UPCOMING_FILE))

@app.route("/api/scrape", methods=["POST"])
def scrape_route():
    try:
        # Attempt live scrape of Butler's calendar first
        scraped = run_scrape()
        # If scraper got nothing (JS-rendered page, network error, etc.) fall back to seed
        if not scraped:
            scraped = build_events_from_seed()
        return jsonify({"ok": True, "count": len(scraped)})
    except Exception as exc:
        # Always fall back to seed so the button is never useless
        try:
            result = build_events_from_seed()
            return jsonify({"ok": True, "count": len(result), "note": "Used cached data"})
        except Exception as e2:
            return jsonify({"ok": False, "error": str(e2)}), 500

@app.route("/api/courses")
def get_courses():
    return jsonify(COURSES)

# ── Seed data on first run ────────────────────────────────────────────────────

BUTLER_EVENTS = [
    # April 2026 — source: butlersgolf.com/events/calendar
    ("Bethel Park Hockey Outing",               "2026-04-25", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    # May 2026
    ("Bountiful Blessings Golf Outing",         "2026-05-02", "8:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Mike Kerston Memorial Golf Outing",       "2026-05-03", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Tribe Baseball Outing",                   "2026-05-08", "1:00 PM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Kanes Krew Cystic Fibrosis Outing",       "2026-05-09", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Mayor Tom Maglicco Spring Classic",       "2026-05-15", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Jereme Dudzinski Foundation Outing",      "2026-05-16", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Buena Vista Fireman Outing",              "2026-05-17", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("McKeesport Heritage Golf Outing",         "2026-05-29", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("The Backdraft Golf Outing",               "2026-05-30", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    # June 2026
    ("PENNDOT Golf Outing",                     "2026-06-05", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("White Oak Volunteer Fire Co. Outing",     "2026-06-06", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Mon Valley Paws Golf Outing",             "2026-06-07", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Rostraver Fire Dept Golf Outing",         "2026-06-09", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("UVWA Local 612 Golf Outing",              "2026-06-13", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Butler's VFW Golf Outing",                "2026-06-15", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Gospel Alliance Youth Group Outing",      "2026-06-19", "8:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Sam's Club / Children's Hospital Outing", "2026-06-19", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Iron Workers Local Union #3 Outing",      "2026-06-20", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("McKeesport Tiger Football Outing",        "2026-06-26", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Hitachi Rail Golf Outing",                "2026-06-27", "8:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Chuck Bakewell Memorial Outing",          "2026-06-27", "2:00 PM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    # July 2026
    ("Steve Kraus Memorial Outing",             "2026-07-03", "10:00 AM", "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Roarty Memorial Golf Outing",             "2026-07-10", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Perrotta Memorial Golf Outing",           "2026-07-11", "8:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("Process Combustion Corp. Outing",         "2026-07-17", "8:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
    ("All But Furgotten Rescue Golf Outing",    "2026-07-18", "9:00 AM",  "Butler's Golf Course", "800 Rock Run Rd, Elizabeth, PA 15037"),
]

# source: 3lakesgolf.com/wp-json/tribe/events/v1/events — verified April 2026
THREE_LAKES_EVENTS = [
    ("SPY Swimming Golf Outing",                    "2026-05-16", "1:00 PM",  "3 Lakes Golf Course", "6700 Saltsburg Rd, Pittsburgh, PA 15235", "https://3lakesgolf.com/event/spy-swimming-golf-outing/",                          "Fundraiser supporting competitive swimming. 18 holes, cart, lunch, dinner & prizes."),
    ("Public Shotgun Start",                        "2026-05-17", "8:00 AM",  "3 Lakes Golf Course", "6700 Saltsburg Rd, Pittsburgh, PA 15235", "https://3lakesgolf.com/event/shotgun-start-8-am-private-event/",                 "Public tee times available for the 8 am shotgun start. Book your starting hole."),
    ("Men's Baseball League Golf Outing",           "2026-05-17", "2:00 PM",  "3 Lakes Golf Course", "6700 Saltsburg Rd, Pittsburgh, PA 15235", "https://3lakesgolf.com/event/mens-baseball-league-golf-outing/",                 "2nd year of the men's baseball league outing at 3 Lakes."),
    ("Glow Golf Night",                             "2026-05-02", "8:00 PM",  "3 Lakes Golf Course", "6700 Saltsburg Rd, Pittsburgh, PA 15235", "https://3lakesgolf.com/event/glow-golf-night/2026-05-02/",                       "$39 — 9 holes illuminated golf, 1 LED ball, $5 bar credit. Check in before 8 PM."),
    ("Glow Golf Night",                             "2026-05-30", "8:00 PM",  "3 Lakes Golf Course", "6700 Saltsburg Rd, Pittsburgh, PA 15235", "https://3lakesgolf.com/event/glow-golf-night/2026-05-30/",                       "$39 — 9 holes illuminated golf, 1 LED ball, $5 bar credit."),
    ("Mitchell P Harmon Memorial Scholarship Outing","2026-09-19", "1:00 PM", "3 Lakes Golf Course", "6700 Saltsburg Rd, Pittsburgh, PA 15235", "https://3lakesgolf.com/event/mitchell-p-harmon-memorial-scholarship-outing/",   "Annual memorial scholarship golf outing at 3 Lakes."),
    ("Marlin's & Mates Leukemia Benefit Outing",    "2026-09-26", "9:00 AM",  "3 Lakes Golf Course", "6700 Saltsburg Rd, Pittsburgh, PA 15235", "https://3lakesgolf.com/event/marlins-mates-leukemia-benefit-golf-outing/",      "Annual leukemia charity golf outing."),
    ("Glow Golf Night",                             "2026-09-26", "8:00 PM",  "3 Lakes Golf Course", "6700 Saltsburg Rd, Pittsburgh, PA 15235", "https://3lakesgolf.com/event/glow-golf-night/2026-09-26/",                       "$39 — 9 holes illuminated golf, 1 LED ball, $5 bar credit."),
]

UPCOMING_EVENTS = [
    # All sourced from Eventbrite Pittsburgh golf listings — verified April 2026
    {
        "title": "Jeremy Dentel Memorial Golf Outing",
        "course": "3 Lakes Golf Course",
        "address": "6700 Saltsburg Rd, Pittsburgh, PA 15235",
        "date": "2026-08-01",
        "time": "8:00 AM",
        "description": "Annual memorial golf outing at 3 Lakes Golf Course in Penn Hills.",
        "event_url": "https://www.eventbrite.com/e/jeremy-dentel-memorial-golf-outing-tickets-1977177525202",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "11th Annual DNA Charity Golf Classic",
        "course": "Meadowink Golf Course",
        "address": "4076 Bulltown Rd, Murrysville, PA 15668",
        "date": "2026-06-12",
        "time": "9:45 AM",
        "description": "11th annual charity golf classic benefiting local Pittsburgh organizations.",
        "event_url": "https://www.eventbrite.com/e/11th-annual-dna-charity-golf-classic-tickets-1985727278745",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Denise Grayson Classic 2026",
        "course": "Butler's Golf Course",
        "address": "800 Rock Run Rd, Elizabeth, PA 15037",
        "date": "2026-08-15",
        "time": "7:30 AM",
        "description": "Annual charity golf classic at Butler's Golf Course, Elizabeth PA.",
        "event_url": "https://www.eventbrite.com/e/denise-grayson-classic-2026-tickets-1985464987224",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "8th Annual Pgh Irish Fest Golf Outing",
        "course": "Murrysville Golf Club",
        "address": "3804 Sardis Rd, Murrysville, PA 15668",
        "date": "2026-08-09",
        "time": "1:00 PM",
        "description": "Presented by Brighton Land Management. Benefits Pittsburgh Irish Festival.",
        "event_url": "https://www.eventbrite.com/e/8th-annual-pgh-irish-fest-golf-outing-presented-by-brighton-land-management-tickets-1986446567156",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Swing for the Singlet – Hampton Wrestling Golf Outing",
        "course": "Pheasant Ridge Golf Club",
        "address": "Gibsonia, PA",
        "date": "2026-05-09",
        "time": "2:00 PM",
        "description": "Benefits Hampton Wrestling program. 4-person scramble format.",
        "event_url": "https://www.eventbrite.com/e/swing-for-the-singlet-hampton-wrestling-golf-outing-tickets-1983280654827",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Connecting Champions Golf Scramble",
        "course": "Green Oaks Country Club",
        "address": "Verona, PA",
        "date": "2026-06-08",
        "time": "9:00 AM",
        "description": "Annual charity golf scramble benefiting Connecting Champions organization.",
        "event_url": "https://www.eventbrite.com/e/connecting-champions-golf-scramble-tickets-1981950818250",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Pittsburgh Sports League Golf Outing",
        "course": "Butler's Golf Course",
        "address": "800 Rock Run Rd, Elizabeth, PA 15037",
        "date": "2026-09-12",
        "time": "9:00 AM Shotgun",
        "description": "4-person scramble. $100/golfer early bird (before Aug 15), $125 after. Open registration.",
        "event_url": "https://pittsburghsportsleague.leaguelab.com/page/Golf-Outing",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Steel City Swing – 2026 Pittsburgh Chapter Golf Outing",
        "course": "Olde Stonewall Golf Club",
        "address": "Ellwood City, PA",
        "date": "2026-06-17",
        "time": "9:30 AM",
        "description": "Pittsburgh chapter annual golf outing at Olde Stonewall Golf Club.",
        "event_url": "https://www.eventbrite.com/e/steel-city-swing-2026-pittsburgh-chapter-golf-outing-registration-1982437807849",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Nora Helfrich Memorial Golf Outing – Tri-Community South EMS",
        "course": "Lindenwood Golf Club",
        "address": "Canonsburg, PA",
        "date": "2026-05-21",
        "time": "7:30 AM",
        "description": "Benefits Tri-Community South EMS. Memorial outing at Lindenwood Golf Club.",
        "event_url": "https://www.eventbrite.com/e/nora-helfrich-memorial-golf-outing-supporting-tri-community-south-ems-tickets-1977028656933",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Xtra Innings Sports Bar & Grille 2nd Annual Golf Outing",
        "course": "Saxon Golf Course",
        "address": "Sarver, PA",
        "date": "2026-05-16",
        "time": "8:00 AM",
        "description": "2nd annual outing benefiting local community. Scramble format.",
        "event_url": "https://www.eventbrite.com/e/xtra-innings-sports-bar-grille-2nd-annual-golf-outing-tickets-1984409751987",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "39th Annual Charity Golf Outing",
        "course": "Southpointe Golf Club",
        "address": "Canonsburg, PA",
        "date": "2026-05-11",
        "time": "8:00 AM",
        "description": "39th annual charity golf outing at Southpointe Golf Club.",
        "event_url": "https://www.eventbrite.com/e/39th-annual-charity-golf-outing-tickets-1980208096723",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "19th Annual Alby Oxenreiter Golf Classic",
        "course": "Chartiers Country Club",
        "address": "Pittsburgh, PA",
        "date": "2026-07-27",
        "time": "10:00 AM",
        "description": "19th annual classic at Chartiers Country Club, Pittsburgh.",
        "event_url": "https://www.eventbrite.com/e/19th-annual-alby-oxenreiter-golf-classic-tickets-1983549609277",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Dick Groat and Bill Hillgrove Classic",
        "course": "Champion Lakes Golf Course & Resort",
        "address": "Bolivar, PA",
        "date": "2026-05-09",
        "time": "10:00 AM",
        "description": "Celebrity classic featuring Pittsburgh legends Dick Groat and Bill Hillgrove.",
        "event_url": "https://www.eventbrite.com/e/dick-groat-and-bill-hillgrove-classic-tickets-1982592715181",
        "source": "eventbrite",
        "type": "tournament",
    },
    {
        "title": "D.A.P. 4 Change – Drive and Putt Golf Outing",
        "course": "Black Hawk Golf Course",
        "address": "Beaver Falls, PA",
        "date": "2026-07-18",
        "time": "12:00 PM",
        "description": "Community charity golf outing benefiting D.A.P. 4 Change.",
        "event_url": "https://www.eventbrite.com/e/dap-4-change-drive-and-putt-golf-outing-tickets-1985822849600",
        "source": "eventbrite",
        "type": "outing",
    },
    {
        "title": "Birdies for Books Annual Golf Outing",
        "course": "Aubrey's Dubbs Dred Golf Course",
        "address": "Butler, PA",
        "date": "2026-06-20",
        "time": "8:00 AM",
        "description": "Annual outing benefiting literacy programs in the Pittsburgh area.",
        "event_url": "https://www.eventbrite.com/e/birdies-for-books-annual-golf-outing-registration-1972830690703",
        "source": "eventbrite",
        "type": "outing",
    },
    # PGT (Pittsburgh Golfers Tour) — source: pgtgolf.com/schedule
    {
        "title": "PGT Tournament — Cedarbrook Golf Course",
        "course": "Cedarbrook Golf Course",
        "address": "Belle Vernon, PA",
        "date": "2026-04-26",
        "time": "10:30 AM",
        "description": "Pittsburgh Golfers Tour event at Cedarbrook Golf Course, Belle Vernon PA. Open registration. See pgtgolf.com for details.",
        "event_url": "https://www.pgtgolf.com/schedule",
        "source": "pgt",
        "type": "tournament",
    },
    {
        "title": "PGT Tournament — Youghiogheny Country Club",
        "course": "Youghiogheny Country Club",
        "address": "Elizabeth Township, PA",
        "date": "2026-05-09",
        "time": "12:30 PM",
        "description": "Pittsburgh Golfers Tour event at Youghiogheny Country Club. Open registration. See pgtgolf.com for details.",
        "event_url": "https://www.pgtgolf.com/schedule",
        "source": "pgt",
        "type": "tournament",
    },
    {
        "title": "PGT Tournament — Butler's GC Lakeside",
        "course": "Butler's Golf Course (Lakeside)",
        "address": "800 Rock Run Rd, Elizabeth, PA 15037",
        "date": "2026-06-21",
        "time": "9:00 AM",
        "description": "Pittsburgh Golfers Tour event on the Lakeside course at Butler's Golf. Open registration at pgtgolf.com.",
        "event_url": "https://www.pgtgolf.com/schedule",
        "source": "pgt",
        "type": "tournament",
    },
    {
        "title": "PGT Tournament — Quicksilver Golf Club",
        "course": "Quicksilver Golf Club",
        "address": "2000 Quicksilver Rd, Midway, PA 15060",
        "date": "2026-07-26",
        "time": "10:00 AM",
        "description": "Pittsburgh Golfers Tour event at Quicksilver Golf Club. Former Senior PGA TOUR host course. Open registration at pgtgolf.com.",
        "event_url": "https://www.pgtgolf.com/schedule",
        "source": "pgt",
        "type": "tournament",
    },
    {
        "title": "PGT Tournament — Lindenwood Golf Club",
        "course": "Lindenwood Golf Club",
        "address": "1003 N Race Track Rd, Canonsburg, PA 15317",
        "date": "2026-08-02",
        "time": "10:00 AM",
        "description": "Pittsburgh Golfers Tour event on the Red/Blue course at Lindenwood Golf Club. Open registration at pgtgolf.com.",
        "event_url": "https://www.pgtgolf.com/schedule",
        "source": "pgt",
        "type": "tournament",
    },
    {
        "title": "PGT Tournament — Cranberry Highlands Golf Course",
        "course": "Cranberry Highlands Golf Course",
        "address": "5190 Poplar Dr, Cranberry Township, PA 16066",
        "date": "2026-08-09",
        "time": "9:00 AM",
        "description": "Pittsburgh Golfers Tour event at Cranberry Highlands. Open registration at pgtgolf.com.",
        "event_url": "https://www.pgtgolf.com/schedule",
        "source": "pgt",
        "type": "tournament",
    },
]


def build_events_from_seed():
    """Build confirmed events list from hardcoded seed data, preserving manual entries."""
    existing = load_json(EVENTS_FILE)
    manual = [e for e in existing if e.get("source") == "manual"]
    seeded = []
    counter = 1

    for (title, dt, tm, course, addr) in BUTLER_EVENTS:
        seeded.append({
            "id": counter,
            "title": title,
            "course": course,
            "address": addr,
            "date": dt,
            "time": tm,
            "description": "Public golf outing listed on Butler's official event calendar at butlersgolf.com/events/calendar.",
            "event_url": "https://www.butlersgolf.com/events/calendar",
            "tee_time_url": "https://www.butlersgolf.com/golf/tee-times",
            "source": "butlers_calendar",
            "type": "outing",
        })
        counter += 1

    for (title, dt, tm, course, addr, event_url, desc) in THREE_LAKES_EVENTS:
        seeded.append({
            "id": counter,
            "title": title,
            "course": course,
            "address": addr,
            "date": dt,
            "time": tm,
            "description": desc,
            "event_url": event_url,
            "tee_time_url": "https://www.chronogolf.com/club/3-lakes-golf-course",
            "source": "3lakes_calendar",
            "type": "outing",
        })
        counter += 1

    for ev in manual:
        ev["id"] = counter; counter += 1

    merged = seeded + manual
    save_json(EVENTS_FILE, merged)
    return merged


def seed_data():
    """Write seed files if they are missing or empty."""
    if not os.path.exists(EVENTS_FILE) or os.path.getsize(EVENTS_FILE) < 5:
        result = build_events_from_seed()
        print(f"[seed] {len(result)} confirmed events written.")

    if not os.path.exists(UPCOMING_FILE) or os.path.getsize(UPCOMING_FILE) < 5:
        upcoming = []
        for i, ev in enumerate(UPCOMING_EVENTS, start=1):
            upcoming.append({**ev, "id": i})
        save_json(UPCOMING_FILE, upcoming)
        print(f"[seed] {len(upcoming)} upcoming events written.")


# Run at import time so Flask's debug reloader child process also seeds correctly
seed_data()


if __name__ == "__main__":
    print("=" * 55)
    print("  Golf Calendar — Pittsburgh / 15239 area")
    print("  Open: http://localhost:8080")
    print("=" * 55)
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
