#!/bin/bash
# Publikuje wersje podgladowa strony (noindex) na GitHub Pages: galaz gh-pages, folder otwieranieautkielce/
set -e
cd "$(dirname "$0")"
REPO=$(git rev-parse --show-toplevel)
TMP=$(mktemp -d)
python3 build.py --podglad "$TMP/site" | tail -3
git -C "$REPO" fetch -q origin gh-pages:refs/remotes/origin/gh-pages
WT="$TMP/gh-pages"
git -C "$REPO" worktree add -q --detach "$WT" origin/gh-pages
rm -rf "$WT/otwieranieautkielce"
cp -r "$TMP/site" "$WT/otwieranieautkielce"
rm -f "$WT/otwieranieautkielce/.htaccess"
cd "$WT"
git add -A otwieranieautkielce
if git diff --cached --quiet; then echo "Brak zmian do publikacji."; else
  git commit -q -m "Podgląd strony otwieranieautkielce.pl (wersja do akceptacji)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01S9byUn1KSFiK8hRwm8oAU9"
  for i in 1 2 3 4; do git push -q origin HEAD:gh-pages && break || sleep $((2**i)); done
  echo "Opublikowano: $(git rev-parse --short HEAD)"
fi
cd "$REPO"; git worktree remove --force "$WT"; rm -rf "$TMP"
