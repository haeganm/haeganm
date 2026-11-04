# Haegan McGarry

**CS student building cloud systems and measuring them honestly. Looking for a SWE internship: cloud, infrastructure, security.**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Haegan_McGarry-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/haegan-mcgarry-90aa43392)
[![Email](https://img.shields.io/badge/Email-haeganm%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:haeganm@gmail.com)
![AWS CCP](https://img.shields.io/badge/AWS-Certified_Cloud_Practitioner-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)

## What I do

I build systems end to end, deploy them on AWS, test them, and write down what the numbers actually say. Every number on this page comes from a test run, a live measurement or a merged PR you can open. If a project did not work, its README says so in the first paragraph.

Python daily. AWS SAM, Step Functions, Lambda, DynamoDB, IAM. C when speed matters. CI on every repo.

## Featured

### [Agentic NetOps](https://github.com/haeganm/agentic-netops): closed-loop network remediation on AWS

A serverless platform that heals a VPC when it drifts from declared intent: detect, prove, measure, generate a repair, approve, execute, verify. The LLM proposes and deterministic systems dispose, so control flow runs on config diffs and never on model output. Repairs are bounded to converge-to-baseline by a versioned policy gate, routed through fail-closed autonomy tiers (auto-execute behind a veto window, one approval, or two-party maker-checker), and executed under per-incident scoped STS credentials. Every decision lands in a hash-chained ledger anchored out of band.

- Measured on the live deployment: self-healed a seeded fault in 191 s with no human touch, and all 9 seeded fault classes remediate.
- 155 tests in credential-free CI, 17 architecture decision records, a security findings register from repeated adversarial audits, $0 idle.

`AWS SAM` `Step Functions` `Lambda` `DynamoDB` `EventBridge` `Cognito` `Bedrock` `IAM` `CloudFront`

### [walkforward](https://github.com/haeganm/walkforward): volatility, sizing and purged walk-forward splits in C11, with a Python front door

[![PyPI](https://img.shields.io/pypi/v/walkforward?style=flat-square)](https://pypi.org/project/walkforward/) `pip install walkforward`

GARCH(1,1), EWMA and range-based volatility, Kelly and vol-target sizing, purged walk-forward splits and ridge regression, written from scratch in C11 with a ctypes binding over numpy and pandas. A 12-job CI matrix runs gcc, clang, macOS, Windows, 32-bit, sanitizers and a fuzz sweep, then checks the C against pandas, numpy, scikit-learn and arch. Wheels for five platforms ship through cibuildwheel and PyPI trusted publishing, with no token anywhere. The worked SPY example reports honest out-of-sample numbers, including the ones that did not help.

`C11` `CMake` `ctypes` `cibuildwheel` `GitHub Actions` `PyPI trusted publishing`

### [Retro](https://github.com/haeganm/retro-spotify-voice-remote): offline voice remote for Spotify

Speech never leaves the machine: Vosk and faster-whisper on the GPU, your own artists and playlists injected into the recognizer vocabulary, OAuth PKCE with tokens stored on device, and a Windows tray app with a one-command installer.

`Python` `Vosk` `faster-whisper` `OAuth PKCE`

## Measured, then retired

Three quant systems, each built to find out whether an edge existed, each shut down by its own pre-committed gate. The READMEs lead with the negative result.

- **[density-desk](https://github.com/haeganm/density-desk):** an autonomous Kalshi trading desk that tested three hypotheses against live markets with real money. All three failed, for about $6 in realized losses. 112 tests.
- **[technical-engine](https://github.com/haeganm/technical-engine):** a 506-ticker intraday scanner with Discord alerts and a look-ahead-safe backtest. 5,400 alerts over 60 sessions came to -748R, and three rescue hypotheses were tested and rejected. 99 tests.
- **[alphaos](https://github.com/haeganm/alphaos):** a $0 point-in-time alpha research lab with an append-only trial ledger and Deflated Sharpe. 8 campaigns, 34 pre-registered hypotheses, 0 survivors. 107 tests.

## Open source

Merged upstream:

| Repo | PR | Fix |
|---|---|---|
| moto | [#10234](https://github.com/getmoto/moto/pull/10234) | SQS raises `PurgeQueueInProgress` on a repeated purge within 60 s |
| statsmodels | [#10229](https://github.com/statsmodels/statsmodels/pull/10229) | Probit log-likelihood, score and Hessian computed in log space |
| nautilus_trader | [#4914](https://github.com/nautechsystems/nautilus_trader/pull/4914) | AroonOscillator lowest-low scan and tie handling |
| pandas_market_calendars | [#485](https://github.com/rsheftel/pandas_market_calendars/pull/485) | TASE calendar updated for the Monday to Friday trading week |
| anndata | [#2652](https://github.com/scverse/anndata/pull/2652) | Raise on float index arrays with any non-integer value |
| scikit-bio | [#2580](https://github.com/scikit-bio/scikit-bio/pull/2580) | `to_indices` and `to_cigar` on single-segment alignment paths |
| PyLabRobot | [#1273](https://github.com/PyLabRobot/pylabrobot/pull/1273) | Serialize `Container.no_go_zones` so `copy()` and `deserialize()` keep them |

In review: [mypy #21926](https://github.com/python/mypy/pull/21926) (report irrefutable match patterns that make later cases unreachable) and [biotite #946](https://github.com/biotite-dev/biotite/pull/946) (CONECT records for bonds across insertion codes).

## Shipped to real users

Five public Roblox games, built with Rojo, Studio automation and git. [Roblox profile](https://www.roblox.com/users/9068682769/profile).

## Education and certifications

- B.S. Computer Science, California State University San Marcos, 2026 to present
- AWS Certified Cloud Practitioner
- Collaborator and apprentice, Riffyx Labs mentorship (Jun 2025 to Jun 2026): AWS fundamentals, debugging and Git workflows alongside Cisco professionals
