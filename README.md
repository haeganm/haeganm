# Haegan McGarry

**CS student building cloud systems and measuring them honestly. Looking for a 2026 SWE internship: cloud, infrastructure, security.**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Haegan_McGarry-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/haegan-mcgarry-90aa43392)
[![Email](https://img.shields.io/badge/Email-haeganm%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:haeganm@gmail.com)
![AWS CCP](https://img.shields.io/badge/AWS-Certified_Cloud_Practitioner-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)

## What I do

I build systems end to end, deploy them on AWS, test them, and write down what the numbers actually say. Every figure below links to the code, the CI run or the merged PR that backs it. If a project did not work, its README says so.

Python daily. AWS SAM, Step Functions, Lambda, DynamoDB, IAM. C when speed matters. GitHub Actions for every repo.

## Featured

### [Agentic NetOps](https://github.com/haeganm/agentic-netops): closed-loop network remediation on AWS

A serverless platform that heals a VPC when it drifts from declared intent. DETECT, PROVE, MEASURE, GENERATE-REPAIR, APPROVE, EXECUTE, VERIFY. The LLM proposes, deterministic systems dispose: control flow runs on config diffs, never on model output. Repairs are bounded to converge-to-baseline by a versioned policy gate, routed through fail-closed autonomy tiers (auto-execute behind a veto window, single approval, or two-party maker-checker), and executed under per-incident scoped STS credentials. Every decision lands in a hash-chained ledger anchored out of band.

Measured live: self-healed a seeded fault in 191 s with no human touch, 9 of 9 fault classes remediate, 155 tests in credential-free CI, 17 architecture decision records, repeated adversarial security audits with the findings register in `docs/SECURITY.md`, $0 idle.

`AWS SAM` `Step Functions` `Lambda` `DynamoDB` `EventBridge` `Cognito` `Bedrock` `IAM` `CloudFront`

### [walkforward](https://github.com/haeganm/walkforward): volatility, sizing and purged walk-forward splits, in C11 with a Python front door

[![PyPI](https://img.shields.io/pypi/v/walkforward?style=flat-square)](https://pypi.org/project/walkforward/) `pip install walkforward`

GARCH(1,1), EWMA and range-based volatility, Kelly and vol-target sizing, purged walk-forward splits and ridge regression, written from scratch in C11 with a ctypes binding over numpy and pandas. CI runs gcc, clang, macOS, Windows, 32-bit, sanitizers and a fuzz sweep, then checks the C against pandas, numpy, scikit-learn and arch. Wheels for five platforms ship through cibuildwheel and PyPI trusted publishing, no token anywhere. The worked SPY example in the README reports the honest out-of-sample numbers, including the ones that did not help.

`C11` `CMake` `ctypes` `cibuildwheel` `GitHub Actions` `PyPI trusted publishing`

### [Retro](https://github.com/haeganm/retro-spotify-voice-remote): offline voice remote for Spotify

Speech never leaves the machine: Vosk and faster-whisper on the GPU, your own artists and playlists injected into the recognizer vocabulary, OAuth PKCE with tokens stored on device, a Windows tray app with a one-command installer.

`Python` `Vosk` `faster-whisper` `OAuth PKCE`

## Open source

Merged upstream, each one a reproduced bug with a failing test first:

| Repo | PR | Fix |
|---|---|---|
| statsmodels | [#10229](https://github.com/statsmodels/statsmodels/pull/10229) | Probit log-likelihood, score and Hessian computed in log space so extreme fitted values stop underflowing |
| nautilus_trader | [#4914](https://github.com/nautechsystems/nautilus_trader/pull/4914) | AroonOscillator lowest-low scan and tie handling |
| moto | [#10234](https://github.com/getmoto/moto/pull/10234) | SQS raises `PurgeQueueInProgress` on a repeated purge within 60 s, matching AWS |
| pandas_market_calendars | [#485](https://github.com/rsheftel/pandas_market_calendars/pull/485) | TASE calendar updated for the Monday to Friday trading week |
| anndata | [#2652](https://github.com/scverse/anndata/pull/2652) | Raise on float index arrays with non-integer values instead of silently truncating |
| scikit-bio | [#2580](https://github.com/scikit-bio/scikit-bio/pull/2580) | `to_indices` and `to_cigar` on single-segment alignment paths |
| PyLabRobot | [#1273](https://github.com/PyLabRobot/pylabrobot/pull/1273) | Serialize `Container.no_go_zones` so `copy()` and `deserialize()` keep them |

Open: [mypy #21926](https://github.com/python/mypy/pull/21926) (error on irrefutable match patterns that make later cases unreachable), [biotite #946](https://github.com/biotite-dev/biotite/pull/946) (CONECT records across insertion codes).

## Shipped to real users

Five public Roblox games with live players, persistent saves and paid products, built with Rojo and a git workflow. [Roblox profile](https://www.roblox.com/users/9068682769/profile).

## Education and certifications

- B.S. Computer Science, California State University San Marcos, 2026 to present
- AWS Certified Cloud Practitioner
- Collaborator and apprentice, Riffyx Labs mentorship (Jun 2025 to Jun 2026): AWS fundamentals, debugging and Git workflows alongside Cisco professionals
