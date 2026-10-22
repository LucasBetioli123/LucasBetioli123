# Visual GitHub profile

The profile is published at <https://github.com/LucasBetioli123> from this repository’s root `README.md`.

## Content and design

- `README.md`: compact English profile, project links, contact links and an expandable research note.
- `assets/*-v2.svg`: header, qualifications, technology logos, project illustrations and public GitHub data cards.
- `scripts/build_visual_profile.py`: manually generates the current visuals.
- `scripts/build_profile.py`: provides the GitHub data collection functions used by the visual generator; it can also generate the earlier visual assets.

## Refresh the current visuals

Use Python 3.10 or newer. Only the standard library is needed.

```bash
python3 scripts/build_visual_profile.py
git add assets/*-v2.svg
git commit -m "Refresh visual profile"
git push
```

The generator uses GitHub’s public APIs and contribution calendars, and downloads vector technology logos from Devicon. It fetches no private repository source or employer project names. An optional `GH_TOKEN` can enable GraphQL for the contribution calendar; do not commit any token.

There is no active scheduled workflow. Charts show the snapshot date printed on the GitHub card.

## Data interpretation

- Repository and pull request counts are public GitHub data for this account.
- Contributions cover the current and previous calendar years. The current month is partial.
- Language percentages aggregate GitHub-reported bytes from original public repositories, excluding forks and this profile repository.
- GitHub classifies notebook files as **Jupyter Notebook**, even when their cells contain Python. This chart does not measure language proficiency.
- Project illustrations are conceptual visuals, not screenshots or model evaluation results.

## Credits

Most technology logos are from [Devicon](https://github.com/devicons/devicon), used under its MIT license. See `assets/devicon-LICENSE.txt`. CUDA uses the NVIDIA brand mark distributed by [Simple Icons](https://github.com/simple-icons/simple-icons) under CC0. The VTK logo is by Steve Jordan / Kitware and is sourced from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Visualization_Toolkit_logo.svg), which identifies it as a public-domain text logo. VTK also provides its logo on [its official website](https://vtk.org/about/#logos). Original names, logos and trademarks belong to their respective owners.
