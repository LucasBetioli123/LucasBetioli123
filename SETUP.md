# Publish this GitHub profile

Everything displayed in the profile is in English. The visual assets are custom SVGs, with separate light and dark versions. Charts are generated locally and committed to the repository, so viewing the profile does not depend on a third-party stats service.

## Upload

1. Create a **public** repository named **LucasBetioli123** under **LucasBetioli123**. A profile README requires the repository name to match the username exactly. The existing `LucasBetioli` repository has a different name.
2. Upload the contents of this package into its root. Keep `assets`, `scripts`, and `.github/workflows` in their original locations. The root must contain `README.md`.
3. Commit the files. The README will appear at <https://github.com/LucasBetioli123>.
4. Open **Actions → Refresh profile charts → Run workflow**. The workflow also runs daily at 08:23 UTC. No personal access token or paid service is required; it uses the repository’s automatic GitHub token.

If browser upload does not preserve `.github/workflows`, add `.github/workflows/profile.yml` using **Add file → Create new file**, then paste the supplied YAML. Repository rules may require approving the workflow or allowing GitHub Actions to write to the repository.

## Upload with GitHub CLI instead

From the extracted package directory, with `gh` authenticated to your account:

```bash
git init -b main
git add README.md assets scripts .github SETUP.md
git commit -m "Create custom English profile"
gh repo create LucasBetioli123/LucasBetioli123 --public --source=. --remote=origin --push
gh workflow run profile.yml --repo LucasBetioli123/LucasBetioli123
```

If the repository already exists, use a normal clone and commit rather than the creation commands. Do not overwrite an existing README without reviewing it.

## Charts and interpretation

- **Activity:** daily contribution counts for the current and previous calendar years, grouped by month. GitHub defines contribution eligibility and visibility. The current month is partial.
- **Languages:** GitHub language bytes aggregated across public repositories owned by the account, excluding forks and this profile repository. Notebook files are reported as **Jupyter Notebook** by GitHub, even when they contain Python.
- **Fork count:** context about the public repository collection; a fork is not presented as an original project.
- **Initial snapshot:** generated from the public GitHub endpoints on the date printed in the charts. The generator refuses incomplete data rather than inventing missing values.
- **Refresh:** uses the GraphQL contribution calendar when the automatic token is available, with a public calendar fallback. Only public repository metadata and language totals are requested. No repository source files, employer code, or private project names are collected.
- **Failure behavior:** generation validates all fetched inputs before replacing chart files. A failed refresh leaves the previous committed charts intact and fails the workflow visibly.

To regenerate manually with Python 3.10+:

```bash
python3 scripts/build_profile.py
```

An optional `GH_TOKEN` environment variable enables GraphQL and raises the API rate limit. Do not commit tokens. The default username is `LucasBetioli123`; override `PROFILE_USER` for a different account.

## Edit the content

- Biography, qualifications, project descriptions, contacts: `README.md`.
- Header, atlas, colors, and chart layout: `scripts/build_profile.py`.
- Chart update schedule: `.github/workflows/profile.yml`.

The profile lists the completed B.Sc. and M.Sc. It does not claim a current PhD enrollment, assign skill percentages, or publish internal Alliage implementation details.

GitHub’s profile README documentation: <https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme>.
