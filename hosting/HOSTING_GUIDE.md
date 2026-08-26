# Hosting your synthetic population explorer

You built a real thing: a generator that manufactures a fake patient population in
Synthea's exact data shape, and an explorer that profiles it - population stats,
per-patient timelines, and the anatomy of a FHIR bundle. Right now it only runs when
you type a command on your laptop. "Hosting" just means putting the pieces somewhere
they keep working when your machine is asleep - and, just as importantly, somewhere
you can send a recruiter a link.

There are three pieces, and they live in three free places:

1. The **code** lives on GitHub. That's storage plus version history for your files,
   and it's the thing you link to on a CV.
2. A **live interactive demo** lives on Streamlit Community Cloud. Streamlit turns
   your Python into a small web app; Community Cloud hosts it for free and gives you
   a public URL anyone can click. They pick a population size, hit Generate, and
   watch your generator invent patients and your explorer profile them - no install.
3. The **tests** run in GitHub Actions. Every time you push, GitHub spins up a
   temporary Linux box, runs `pytest`, and shows a green check (or a red X) so you -
   and anyone reading your repo - can see the code actually works.

All three are free at this size. You will not put in a credit card.

## Read this first: why it's safe to host this in public

The patients in this project do not exist. They are invented by the `synthea_mini`
generator using the Faker library - random names, random birthdates, random visits.
There is no real patient data (no PHI) anywhere in this repo, so there is nothing
private to leak. That is exactly why you can put it on free public hosting.

Make this a habit now, because it's the rule that matters most in health tech:

> Synthetic data only. You build and demo on invented patients. You would never put
> real PHI on free public hosting - that would need a BAA-covered environment (a
> provider who has signed a contract making themselves legally responsible for the
> data, like a locked-down AWS/GCP/Azure setup). No real patients here, so no problem.

Being able to say that sentence out loud is a hiring signal. It tells an interviewer
you understand not just the code but the rules around the data. The same habit shows
up in your `.gitignore`, which keeps generated data files out of the repo even though
they're fake - see Step 1.

---

## Step 1 - Put the code on GitHub

GitHub is where the code lives. First you make a local Git repo, then you make an
empty repo on the website, then you connect the two and push.

### 1a. Check Git knows who you are

Only needed once per machine. If you've committed before, skip it.

```powershell
git config --global user.name "Your Name"
git config --global user.email "mathuransada@gmail.com"
```

### 1b. The .gitignore - read this part, it's the one that bites people

In a health-tech project, the cardinal sin is committing data. Synthetic or not, you
want "generated data never goes in Git" to be muscle memory now, so that the day you
touch real PHI you don't even have to think about it. `build_from_scratch/` already
ships a `.gitignore`. Open it and confirm it contains at least these lines:

```
data/output/
out/
*.zip
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ipynb_checkpoints/
```

Why these matter:

- `data/output/` and `out/` and `*.zip` - the populations you generate locally never
  get committed. The repo ships one tiny committed sample under `data/sample/` on
  purpose (the app doesn't even need it - it generates fresh data on the fly), but
  everything else you generate stays on your laptop. Clean repo, right habit.
- `.env` - if you ever add a secret, it goes here, and this line keeps it off the
  internet. Git keeps history forever, so a secret committed once is a secret leaked
  forever, even if you "delete" it in a later commit.

One thing to know about this project: it has no secrets and no database. The app
generates its data in memory every time it loads. So unlike Project 1, there's no
`DB_URL` or salt to manage - nothing to put in GitHub Secrets. One less thing to get
wrong.

### 1c. Decide what to push - push the whole project folder

The simplest, cleanest option is to make the **whole project folder**
(`02_synthetic_patients_synthea/`) one repo. That way `hosting/` and
`build_from_scratch/` sit together exactly as the app expects: the Streamlit app
reaches from `hosting/streamlit_app/app.py` up two levels and into
`build_from_scratch/` to import your `synthea_mini` and `synthea_explorer` packages.

If you push only `build_from_scratch/` on its own, the Streamlit app won't find the
code and the deploy will fail. So push from the project root.

> If the project root doesn't have its own `.gitignore`, copy the one from
> `build_from_scratch/` up to the root, or just make sure the rules in 1b are in
> effect from wherever you run `git init`.

### 1d. Initialize, stage, commit

From the project root (`02_synthetic_patients_synthea/`):

```powershell
git init
git add .
git commit -m "Initial commit: synthetic patient generator + explorer + hosting"
```

`git add .` stages everything that isn't ignored. Now the critical sanity check:

```powershell
git status
```

Confirm you do **not** see `.env`, any large generated CSVs under `data/output/`, or a
`.venv/` folder listed. If a generated file shows up as staged, your `.gitignore`
isn't catching it - run `git rm --cached the_file`, fix the ignore rule, and commit
again. Do this before you push, not after.

### 1e. Make the empty repo on github.com

In the browser:

1. Go to github.com, sign in (create the account first if you haven't).
2. Top-right, click the **+** then **New repository**.
3. Name it something like `synthetic-patients-synthea`. Lowercase, hyphens, no spaces.
4. Leave it **Public** - you want recruiters to see it, and public repos get
   unlimited free GitHub Actions minutes.
5. Do **not** check "Add a README", "Add .gitignore", or "Add a license". You want
   it completely empty, otherwise your first push hits a conflict. Leave all boxes off.
6. Click **Create repository**.

GitHub then shows a page with commands. Ignore most of it and use what's below.

### 1f. Connect and push

Copy the repo URL from that page (the
`https://github.com/yourname/synthetic-patients-synthea.git` one). Then:

```powershell
git remote add origin https://github.com/YOURNAME/synthetic-patients-synthea.git
git branch -M main
git push -u origin main
```

The first push pops a browser window or a credential prompt to log into GitHub. Do
it. If it asks for a password in the terminal, that won't work anymore - GitHub
killed password auth. Use the browser sign-in it offers, or a Personal Access Token
as the password. The browser flow is easier.

Refresh the GitHub page. Your files are there. The code is hosted. One piece down.

---

## Step 2 - Deploy the live demo to Streamlit Community Cloud

This is the fun part: a public URL where anyone can pick a population size, hit
Generate, and watch your project invent and profile patients in real time. The app
file is already written - it's `hosting/streamlit_app/app.py`. It imports your real
`synthea_mini` and `synthea_explorer` packages, generates a population, shows the
summary metrics and charts, lets you pick a patient and see their timeline, and
builds that patient's FHIR bundle. You just have to point Streamlit at it.

The official walkthrough is here and worth a skim:
https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started

### 2a. Sign in

1. Go to https://share.streamlit.io and click **Continue with GitHub**.
2. Authorize Streamlit to see your repos. (It needs read access to deploy from them.)

Signing in with the same GitHub account you just pushed to means Streamlit can see
your new repo immediately.

### 2b. Create the app

1. Click **Create app** (sometimes labelled "New app").
2. Choose **Deploy a public app from GitHub** / "Use existing repo".
3. Fill in the three fields:
   - **Repository:** `YOURNAME/synthetic-patients-synthea`
   - **Branch:** `main`
   - **Main file path:** `hosting/streamlit_app/app.py`

   That main file path is the one people get wrong. It is the path **inside your
   repo** to the app script. Type it exactly: `hosting/streamlit_app/app.py`. If you
   pushed only the `build_from_scratch` folder instead of the whole project, this
   path won't exist and the deploy will fail - that's the reason Step 1 said push
   from the project root.

4. Click **Deploy**.

### 2c. What happens next

Streamlit reads `hosting/streamlit_app/requirements.txt`, installs streamlit,
pandas, and Faker on its server, then runs your app. The first build takes a couple
of minutes - you'll see a log scrolling. When it finishes you get a public URL like
`https://your-app-name.streamlit.app`. Open it. You should land on a populated page
straight away (the app generates 25 patients by default so it's never blank), with
the summary metrics, the two charts, a patient timeline, and a FHIR bundle showing a
green **PASS** on the reference check.

That URL is shareable. Send it to anyone. It is, genuinely, your project running on
the internet.

### 2d. If the deploy goes red

Click into the log; the real error is usually near the bottom.

- `ModuleNotFoundError: No module named 'synthea_mini'` (or `synthea_explorer`) - the
  repo doesn't contain `build_from_scratch/`, or you deployed from the wrong folder.
  The app reaches from `hosting/streamlit_app/app.py` up two levels and into
  `build_from_scratch/` to find those packages. Both folders must be in the same
  repo. Push from the project root and redeploy.
- `ModuleNotFoundError: No module named 'faker'` (or pandas) - a package is missing
  from `hosting/streamlit_app/requirements.txt`. Add it, push, and Streamlit
  redeploys automatically on the next push.
- "main file not found" - the **Main file path** is wrong. It must be
  `hosting/streamlit_app/app.py`, spelled exactly.

Every time you push to `main`, Streamlit redeploys on its own. No need to click
anything after the first time.

---

## Step 3 - Turn on CI (run the tests automatically)

Your `build_from_scratch/` folder has a pytest suite (around 12 tests). Right now
those only run when you type `pytest`. GitHub Actions runs them for you on every
push, on GitHub's machines, for free, and shows a green check on your repo when they
pass. That green check is what turns "I wrote some code" into "I wrote tested code."

### 3a. Put the workflow file in the right place

A workflow only runs if it lives at `.github/workflows/` in your repo. This hosting
folder ships a ready-made one at `hosting/github_actions/tests.yml`. Copy it to the
real location:

```powershell
mkdir .github\workflows
copy hosting\github_actions\tests.yml .github\workflows\tests.yml
```

Then commit and push:

```powershell
git add .github\workflows\tests.yml
git commit -m "Add CI: run pytest on every push"
git push
```

### 3b. What the workflow does

Open the file and read the comments - it's deliberately written to be read. In
short, on every push or pull request (and on demand from the Actions tab) it:

1. Checks out your code onto a fresh Ubuntu box.
2. Installs Python 3.12.
3. Installs `build_from_scratch/requirements.txt` (pandas, Faker, pytest).
4. Runs `pytest -v` inside `build_from_scratch/`.

The `working-directory: build_from_scratch` line on the install and test steps is the
important detail: it tells the runner to stand inside that folder, because that's
where the packages and the `tests/` folder live. Run pytest from the repo root and it
wouldn't find them.

If every test passes, the run is green. If one fails, it goes red and GitHub emails
you.

### 3c. Watch it run, then add the badge

1. Go to your repo's **Actions** tab. You'll see a run already going (the push
   triggered it).
2. Click into it, click the **pytest** job, and watch the steps expand live. Green
   check means it worked. Click any step to read its log.

Now add a **status badge** to your README - the little "Tests: passing" image. It's
the first thing a recruiter's eye lands on. On the Actions page, click your "Tests"
workflow, then the `...` menu, then **Create status badge**, and copy the Markdown.
It looks like this (swap in your username and repo):

```markdown
![Tests](https://github.com/YOURNAME/synthetic-patients-synthea/actions/workflows/tests.yml/badge.svg)
```

Paste that at the top of your README. Now anyone landing on your repo sees, at a
glance, that the tests pass.

Full Actions docs if you want to go deeper: https://docs.github.com/actions

### 3d. The free-minutes thing, briefly

Public repos get **unlimited** free Actions minutes, so you never have to think
about this. (Private repos get a couple thousand minutes a month, which a test run
like this barely dents.) This workflow runs on push, not on a schedule, so it just
runs whenever you push. Nothing to manage.

---

## What to put in your README and show a recruiter

When you write the repo's README, describe it as what it is: a Java-free synthetic
patient generator that writes data in Synthea's exact CSV schema and FHIR R4 shape,
plus an explorer that profiles the population (demographics, utilisation, top
conditions and medications), reconstructs one patient's timeline across files, and
takes a FHIR bundle apart to check its references resolve. Put these at the top:

- The **tests badge** (Step 3c).
- A link to the **live Streamlit demo**.
- The **synthetic-data sentence** (synthetic data only; free hosting isn't
  BAA-covered; real PHI would need a BAA-covered environment). This one line does a
  lot of work.

In an interview, the points that land:

- **You know the EHR data model.** You can explain how Patient, Encounter, Condition,
  Observation, and MedicationRequest hang off each other by id, and that a FHIR
  Bundle wires them with references that should all resolve internally - your explorer
  literally checks that and the demo shows the PASS.
- **You know the coding systems.** SNOMED CT for conditions and procedures, LOINC for
  observations, RxNorm for medications, CVX for vaccines - the same vocabularies real
  systems use, and your generator emits real codes from them.
- **You handle data correctly.** Synthetic only, generated populations are
  gitignored, and you know real PHI needs a BAA-covered environment, not free public
  hosting.
- **It's real and runnable.** There's a live demo a recruiter can click and a CI
  badge proving the tests pass. And you can add: the mini generator is a faithful
  *schema* twin of Synthea, so the very same explorer code runs unchanged on real
  Synthea output - which you can generate by following `run_real_synthea.md`. That's
  the difference between a toy and a project.

Have the live demo open in a tab during the call. Picking a patient and showing their
timeline and FHIR bundle resolve in real time beats any amount of describing it.

Real Synthea, if you want to go deeper: https://synthetichealth.github.io/synthea/
