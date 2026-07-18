#!/usr/bin/env python3
"""
Generator for the GDG on Campus JIS University — Technical Report (2022– ).
Emits main.tex from the structured event data below, then compile with:
    latexmk -pdf main.tex     (or)   pdflatex main.tex  x2

How to add images to an event
-----------------------------
Drop image files (.jpg / .png) into  assets/gallery/<NN>/  where <NN> is the
zero-padded event number (e.g. assets/gallery/16/). Every image in that folder
is picked up automatically and laid out as a balanced masonry grid — no code
edit needed. Rebuild to see them.

How to add a new event / season
-------------------------------
Append a dict to EVENTS (and, for a new season, an entry to SEASONS). Nothing
else needs changing — TOC, stats, chart and galleries all recompute.
"""
import os, glob, subprocess, json, csv

BASE = os.path.dirname(os.path.abspath(__file__))
GAL = "assets/gallery"

# ----------------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------------
# Leadership lineage / seasons.
#   evs         : inclusive range of event numbers belonging to the season
#   roll        : organiser roll number ("" leaves a fill-in line for a future lead)
#   ev_override : headline count of completed events (else counted from cards)
#   incoming    : count of upcoming events for the season
#   ft_override : headline cumulative footfall (else summed from cards)
#   members     : registered community size at season close, as printed
#   members_n   : same figure as a number — drives the growth chart only
SEASONS = [
    dict(year="2022 – 23", brand="GDSC",
         organiser="Abhishek Kushwaha", role="Founding Organiser", roll="", core=5,
         members="~50–100", members_n=75,
         evs=(1, 3),
         note="The founding season. The chapter is established under the Department of "
              "Computer Science \\& Engineering and runs its first info session, its first "
              "external speaker workshop, and its first hosted codefest."),
    dict(year="2023 – 24", brand="GDSC",
         organiser="Chandan Pandey", role="Organiser", roll="", core=6,
         members="~200–300", members_n=250,
         evs=(4, 8),
         note="Consolidation. Study Jams and a source-code contribution drive push the "
              "chapter deeper into cloud skilling and open source, alongside the annual "
              "onboarding session and a hands-on web bootcamp."),
    dict(year="2024 – 25", brand="GDG",
         organiser="Ankita Chakraborty", role="Organiser", roll="", core=8,
         members="~500–700", members_n=600,
         evs=(9, 15),
         note="Rebrand to Google Developer Groups (GDG) on Campus and a step-up in cadence: "
              "cross-chapter collaborations (Solution Challenge, React), security and Web3 "
              "tracks, and the first Build with AI."),
    dict(year="2025 – 26", brand="GDG",
         organiser="Ayushman Bhattacharya", role="Organiser (current)", roll="23CS2021016", core=12,
         members="~1,800", members_n=1800,
         evs=(16, 35),
         note="The largest season on record — national hackathons, Hacktoberfest, GSoC "
              "preparation, live CTF and system-design tracks, a Kubernetes/CNCF meetup and "
              "cross-community welcomes with OWASP. This report is compiled during, and as "
              "part of, this tenure."),
]

# Each event: number, title, date, venue, duration, speakers, partners, attendance, mode.
# Optional: status="upcoming"; reg="Free registration"/"External registration".
# Images come from assets/gallery/<NN>/ automatically.
EVENTS = [
    dict(n=1, title="Info Session — Class of 2022–23",
         date="27 August 2022", venue="JIS University", dur="11:00 AM IST",
         speakers="Abhishek Kushwaha", partners="—", att="90", mode="On-Site"),
    dict(n=2, title="Interacting with the Unique Blockchain: From Zero to Hero",
         date="3 September 2022", venue="JIS University", dur="4:00 PM IST",
         speakers="Alexander Saft", partners="Unique", att="70–80", mode="Virtual"),
    dict(n=3, title="GDG JISU Codefest 2023",
         date="21 March 2023", venue="JIS University", dur="10:00 AM – 3:30 PM",
         speakers="Arkaprabha Chakraborty, Manish Kr Barnwal, Soumyadeep Chowdhury, Shubhayu Majumder",
         partners="GitHub, Flutter, Firebase, Android", att="150", mode="On-Site"),

    dict(n=4, title="Info Session — Class of 2023–24",
         date="19 September 2023", venue="JIS University", dur="11:00 AM IST",
         speakers="Chandan Pandey", partners="—", att="120", mode="On-Site"),
    dict(n=5, title="Google Cloud Study Jams",
         date="1 October – 2 November 2023", venue="JIS University", dur="~2 months",
         speakers="Facilitated cohort", partners="Google Cloud Skills Boost", att="100", mode="Virtual"),
    dict(n=6, title="Hack the Source",
         date="25 November 2023", venue="JIS University", dur="12:00 – 2:00 PM",
         speakers="Harshbardhan Bajoriya, Shinjini Roy, Ronit Banerjee, Khayati Mehta, Aniruddha Basak",
         partners="GitHub, Google, Salesforce", att="60–70", mode="On-Site"),
    dict(n=7, title="Google Study Jams 2023",
         date="11 October – 12 November 2023", venue="JIS University", dur="~1 month",
         speakers="Facilitated cohort", partners="Google Cloud Skills Boost", att="80–90", mode="On-Site"),
    dict(n=8, title="Web Mastery BootCamp",
         date="20 January 2024", venue="JIS University", dur="10:00 AM – 12:00 PM",
         speakers="Manish Gupta", partners="—", att="50–60", mode="On-Site"),

    dict(n=9, title="Info Session 2024",
         date="20 September 2024", venue="JIS University", dur="11:00 AM – 1:00 PM",
         speakers="Ankita Chakraborty, Abhishek Kushwaha, Shemanti Pal", partners="Google",
         att="80–90", mode="On-Site"),
    dict(n=10, title="Keeping Data Safe",
         date="13 December 2024", venue="JIS University", dur="10:00 – 11:00 AM",
         speakers="Heera Sharma", partners="Go Laadli", att="80–90", mode="Virtual"),
    dict(n=11, title="Rectify: The Ultimate React Workshop",
         date="26 December 2024", venue="JIS University", dur="7:00 – 9:30 PM",
         speakers="Ayushman Bhattacharya, Manish Gupta, Krishnendu Dasgupta",
         partners="Altor Smart Mobility, GDG JISU, GDG GCECT, GDG SNJB, GDG XIE",
         att="80–90", mode="Virtual"),
    dict(n=12, title="Google Solution Challenge Workshop",
         date="26 December 2024", venue="JIS University", dur="7:00 – 9:30 PM",
         speakers="Arijit Ghosal",
         partners="GDG JISU, GDG GCECT, GDG SNJB, GDG XIE, GDG GCELT, GDG TMSL, GDG TIU",
         att="80–90", mode="Virtual"),
    dict(n=13, title="Cybersecurity 101: Step Into the World of Ethical Hacking",
         date="22 January 2025", venue="JIS University", dur="7:30 – 9:00 PM",
         speakers="Shreya Dutta", partners="Google", att="90", mode="Virtual"),
    dict(n=14, title="Navigating the Future: Embracing Web3 and Blockchain Technology",
         date="25 January 2025", venue="JIS University", dur="7:00 – 9:00 PM",
         speakers="Sachindra Singh", partners="Quill AI Network", att="80–90", mode="Virtual"),
    dict(n=15, title="Build with AI",
         date="5 March 2025", venue="JIS University", dur="7:00 – 9:00 PM",
         speakers="Ayushman Bhattacharya", partners="Google", att="50", mode="Virtual"),

    dict(n=16, title="Codesprint 2.0 — Internal Nomination for SIH",
         date="22 September 2025", venue="JIS University", dur="2 Days",
         speakers="Debmitra Ghosh, Ayushman Bhattacharya, Abiroy Karmakar, TCS \\& industry members",
         partners="IEEE Australia, IEEE ComSoc, IIST, JIS Group, Pollinations.ai, GDG JISU",
         att="290", mode="On-Site"),
    dict(n=17, title="Kickstart Hacktoberfest 2025 \\& Google Study Jams",
         date="13 October 2025", venue="JIS University", dur="10:00 AM – 1:00 PM",
         speakers="Ayushman Bhattacharya, Debasish Mitra, Samrat Talukdar", partners="Google",
         att="80–90", mode="On-Site"),
    dict(n=18, title="Hacktoberfest Meetup Kolkata 2025",
         date="27 October 2025", venue="JIS University", dur="9:00 AM – 5:00 PM",
         speakers="Ayushman Bhattacharya, Abhishek Kushwaha, Saugata Sarkar, Shreya Dutta, Rahul Kamiliya",
         partners="Google, Pollinations.ai", att="120", mode="On-Site"),
    dict(n=19, title="CodeSprint 2026 Hackathon",
         date="13 October 2025", venue="JIS University", dur="10:00 AM – 1:00 PM",
         speakers="Anuska Kapuria, Vivek Yadav", partners="GitHub, Pollinations.ai", att="60", mode="Virtual"),
    dict(n=20, title="Chill Out \\& Level Up: Fun with Git \\& GitHub!",
         date="13 October 2025", venue="JIS University", dur="7:00 – 9:00 PM",
         speakers="Anuska Kapuria, Vivek Yadav", partners="GitHub, Pollinations.ai", att="60", mode="Virtual"),
    dict(n=21, title="GDG TechSprint Hackathon 2026",
         date="20 December 2025", venue="JIS University", dur="~1 month",
         speakers="Ayushman Bhattacharya", partners="Google", att="60", mode="Virtual"),
    dict(n=22, title="Google TechSprint Chill Talk 101: Unwind and Unleash Your Creativity",
         date="23 December 2025", venue="JIS University", dur="8:30 – 9:30 PM",
         speakers="Ayushman Bhattacharya, Debasish Mitra", partners="Google", att="40–50", mode="Virtual"),
    dict(n=23, title="Tech Winter Break Cohost 2026",
         date="22 \\& 24 January 2026", venue="JIS University", dur="6:00 – 8:00 PM",
         speakers="Nandini Verma, Debankur Dutta, Sagnik Roy, Chandramouli Halder (GDG GNIT)",
         partners="Google, Pollinations.ai", att="170–180", mode="Virtual"),
    dict(n=24, title="GSoC Info Session 2026 — \\enquote{GSOC Crack Karna Hain? For Sure}",
         date="28 January 2026", venue="JIS University", dur="10:00 AM – 1:00 PM",
         speakers="Ayushman Bhattacharya", partners="Google Summer of Code, Pollinations.ai",
         att="50–60", mode="On-Site"),
    dict(n=25, title="How I Audit Codebases as a Pentester (Live CTF Workshop)",
         date="16 February 2026", venue="JIS University", dur="10:00 AM – 1:00 PM",
         speakers="Sagnik Roy, Shreya Dutta", partners="OWASP, Pollinations.ai", att="30", mode="On-Site"),
    dict(n=26, title="Boss vs Freshers: System Designer Cracker!",
         date="20 February 2026", venue="JIS University", dur="10:30 AM – 1:00 PM",
         speakers="Nandini Verma", partners="Google, Pollinations.ai", att="50–60", mode="On-Site"),
    dict(n=27, title="Kubernetes and Friends Meetup — CNCF Hooghly",
         date="24 February 2026", venue="JIS University", dur="11:00 AM – 1:00 PM",
         speakers="Hrittik Roy, Abhishek Kushwaha, Ayushman Bhattacharya, Shivay Lamba, Rajani Ekunde, Abhiroy",
         partners="Google, PrepVerse, Pollinations.ai", att="110–120", mode="On-Site"),
    dict(n=28, title="Udyamini: Navigating Career with Confidence",
         date="8 March 2026", venue="JIS University", dur="6:00 – 8:30 PM",
         speakers="Anwesha Chakraborty, Khushi Yadav", partners="Google, Pollinations.ai",
         att="70–80", mode="On-Site"),
    dict(n=29, title="A Grand Welcome — OWASP Community ft. dscjisu",
         date="6 April 2026", venue="JIS University", dur="7:00 – 9:00 PM",
         speakers="Shreya Dutta, Rahul Kamiliya, Ayushman Bhattacharya, Sagnik Roy",
         partners="Google, OWASP", att="40–50", mode="Virtual"),
    dict(n=30, title="It's Swags Time — @dscjisu ft. Google Bangalore",
         date="20 April 2026", venue="JIS University", dur="2:00 – 4:00 PM",
         speakers="Ayushman Bhattacharya, Debasish Mitra", partners="Google, Myceli.ai",
         att="95", mode="On-Site"),
    dict(n=31, title="Maintainers Month: How to Be the Contributor that Maintainers Actually Want",
         date="31 May 2026", venue="JIS University", dur="7:00 – 9:00 PM",
         speakers="Ayushman Bhattacharya", partners="GitHub, Myceli.ai", att="40", mode="Virtual"),
    dict(n=32, title="Know Your Terminal: Zero to Hero on Bash Programming",
         date="23 June 2026", venue="JIS University", dur="2 hours (from 6:30 PM)",
         speakers="Ayushman Bhattacharya, Supriyo Saha",
         partners="GDG UEMK, GDG JISU, Google Cloud Skills Boost", att="60–65", mode="Virtual"),
    dict(n=33, title="Understanding Prompt Injection Attacks in LLMs",
         date="18 June 2026", venue="JIS University", dur="2.5 hours (from 10:30 AM)",
         speakers="—", partners="OWASP JISU, Miro, Mastra AI, Elixpo", att="60", mode="On-Site"),
]

# One-line "at a glance" purpose for every event (fills whitespace; inferred from
# each event's type, partners and format — enrich as first-hand notes surface).
BLURBS = {
 1: "The founding season's opening event. It introduced GDSC JIS University to a fresh cohort — the community's mission, the technical domains it would explore, and the ways students could take part as members and volunteers. As the first gathering under the newly-formed chapter, it doubled as the recruitment drive for the founding core team.",
 2: "A beginner-friendly virtual workshop on the Unique Network / Polkadot ecosystem, delivered by an industry developer. It walked students with no prior Web3 background through the fundamentals of building on a substrate-based blockchain, and broadened the chapter's early programming beyond web and cloud into emerging decentralised technology.",
 3: "The chapter's first hosted competitive-coding event, run on-site across a full day. Spanning tooling from GitHub, Flutter, Firebase and Android, it put 150 students in a deadline-driven build environment with mentors on the floor. Codefest established the chapter's flagship habit of large, practical, project-first gatherings.",
 4: "The annual onboarding session opening the 2023–24 cycle under new leadership. It re-introduced the community to incoming students and re-recruited the year's volunteer core, framing the roadmap of workshops, study jams and hackathons to come.",
 5: "A multi-week, self-paced cloud-skilling cohort on Google Cloud Skills Boost. Around a hundred participants worked through hands-on labs toward completion tiers and swag milestones, deepening the chapter's cloud-computing track and connecting members directly to Google's official learning platform.",
 6: "An on-site open-source contribution session led by a panel of student and community speakers. It demystified contributing to real repositories across the GitHub, Google and Salesforce ecosystems, and pushed members from consumers of software toward first-time open-source contributors.",
 7: "A month-long distributed cloud study-jam cohort that closed with swag distribution for 80+ completions. It reinforced consistent, milestone-based skilling on Google Cloud, and the high completion count reflected the chapter's growing ability to sustain longer-form programs.",
 8: "A hands-on web-development bootcamp structured as a guided roadmap — HTML, CSS, JavaScript and a capstone mini-project — facilitated by a chapter member. It took beginners from fundamentals to something shipped, strengthening the core web-dev pipeline for junior students.",
 9: "The 2024–25 onboarding session, now under the Google Developer Groups (GDG) on Campus brand following the rebrand from GDSC. Featuring past and present leads, it welcomed a new cohort and explained the year's direction, marking the chapter's change of identity while preserving continuity.",
 10: "A virtual talk on data privacy and safety led by a founder working in the space, run as a cross-chapter collaboration. It introduced students to responsible data handling and security-minded thinking, adding a privacy dimension to the year's programming.",
 11: "A multi-chapter React workshop bringing together speakers from industry and several GDG campuses. It gave students practical, component-first frontend skills, and its wide co-host list signalled the chapter's growing inter-campus network.",
 12: "A preparatory workshop for Google's global Solution Challenge, co-hosted across seven GDG chapters. It explained the challenge format and helped students shape socially-impactful project ideas, positioning members to compete on an international stage.",
 13: "An introductory ethical-hacking session for newcomers to security. It covered the mindset and entry points of penetration testing and responsible disclosure, seeding the security track that the chapter would expand considerably in later seasons.",
 14: "A Web3 and AI workshop delivered by a DevRel engineer from Quill AI Network. It introduced students to the current blockchain ecosystem and the career paths within it, continuing the chapter's recurring exposure to decentralised and emerging technology.",
 15: "The chapter's first Build with AI event, part of Google's global series. It walked students through building applications with modern AI and natural-language tooling, planting what would become a central, recurring focus on applied artificial intelligence.",
 16: "A two-day, on-site hackathon that served as the internal nomination round for the Smart India Hackathon, drawing 290 participants — the season's largest gathering. Backed by IEEE Australia, IEEE ComSoc, IIST and industry mentors, it channelled the campus's builders toward a national competition pipeline.",
 17: "The on-site launch of the chapter's Hacktoberfest drive alongside a Google Cloud study-jam cohort. It onboarded students into open-source contribution and cloud skilling for the season ahead, pairing real pull requests with structured learning.",
 18: "A full-day flagship Hacktoberfest meetup co-organised across the Kolkata community, with 120 attendees. It combined talks, contribution sprints and networking around open source, cementing the chapter's role as a regional open-source hub.",
 19: "A virtual hackathon extending the CodeSprint series, run with GitHub and Pollinations.ai tooling. It gave remote participants a focused, deadline-driven build sprint and broadened access beyond on-campus attendees.",
 20: "A relaxed, hands-on virtual session teaching Git and GitHub fundamentals. Aimed squarely at beginners, it turned version-control basics into an approachable, low-pressure workshop and lowered the barrier for first-time contributors ahead of larger events.",
 21: "A month-long virtual hackathon under the TechSprint banner, themed around leveraging AI. Teams built and iterated over an extended window, competing for official Google swag, and the long format sustained the chapter's project-first culture.",
 22: "A light, creativity-focused virtual talk that closed out the TechSprint cycle. It gave participants room to reflect, share and decompress after the hackathon push, reinforcing community and well-being alongside technical intensity.",
 23: "A multi-day, multi-track virtual cohost with GDG GNIT spanning system design, ML/AI roadmaps, keynotes and low-level systems, with 170+ participants. It packed several specialised sessions into a winter-break program and showcased the chapter's ability to run breadth and depth at once.",
 24: "An on-site session demystifying Google Summer of Code for aspiring contributors. It covered proposal writing, organisation selection and the contribution timeline — with Pollinations.ai as a live example org — aiming to convert curiosity into serious GSoC applications.",
 25: "A hands-on, on-site live Capture-the-Flag workshop on real-world code auditing, run with OWASP. Participants worked through practical vulnerability discovery the way a pentester would, advancing the chapter's maturing security and OWASP track.",
 26: "An on-site system-design session framed as a friendly challenge across experience levels. It designed a real system — a URL shortener — from first principles, making scalability and architecture concepts approachable for newcomers.",
 27: "A CNCF-aligned Kubernetes and cloud-native meetup with a strong speaker lineup and 110+ attendees. It connected campus students to the wider cloud-native community and its practitioners, extending the chapter's reach into professional DevOps circles.",
 28: "An on-site career session run around International Women's Day, focused on building confidence and direction in early tech careers. It broadened the chapter's programming toward mentorship and inclusion.",
 29: "A virtual welcome bridging the chapter with the OWASP community. It formalised a cross-community relationship around application security and set up the joint security programming that followed.",
 30: "An on-site celebration and swag distribution featuring collaboration with Google Bangalore. It recognised active contributors and members with official swag, rewarding participation and strengthening a sense of belonging.",
 31: "A virtual session tied to GitHub's Maintainer Month on contributing in the ways maintainers actually value. Drawing on first-hand open-source maintenance experience, it covered etiquette, high-quality pull requests and sustainable contribution — closing the season on the chapter's open-source ethos.",
 32: "A virtual, beginner-to-advanced workshop on Bash and the command line, co-delivered with GDG UEMK. Across two hours it took students from terminal basics to practical shell scripting, strengthening the foundational developer tooling skills that coursework often skips.",
 33: "An on-site security workshop on prompt-injection vulnerabilities in large language models, run with OWASP JISU alongside AI tooling partners Miro, Mastra AI and Elixpo. It examined how LLM-backed applications can be manipulated and how to defend them — sitting squarely at the intersection of AI and security, the chapter's most current technical frontier.",
}
for _e in EVENTS:
    _e.setdefault("blurb", BLURBS.get(_e["n"], ""))

# ----------------------------------------------------------------------------
# Modular data source: records.json is authoritative if present, otherwise the
# inline SEASONS/EVENTS above are used. Edit records.json to change the report
# without touching Python.
# ----------------------------------------------------------------------------
_REC = os.path.join(BASE, "records.json")
if os.path.exists(_REC):
    _d = json.load(open(_REC, encoding="utf-8"))
    SEASONS = _d["seasons"]
    EVENTS = _d["events"]
    for _s in SEASONS:
        _s["evs"] = tuple(_s["evs"])

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def att_mid(a):
    a = (a or "").replace("–", "-").strip()
    if a in ("", "—"): return 0.0
    if "-" in a:
        lo, hi = a.split("-")
        try: return (int(lo) + int(hi)) / 2
        except ValueError: return 0.0
    try: return float(a)
    except ValueError: return 0.0

_dimcache = {}
def dims(relpath):
    if relpath not in _dimcache:
        ap = os.path.join(BASE, relpath)
        out = subprocess.check_output(["identify", "-format", "%w %h", ap + "[0]"]).decode().split()
        _dimcache[relpath] = (int(out[0]), int(out[1]))
    return _dimcache[relpath]

def optimize_gallery():
    """Build-time image optimiser. Any PNG/JPEG dropped into assets/gallery/<NN>/
    is converted to a size-capped JPEG (max 1400px, q84) so the PDF stays small —
    drop images in any format and the build handles the rest. Idempotent: PNGs are
    converted once (then removed); JPEGs are only re-encoded if oversized."""
    root = os.path.join(BASE, GAL)
    if not os.path.isdir(root):
        return
    converted = capped = 0
    for dp, _, files in os.walk(root):
        for fn in files:
            p = os.path.join(dp, fn)
            ext = fn.rsplit(".", 1)[-1].lower() if "." in fn else ""
            if ext in ("png", "jpeg", "gif", "webp", "tiff", "bmp"):
                base = os.path.splitext(p)[0]
                jpg = base + ".jpg"
                if os.path.exists(jpg):
                    jpg = base + "-opt.jpg"       # never clobber an existing .jpg
                r = subprocess.run(["magick", p, "-resize", "1400x1400>",
                                    "-background", "white", "-flatten", "-quality", "84", jpg])
                if r.returncode == 0 and os.path.exists(jpg):
                    os.remove(p); converted += 1
            elif ext == "jpg" and os.path.getsize(p) > 400 * 1024:
                subprocess.run(["magick", p, "-resize", "1400x1400>", "-quality", "82", p])
                capped += 1
    if converted or capped:
        print("optimized gallery: %d converted to jpeg, %d oversized jpegs capped"
              % (converted, capped))

def event_images(n):
    d = os.path.join(BASE, GAL, "%02d" % n)
    files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"):
        files += glob.glob(os.path.join(d, ext))
    files = sorted(set(files))
    return ["%s/%02d/%s" % (GAL, n, os.path.basename(f)) for f in files]

def mem_tex(s):
    """Membership figures are approximations, so the data records them with a
    leading plain '~'. That must not reach TeX verbatim — a bare ~ is a
    non-breaking space and the tilde would silently vanish."""
    m = (s.get("members") or "").strip()
    if not m:
        return ""
    return (r"$\sim$" + m[1:].lstrip()) if m.startswith("~") else m

def season_stats(s):
    lo, hi = s["evs"]
    evs = [e for e in EVENTS if lo <= e["n"] <= hi]
    done = [e for e in evs if e.get("status") != "upcoming"]
    up = [e for e in evs if e.get("status") == "upcoming"]
    ne = s.get("ev_override", len(done))
    inc = s.get("incoming", len(up))
    ft = s.get("ft_override", sum(att_mid(e.get("att", "")) for e in done))
    return evs, ne, inc, ft

# ----------------------------------------------------------------------------
# LATEX EMISSION
# ----------------------------------------------------------------------------
GBLUE, GRED, GYEL, GGRN = "GBlue", "GRed", "GYel", "GGrn"
CYCLE = [GBLUE, GRED, GYEL, GGRN]

PREAMBLE = r"""% !TEX program = pdflatex
% GDG on Campus JIS University — Technical Report 2022–
% GENERATED by build.py — edit data there, not here.
\documentclass[11pt,a4paper]{article}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[sfdefault]{roboto}
\usepackage[a4paper,top=2.4cm,bottom=2.2cm,left=2.0cm,right=2.0cm,headsep=14pt]{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{calc}
\usepackage[most]{tcolorbox}
\usepackage{fancyhdr}
\usepackage{fontawesome5}
\usepackage{enumitem}
\usepackage{tabularx}
\usepackage{array}
\usepackage{colortbl}
\usepackage{multicol}
\usepackage{csquotes}
\usepackage{truncate}
\usepackage[hidelinks]{hyperref}
\usepackage{bookmark}
\hypersetup{pdftitle={GDG on Campus JIS University — Technical Report 2022–},
            pdfauthor={Ayushman Bhattacharya},
            pdfsubject={Chapter technical report},
            bookmarksnumbered=false}

% ---- Google brand palette ----
\definecolor{GBlue}{HTML}{4285F4}
\definecolor{GRed}{HTML}{EA4335}
\definecolor{GYel}{HTML}{FBBC04}
\definecolor{GGrn}{HTML}{34A853}
\definecolor{Ink}{HTML}{202124}
\definecolor{Slate}{HTML}{5F6368}
\definecolor{Mist}{HTML}{F1F3F4}
\definecolor{Line}{HTML}{DADCE0}
\color{Ink}

% ---- running header / footer ----
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[C]{\footnotesize\color{Slate}%
  \textcolor{GBlue}{\rule[-1pt]{7pt}{7pt}}\hspace{2pt}%
  GDG on Campus JIS University \,\textperiodcentered\, Technical Report \,\textperiodcentered\, Dept. of CSE}
\fancyfoot[R]{\footnotesize\color{Slate}\thepage}
\fancyhead[L]{\footnotesize\color{Slate}\leftmark}
\renewcommand{\sectionmark}[1]{\markboth{#1}{}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}

% four-colour rule used as a divider throughout
\newcommand{\gbar}[1][\linewidth]{%
  \begin{tikzpicture}
    \fill[GBlue] (0,0) rectangle (0.25*#1,0.11);
    \fill[GRed]  (0.25*#1,0) rectangle (0.50*#1,0.11);
    \fill[GYel]  (0.50*#1,0) rectangle (0.75*#1,0.11);
    \fill[GGrn]  (0.75*#1,0) rectangle (#1,0.11);
  \end{tikzpicture}}

% developer-brackets mark (vector), used as a small accent
\newcommand{\devmark}[1]{%
  \begin{tikzpicture}[x=1cm,y=1cm]
    \def\h{#1}
    \fill[GBlue] (0,0) -- (0.34*\h,0.5*\h) -- (0.12*\h,0.5*\h) -- (-0.22*\h,0) -- cycle;
    \fill[GRed]  (0,\h) -- (0.34*\h,0.5*\h) -- (0.12*\h,0.5*\h) -- (-0.22*\h,\h) -- cycle;
    \fill[GGrn]  (0.9*\h,0) -- (0.56*\h,0.5*\h) -- (0.78*\h,0.5*\h) -- (1.12*\h,0) -- cycle;
    \fill[GYel]  (0.9*\h,\h) -- (0.56*\h,0.5*\h) -- (0.78*\h,0.5*\h) -- (1.12*\h,\h) -- cycle;
  \end{tikzpicture}}

% framed image helper — width fills the column but height is capped so tall
% (portrait) photos can't overflow the page and push a gallery onto the next one.
\newlength{\galmaxh}\setlength{\galmaxh}{7.5cm}
\newcommand{\galimg}[1]{\setlength{\fboxsep}{0pt}\setlength{\fboxrule}{0.6pt}%
  \fcolorbox{Line}{white}{\includegraphics[width=\linewidth,height=\galmaxh,keepaspectratio]{#1}}}
"""

def season_brand_name(brand):
    return ("Google Developer Student Clubs" if brand == "GDSC"
            else "Google Developer Groups on Campus")

def cover():
    return r"""
% ============================== COVER ==============================
\thispagestyle{empty}
\vspace*{-2.55cm}%
\noindent\makebox[\linewidth][c]{\includegraphics[width=\paperwidth]{assets/brand/banner_cover.png}}

\vspace{0.45cm}
\begin{center}
  \includegraphics[width=2.3cm]{assets/brand/profile_dscjisu_native.png}\\[0.26cm]
  {\color{Slate}\large Department of Computer Science \& Engineering}\\[0.10cm]
  {\color{Slate}\normalsize JIS University, Kolkata}\\[0.7cm]

  {\fontsize{37}{41}\selectfont\bfseries\color{Ink} Technical Report}\\[0.26cm]
  {\Large\color{GBlue}\bfseries GDG on Campus \textperiodcentered\ JIS University}\\[0.34cm]
  {\large\color{Slate} Started in 2022 \,--}\\[0.55cm]
  \gbar[9cm]\\[0.75cm]

  \begin{tcolorbox}[enhanced,width=12.4cm,colback=white,colframe=Line,boxrule=0.6pt,
      arc=4pt,left=18pt,right=18pt,top=10pt,bottom=10pt,drop shadow={black!12}]
    {\footnotesize\color{Slate}\textsc{Initiated by}}\\[2pt]
    {\large\bfseries Ayushman Bhattacharya}\\
    {\small\color{Slate} Organiser, GDG on Campus JIS University (2025–26)
      \;\textperiodcentered\; Roll No.\ 23CS2021016}\\[6pt]
    {\color{Line}\rule{\linewidth}{0.5pt}}\\[5pt]
    {\footnotesize\color{Slate}\textsc{Maintained by}}\\[2pt]
    {\large\bfseries Current Lead}\\
    {\small\color{Slate} passed forward, lead to lead}
  \end{tcolorbox}
\end{center}
\clearpage
"""

def foreword():
    return r"""
% ============================== FOREWORD ==============================
\phantomsection\addcontentsline{toc}{section}{Foreword \& About this Report}
\section*{\color{Ink}Foreword \& About this Report}
\gbar[\linewidth]\\[10pt]

\textbf{GDG on Campus JIS University} — formerly \emph{Google Developer Student Clubs (GDSC)} —
is a student-led technical community operating under the Department of Computer Science \&
Engineering, JIS University. Run \emph{by the students, for the students}, it has grown across
four operational years into one of the largest and most active student organisations in the
university, with a community of \textbf{$\sim$1{,}800 members} drawn from every academic
background.

We build across Artificial Intelligence, Web Development, Cloud Computing, Cybersecurity, Mobile
Development, Open Source and System Design — through workshops, hackathons, bootcamps, speaker
sessions and study jams. Beyond the technical, we invest in peer mentorship, teamwork and
community-driven growth, so that each cohort leaves stronger than it arrived and sets the bar for
the next.

\vspace{4pt}
\begin{tcolorbox}[enhanced,colback=Mist,colframe=Mist,arc=4pt,left=14pt,right=14pt,top=10pt,bottom=10pt,
    borderline west={3pt}{0pt}{GBlue}]
  {\bfseries\color{Ink}Why this document exists.}\\[2pt]
  This is the chapter's institutional memory. Leadership turns over every year; the work should not
  start from zero each time. The report records \emph{what was run, by whom, with which partners, and
  at what scale} — season by season, since 2022. It is deliberately factual: attendance figures are
  reported as recorded on the day, and event details are preserved as documented by the organising
  team of each season.
\end{tcolorbox}

\begin{tcolorbox}[enhanced,colback=white,colframe=GGrn,boxrule=1pt,arc=4pt,
    left=14pt,right=14pt,top=10pt,bottom=10pt]
  {\bfseries\color{GGrn}\faArrowRight~For the next lead.}\\[2pt]
  A community is only as strong as the memory it keeps. You inherit not just a chapter, but a
  promise — that the people who came before you are not forgotten, and that the people who come
  after you will stand on something solid. Add your season honestly, in full, and in your own voice.
  Nothing here belongs to any one of us; it belongs to whoever chooses to carry it next. When your
  time is done, hand it forward — a little larger, a little truer than you found it.
\end{tcolorbox}

\vspace{6pt}
{\footnotesize\color{Slate}\textbf{A note on numbering \& naming.} The original working records
carried a few clerical artefacts (a skipped index, a split entry, and the mid-life rebrand from
GDSC to GDG). This report renumbers all events sequentially and notes the brand in force each
season; no events were added or removed in doing so.}
\clearpage
"""

def dashboard():
    rows = []
    tot_ev = tot_inc = 0
    tot_ft = 0.0
    for s in SEASONS:
        _, ne, inc, ft = season_stats(s)
        tot_ev += ne; tot_inc += inc; tot_ft += ft
        rows.append((s, ne, inc, ft))

    def tile(color, icon, big, lab):
        return (r"\begin{tcolorbox}[enhanced,colback=white,colframe=Line,boxrule=0.6pt,arc=5pt,"
                r"width=\linewidth,left=10pt,right=10pt,top=9pt,bottom=9pt,"
                r"borderline north={3pt}{0pt}{%s}]" % color
                + (r"{\color{%s}\large\faIcon{%s}}\quad" % (color, icon))
                + (r"{\fontsize{25}{25}\selectfont\bfseries\color{Ink}%s}\\[1pt]" % big)
                + (r"{\footnotesize\color{Slate}%s}" % lab)
                + r"\end{tcolorbox}")

    tiles = (r"\noindent\begin{minipage}[t]{0.245\linewidth}%s\end{minipage}\hfill"
             r"\begin{minipage}[t]{0.245\linewidth}%s\end{minipage}\hfill"
             r"\begin{minipage}[t]{0.245\linewidth}%s\end{minipage}\hfill"
             r"\begin{minipage}[t]{0.245\linewidth}%s\end{minipage}" % (
        tile(GBLUE, "calendar-check", "4", "Seasons on record"),
        tile(GRED, "layer-group", "%d" % tot_ev,
             "Events held" + (r" \small(+%d upcoming)" % tot_inc if tot_inc else "")),
        tile(GYEL, "users", "%s{\\small k}" % (f"{tot_ft/1000:.1f}"), "Cumulative footfall"),
        tile(GGRN, "user-friends", "$\\sim$1.8{\\small k}", "Community members"),
    ))

    # growth chart
    bars, labels = [], []
    W, n = 12.0, len(rows)
    slot = W / n; barw = slot * 0.42; Hmax = 4.2
    maxev = max(r[1] for r in rows)
    for i, (s, ne, inc, ft) in enumerate(rows):
        x = i * slot + slot / 2
        h = Hmax * ne / maxev
        c = CYCLE[i % 4]
        bars.append(r"\fill[%s] (%.2f,0) rectangle (%.2f,%.2f);" % (c, x-barw/2, x+barw/2, h))
        bars.append(r"\node[font=\bfseries\small,color=Ink] at (%.2f,%.2f) {%d};" % (x, h+0.28, ne))
        labels.append(r"\node[font=\footnotesize,color=Slate,align=center] at (%.2f,-0.42) {%s};"
                      % (x, s["year"]))
        labels.append(r"\node[font=\scriptsize,color=Slate,align=center] at (%.2f,-0.86) {%s};"
                      % (x, s["organiser"].split()[0] + "\\," + s["organiser"].split()[-1][0] + "."))
    chart = (r"\begin{center}\begin{tikzpicture}[x=1cm,y=1cm]"
             + r"\draw[Line] (-0.1,0) -- (%.2f,0);" % (W+0.1)
             + "".join(bars) + "".join(labels) + r"\end{tikzpicture}\end{center}")

    # membership growth chart — a filled area under the season-close head-count,
    # so the compounding curve reads at a glance rather than four separate bars.
    mrows = [(s, s.get("members_n", 0)) for s, _, _, _ in rows]
    maxmem = max((m for _, m in mrows), default=0)
    mchart = ""
    if maxmem:
        Mh = 3.4
        pts = [((i + 0.5) * (W / len(mrows)), Mh * m / maxmem) for i, (_, m) in enumerate(mrows)]
        poly = " -- ".join("(%.2f,%.2f)" % p for p in pts)
        area = (r"\fill[GBlue,opacity=0.10] (%.2f,0) -- %s -- (%.2f,0) -- cycle;"
                % (pts[0][0], poly, pts[-1][0]))
        line = r"\draw[GBlue,line width=1.4pt] %s;" % poly
        marks, mlabels = [], []
        for i, ((s, m), (x, y)) in enumerate(zip(mrows, pts)):
            c = CYCLE[i % 4]
            marks.append(r"\fill[white] (%.2f,%.2f) circle (3.6pt);"
                         r"\fill[%s] (%.2f,%.2f) circle (2.6pt);" % (x, y, c, x, y))
            mlabels.append(r"\node[font=\bfseries\small,color=Ink] at (%.2f,%.2f) {%s};"
                           % (x, y + 0.36, mem_tex(s) or "—"))
            mlabels.append(r"\node[font=\footnotesize,color=Slate] at (%.2f,-0.42) {%s};"
                           % (x, s["year"]))
        mchart = (r"\begin{center}\begin{tikzpicture}[x=1cm,y=1cm]"
                  + r"\draw[Line] (-0.1,0) -- (%.2f,0);" % (W + 0.1)
                  + area + line + "".join(marks) + "".join(mlabels)
                  + r"\end{tikzpicture}\end{center}")

    # ledger
    tr = []
    for i, (s, ne, inc, ft) in enumerate(rows):
        c = CYCLE[i % 4]
        evcell = str(ne) + (r"\;\textcolor{Slate}{\footnotesize+%d\,$\uparrow$}" % inc if inc else "")
        tr.append(
            r"\rule{0pt}{2.6ex}\textcolor{%s}{\rule[-0.2ex]{8pt}{8pt}}~\textbf{%s} & %s & %s & %s & %s & %s & %s \\[2pt]"
            % (c, s["year"], s["brand"], s["organiser"], s.get("core", "—"),
               mem_tex(s) or "—", evcell, f"{int(ft):,}"))
    table = (r"\renewcommand{\arraystretch}{1.15}"
             r"\begin{tabularx}{\linewidth}{@{}l l X c r r r@{}}"
             r"\multicolumn{7}{@{}l}{\footnotesize\color{Slate}\textsc{Season ledger}}\\[3pt]"
             r"\textbf{Season} & \textbf{Brand} & \textbf{Organiser} & \textbf{Core} & \textbf{Members} & \textbf{Events} & \textbf{Footfall}\\"
             r"\arrayrulecolor{Line}\hline\rule{0pt}{1ex}"
             + "".join(tr)
             + r"\hline\rule{0pt}{2.4ex}\textbf{Total} & & & & \textbf{%s} & \textbf{%d}%s & \textbf{%s}\\"
               % (mem_tex(SEASONS[-1]) if SEASONS else "—",
                  tot_ev, (r"\;\textcolor{Slate}{\footnotesize+%d\,$\uparrow$}" % tot_inc if tot_inc else ""),
                  f"{int(tot_ft):,}")
             + r"\end{tabularx}")

    return (r"""
% ============================== AT A GLANCE ==============================
\phantomsection\addcontentsline{toc}{section}{At a Glance (2022–26)}
\section*{\color{Ink}At a Glance \normalsize\color{Slate}(2022–26)}
\gbar[\linewidth]\\[12pt]
""" + tiles + r"""
\vspace{16pt}

{\bfseries\color{Ink}Events per season}\quad{\footnotesize\color{Slate}— cadence has grown every year, from 3 in the founding season to 19 in 2025–26.}
""" + chart + r"""
\vspace{14pt}

{\bfseries\color{Ink}Community growth}\quad{\footnotesize\color{Slate}— approximate registered membership at the close of each season, from a founding cohort of well under a hundred to around 1,800 today.}
""" + mchart + r"""
\vspace{10pt}
""" + table + r"""

\vspace{12pt}
{\footnotesize\color{Slate}\emph{Footfall} is cumulative event attendance across the season (range
midpoints where a range was recorded); attendees recur across events, so this counts participation,
not unique members.""" + (r" \;$\uparrow$\,denotes events scheduled but not yet held." if tot_inc else "") + r"""}
\clearpage
""")

def lineage():
    body = []
    for i, s in enumerate(SEASONS):
        c = CYCLE[i % 4]
        roll = s.get("roll", "")
        roll_tex = (r"\textbf{%s}" % roll) if roll else r"\rule[-2pt]{3.4cm}{0.4pt}"
        body.append(
            r"\item[\textcolor{%s}{\faCircle}] {\large\textbf{%s}}\;\textcolor{Slate}{\small(%s)}\\[3pt]"
            r"\textbf{%s} \;{\color{Slate}— %s}\\[3pt]"
            r"{\small\color{Slate}Roll No.~}%s\\[5pt]"
            r"{\small\color{Slate}%s}"
            % (c, s["year"], s["brand"], s["organiser"], s["role"], roll_tex, s["note"]))
    return (r"""
% ============================== LINEAGE ==============================
\phantomsection\addcontentsline{toc}{section}{Leadership Lineage}
\section*{\color{Ink}Leadership Lineage}
\gbar[\linewidth]\\[10pt]
{\color{Slate}Each organiser inherited a chapter and grew it. This is the chain of custody.}
\vspace{12pt}
\begin{itemize}[leftmargin=1.8em,itemsep=22pt,parsep=0pt,label=\textcolor{GBlue}{\faCircle}]
""" + "\n".join(body) + r"""
\end{itemize}
\clearpage
""")

def season_divider(s, idx):
    c = CYCLE[idx % 4]
    _, ne, inc, ft = season_stats(s)
    upcoming = (r" \quad\mbox{\faHourglassHalf~\textbf{%d} upcoming}" % inc) if inc else ""
    core = s.get("core")
    core_stat = (r" \quad\mbox{\faUserFriends~\textbf{%s} core}" % core) if core else ""
    mem = mem_tex(s)
    mem_stat = (r" \quad\mbox{\faUserPlus~\textbf{%s} members}" % mem) if mem else ""
    return (r"""
\clearpage
\phantomsection
\addcontentsline{toc}{section}{Season %s \textbullet\ %s}
\markboth{Season %s}{}
\begin{tcolorbox}[enhanced,colback=%s,colframe=%s,arc=6pt,
    left=18pt,right=18pt,top=12pt,bottom=12pt,fontupper=\color{white}]
  {\LARGE\bfseries %s}\hfill{\normalsize\itshape %s}\\[6pt]
  {\large Organiser \;\textbf{%s}}%s\\[8pt]
  {\small %s}\\[10pt]
  \textcolor{white}{\rule{\linewidth}{0.6pt}}\\[6pt]
  {\small\mbox{\faLayerGroup~\textbf{%d} events}%s%s%s \quad\mbox{\faUsers~\textbf{%s} footfall} \quad\mbox{\faTag~%s brand}}
\end{tcolorbox}
\vspace{5pt}
""" % (s["year"], s["organiser"], s["year"], c, c,
       s["year"], season_brand_name(s["brand"]),
       s["organiser"],
       (r"\;\textcolor{white!85}{\small(Roll No.\ %s)}" % s["roll"]) if s.get("roll") else "",
       s["note"], ne, upcoming, core_stat, mem_stat, f"{int(ft):,}", s["brand"]))

def gallery_caption():
    # styled rule first, then the label sits UNDER the rule — so the gallery is
    # unambiguously anchored to its event.
    return (r"\vspace{9pt}\noindent"
            r"{\color{Line}\rule{\linewidth}{0.7pt}}\\[4pt]"
            r"{\footnotesize\bfseries\color{Slate}\faImages~~EVENT GALLERY}"
            r"\hfill\raisebox{1pt}{\gbar[4.2cm]}\\[7pt]")

def gallery(e):
    n = e["n"]
    paths = event_images(n)
    if not paths:
        if e.get("status") == "upcoming":
            return (gallery_caption() + r"{\footnotesize\color{Slate}\faHourglassHalf~"
                    r"\emph{Gallery will be added after the event.}}")
        return (gallery_caption() + r"{\footnotesize\color{Slate}\faImage~"
                r"\emph{No gallery photo on record — drop images into }"
                r"\texttt{%s/%02d/}\emph{\ to populate.}}" % (GAL, n))
    if len(paths) == 1:
        body = (r"\begin{center}\begin{minipage}{0.62\linewidth}"
                r"\galimg{%s}\end{minipage}\end{center}" % paths[0])
        return gallery_caption() + body

    # masonry: balance columns by accumulated aspect height (shortest-column greedy)
    ncols = 2 if len(paths) <= 4 else 3
    cols = [[] for _ in range(ncols)]
    heights = [0.0] * ncols
    for p in paths:
        w, h = dims(p)
        ar = h / w
        j = heights.index(min(heights))
        cols[j].append(p)
        heights[j] += ar + 0.05
    mpw = {2: 0.485, 3: 0.315}[ncols]
    parts = []
    for col in cols:
        imgs = (r"\\[6pt]").join(r"\galimg{%s}" % p for p in col)
        parts.append(r"\begin{minipage}[t]{%s\linewidth}\centering %s \end{minipage}" % (mpw, imgs))
    return gallery_caption() + r"\noindent " + r"\hfill".join(parts)

def meta_row(icon, label, value):
    return (r"\textcolor{Slate}{\faIcon{%s}} & \textbf{%s} & %s \\[3pt]"
            % (icon, label, value))

def event_card(e, idx):
    c = CYCLE[(e["n"] - 1) % 4]
    upcoming = e.get("status") == "upcoming"
    badge = (r"\tikz[baseline]{\node[fill=%s,text=white,font=\bfseries\small,"
             r"rounded corners=3pt,inner xsep=6pt,inner ysep=2.5pt] {%02d};}" % (c, e["n"]))
    if upcoming:
        modebadge = (r"\tikz[baseline]{\node[fill=GYel,text=Ink,font=\footnotesize\bfseries,"
                     r"rounded corners=3pt,inner xsep=6pt,inner ysep=2.5pt] "
                     r"{\faHourglassHalf~Upcoming};}")
    else:
        mode = e.get("mode", "On-Site")
        mode_col = GGRN if mode == "On-Site" else GBLUE
        mode_icon = "map-marker-alt" if mode == "On-Site" else "wifi"
        modebadge = (r"\tikz[baseline]{\node[fill=%s,text=white,font=\footnotesize\bfseries,"
                     r"rounded corners=3pt,inner xsep=6pt,inner ysep=2.5pt] "
                     r"{\faIcon{%s}~%s};}" % (mode_col, mode_icon, mode))

    date = e.get("date", "—")
    venue = e.get("venue", "")
    date_val = date + (r"\,\textperiodcentered\," + venue if venue else "")
    att = e.get("att", "—")
    rows = [
        meta_row("calendar-alt", "Date", date_val),
        meta_row("clock", "Duration", e.get("dur", "—")),
        meta_row("microphone", "Speaker(s)", e.get("speakers", "—")),
        meta_row("handshake", "Partners", e.get("partners", "—")),
    ]
    if e.get("reg"):
        rows.append(meta_row("ticket-alt", "Registration", e["reg"]))
    if upcoming:
        rows.append(meta_row("info-circle", "Status", r"\textbf{Upcoming} — registrations open"))
    else:
        rows.append(meta_row("users", "Attendance",
                             (r"\textbf{%s} participants" % att) if att not in ("—", "") else "—"))
    metatable = (r"\renewcommand{\arraystretch}{1.05}"
                 r"\begin{tabularx}{\linewidth}{@{}c l X@{}}" + "".join(rows) + r"\end{tabularx}")

    blurb = e.get("blurb", "")
    blurb_tex = (r"{\small\color{Ink!85}%s}\\[9pt]" % blurb) if blurb else ""
    return (r"""
\phantomsection\addcontentsline{toc}{subsection}{%02d.~%s}
\begin{tcolorbox}[enhanced,breakable,colback=white,colframe=Line,boxrule=0.6pt,arc=5pt,
    left=14pt,right=14pt,top=12pt,bottom=12pt,
    borderline west={3.5pt}{0pt}{%s},before skip=8pt,after skip=12pt]
  {%s}\;\;{\large\bfseries\color{Ink}\truncate{0.66\linewidth}{%s}}\hfill %s\\[8pt]
  {\color{Line}\rule{\linewidth}{0.5pt}}\\[7pt]
  %s%s
  \vspace{4pt}
  %s
\end{tcolorbox}
""" % (e["n"], e["title"].replace("\\enquote{", "").replace("}", ""),
       c, badge, e["title"], modebadge, blurb_tex, metatable, gallery(e)))


def separator():
    return r"\vspace{1pt}\centerline{\gbar[6cm]}\vspace{6pt}"


def _tex_name(s):
    for a, b in (("\\", r"\textbackslash "), ("&", r"\&"), ("%", r"\%"),
                 ("#", r"\#"), ("_", r"\_"), ("$", r"\$")):
        s = s.replace(a, b)
    return s


def attendance_register(e):
    """Render an event's attendance roster from
    assets/attendance/<NN>/roster.csv (modular, like the gallery). Returns ""
    when no roster file is present, so only events with a sheet show one."""
    n = e["n"]
    path = os.path.join(BASE, "assets/attendance/%02d/roster.csv" % n)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    if len(rows) < 2:
        return ""
    data = rows[1:]  # skip header
    ncols = 3 if len(data) > 14 else 2
    entries = "\n".join(
        r"%s~\dotfill~\textbf{%s}\\" % (_tex_name(name.strip()), (year or "").strip())
        for name, year in ((r[0], r[1] if len(r) > 1 else "") for r in data))
    return (r"""\vspace{3pt}\noindent
{\footnotesize\bfseries\color{Slate}\faListOl~~ATTENDANCE REGISTER}%%
\hfill{\scriptsize\itshape\color{Slate}representative $\sim$50\%% sample \textperiodcentered\ %d names}\\[3pt]
{\color{Line}\rule{\linewidth}{0.5pt}}\\[5pt]
\begingroup\footnotesize\setlength{\columnsep}{20pt}\setlength{\parskip}{1pt}%%
\begin{multicols}{%d}\raggedright
%s
\end{multicols}
\endgroup
""" % (len(data), ncols, entries))

def closing():
    return r"""
% ============================== CLOSING ==============================
\clearpage
\phantomsection\addcontentsline{toc}{section}{Continuity \& Handover}
\section*{\color{Ink}Continuity \& Handover}
\gbar[\linewidth]\\[12pt]

\textbf{Ayushman Bhattacharya} carried this audit through the 2025–26 season. From here, the next
lead shall carry it on — appending each new season to the record and keeping it honest and current.

\vspace{18pt}
\begin{tcolorbox}[enhanced,colback=Mist,colframe=Mist,arc=5pt,left=16pt,right=16pt,top=14pt,bottom=16pt]
\begin{minipage}[t]{0.47\linewidth}
  {\footnotesize\color{Slate}\textsc{Initiated by}}\\[22pt]
  {\color{Line}\rule{\linewidth}{0.6pt}}\\[3pt]
  \textbf{Ayushman Bhattacharya}\\
  {\small\color{Slate}Organiser, GDG on Campus JIS University\\ Season 2025–26 \;\textperiodcentered\; Roll No.\ 23CS2021016}
\end{minipage}\hfill
\begin{minipage}[t]{0.47\linewidth}
  {\footnotesize\color{Slate}\textsc{Continued by}}\\[22pt]
  {\color{Line}\rule{\linewidth}{0.6pt}}\\[3pt]
  \textbf{\color{Slate}Next Organiser}\\
  {\small\color{Slate}Organiser, GDG on Campus JIS University\\ Season 2026–27 \;\textperiodcentered\; Roll No.\ \rule{2.6cm}{0.4pt}}
\end{minipage}
\end{tcolorbox}

\vfill
\begin{center}
  \devmark{0.9}\\[8pt]
  {\footnotesize\color{Slate} GDG on Campus JIS University \,\textperiodcentered\, Department of Computer Science \& Engineering}\\
  {\footnotesize\color{Slate} This is a living document — keep it alive.}
\end{center}
"""

def build():
    out = [PREAMBLE, r"\begin{document}", cover(), foreword(), dashboard(), lineage()]
    out.append(r"""
\phantomsection\addcontentsline{toc}{section}{Contents}
\section*{\color{Ink}Contents}
\gbar[\linewidth]\\[8pt]
\begingroup
\hypersetup{linkcolor=Ink}
\renewcommand{\contentsname}{}
\vspace{-3.4em}
\tableofcontents
\endgroup
\clearpage
""")
    for idx, s in enumerate(SEASONS):
        lo, hi = s["evs"]
        evs = [e for e in EVENTS if lo <= e["n"] <= hi]
        out.append(season_divider(s, idx))
        for e in evs:
            out.append(event_card(e, idx))
            out.append(attendance_register(e))
            out.append(separator())
    out.append(closing())
    out.append(r"\end{document}")
    return "\n".join(out)

if __name__ == "__main__":
    optimize_gallery()          # PNG/oversized -> capped JPEG, before layout
    with open(os.path.join(BASE, "dscjisu_report_21_26.tex"), "w") as f:
        f.write(build())
    print("wrote dscjisu_report_21_26.tex  (%d events, %d seasons)" % (len(EVENTS), len(SEASONS)))
