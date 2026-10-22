# GitHub profile

The English profile is published at <https://github.com/LucasBetioli123> from the root `README.md`.

## Current layout

- A short introduction and qualifications.
- Technology logos grouped into languages, AI/GPU/visualization, and backend/cloud.
- A project table with links to Poligome and InVesalius.
- Conventional GitHub Stats and Streak Stats cards, plus a monthly public contribution chart.

The two remote statistics cards refresh through their image services, subject to GitHub's image caching. They use public account data and do not measure skill proficiency. The monthly chart is a dated snapshot of publicly visible contributions; the current month is partial.

## Refresh the monthly chart

Python 3.10+; standard library only:

```bash
python3 scripts/build_classic_profile.py
git add assets/contributions-classic.svg
git commit -m "Refresh public contribution chart"
git push
```

There is no active scheduled workflow. Earlier visual generators and SVGs remain as previous designs; the current README uses only the assets named `*-classic.svg` and the two statistics services.

## Credits

- The language, AI framework and cloud icon strips are from [Skill Icons](https://github.com/tandpfun/skill-icons), under its MIT license. See `assets/skill-icons-LICENSE.txt`.
- CUDA uses the NVIDIA mark from [Simple Icons](https://github.com/simple-icons/simple-icons), under CC0.
- The VTK logo by Steve Jordan / Kitware is sourced from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Visualization_Toolkit_logo.svg), identified there as a public-domain text logo. [VTK also distributes its logos](https://vtk.org/about/#logos).
- Live cards: [GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats) and [GitHub Readme Streak Stats](https://github.com/DenverCoder1/github-readme-streak-stats).
- Previously used Devicon logos retain their MIT notice in `assets/devicon-LICENSE.txt`.

Names, logos and trademarks belong to their respective owners.
