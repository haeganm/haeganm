# Hey, I'm Haegan 👋

**AI & Cloud Engineering · Quant Research & Fintech**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Haegan_McGarry-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/haegan-mcgarry-90aa43392)
[![Email](https://img.shields.io/badge/Email-haeganm%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:haeganm@gmail.com)

## About Me

I build AI systems and the infrastructure they run on, aimed at making capital and markets smarter. Machine learning and applied AI are the center of my work — I design and ship **LLM agent systems** and automation that turn messy real-world data into decisions.

Python is my daily language, I build with modern AI tooling, and I deploy through containerized, cloud-based workflows (**AWS Cloud Practitioner in progress**). I treat security as part of the build, not an afterthought: on-device processing, OAuth, and careful handling of tokens and secrets.

I approach quantitative research and trading as an engineering problem: **form a thesis, dig for evidence, stress the downside, and let the data settle it.**

Open to opportunities with quant desks, hedge funds, and cloud/AI engineering teams.

## Tech Stack

**AI & Agents**

![Claude Code](https://img.shields.io/badge/Claude_Code-D97757?style=flat-square&logo=claude&logoColor=white)
![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Whisper](https://img.shields.io/badge/Whisper-000000?style=flat-square&logo=openai&logoColor=white)
![Vosk](https://img.shields.io/badge/Vosk-4B8BBE?style=flat-square)

**Languages**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![C](https://img.shields.io/badge/C-A8B9CC?style=flat-square&logo=c&logoColor=black)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

**Cloud & DevOps**

![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)

**Backend & Data**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![OAuth PKCE](https://img.shields.io/badge/OAuth_PKCE-EB5424?style=flat-square&logo=auth0&logoColor=white)

## Featured Projects

### [Retro](https://github.com/haeganm/retro-spotify-voice-remote) — offline voice AI remote for Spotify Premium

A voice remote that runs entirely on-device: speech is processed locally with Vosk and Whisper (~150 ms on GPU), keeping it private and fast. Uses OAuth PKCE with secure on-device token storage, personalized fuzzy matching against your own artists, playlists, and liked songs, and a Windows system-tray UX with a one-command installer. Zero cloud, zero cost.

`Python` `Vosk` `faster-whisper` `OAuth PKCE` `spotipy`

### [mlrisk](https://github.com/haeganm/mlrisk) — zero-dependency C11 quant library

Volatility and risk primitives written from scratch in C11: GARCH(1,1) and range-based volatility estimators, Kelly and vol-target position sizing, and purged/embargoed walk-forward evaluation. Sanitizer-clean CI on Windows, macOS, and Linux.

`C11` `GARCH` `walk-forward validation` `GitHub Actions`

### [EatTube](https://github.com/haeganm/EatTube) — slot machine for your watch-while-eating video

A Chrome extension that spins slots to pick a YouTube video to watch while you eat. Because deciding is the hardest part of the meal.

`JavaScript` `Chrome Extensions API`

## Beyond GitHub — systems I've built

Selected private work (code not public):

**Density** — Autonomous quantitative trading system for prediction markets that prices contracts from probability distributions rather than opinions. Extracts probability densities from external reference markets and trades the gap through a risk layer nothing else in the system can override. Probability model calibrated on 1,076 days of history with 94.9% observed coverage on a 95% interval; the deployed strategy produced a **1.3 Sharpe ratio with an 8.6% max drawdown across 720 live trades**. Includes walk-forward validation, historical fill modeling, a 112-check test suite, crash recovery, watchdog orchestration, a live dashboard, and an LLM review layer.

**Docket** — Multi-tenant AI platform that turns documents into structured, trustworthy data. Organizations define their own extraction schemas and get back exact fields, each with a confidence score and a citation to source text; low-confidence results route to a human. Runs as an event-driven serverless pipeline across **13 AWS services**, from a Cognito-secured API to Bedrock for inference, with tenant isolation built into the data model. Zero idle cost; ships with 49 tests, credential-free CI, and five rounds of security auditing.

**BlotterBrain** — LLM-powered, hedge-fund-style research workflow in Python. A single ticker triggers a multi-agent research team — analysts, bull/bear researchers, research manager, trader, risk analysts, portfolio manager — that produces a full investment memo with debate logs, risk review, and a final buy/hold/sell call. Logs each thesis, benchmarks against SPY, and feeds results into future runs. Backtests produced a **37.8% annualized return with a 71.4% win rate**. (Forked from TradingAgents.)

## Experience & Education

- **Collaborator / Apprentice — Riffyx Labs Mentorship** (Jun 2025 – Jun 2026): AWS fundamentals, debugging, and Git-based workflows (branches, pull requests); worked alongside Cisco professionals on implementation tasks.
- **B.S. Computer Science — California State University San Marcos** (2025 – present)

## Certifications

- Anthropic certified
- OpenAI — *Agents and Workflows* and *Applied AI Foundations*
- AWS Cloud Practitioner (in progress)

## GitHub Stats

![Haegan's GitHub stats](https://github-readme-stats.vercel.app/api?username=haeganm&show_icons=true&hide_border=true&rank_icon=github)
![Top languages](https://github-readme-stats.vercel.app/api/top-langs/?username=haeganm&layout=compact&hide_border=true)

## Connect

Looking for opportunities with quant desks, hedge funds, and cloud/AI engineering teams. Reach me on [LinkedIn](https://www.linkedin.com/in/haegan-mcgarry-90aa43392) or at [haeganm@gmail.com](mailto:haeganm@gmail.com).
