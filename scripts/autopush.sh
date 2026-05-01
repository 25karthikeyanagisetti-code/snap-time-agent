#!/usr/bin/env bash
# Pushes any new commits made by the daily Cowork research task to GitHub.
# Installed as a launchd job that runs every morning after the Claude run completes.
#
# Also guarantees a daily green-square contribution: if there are zero new commits
# today, creates an empty "streak heartbeat" commit before pushing.
#
# Logs to ~/Library/Logs/snap-time-agent-autopush.log

set -u
LOG="$HOME/Library/Logs/snap-time-agent-autopush.log"
REPO="$HOME/Documents/Claude/Projects/AI system/snap-time-agent"

# IMPORTANT: this email must match an email registered to your GitHub account,
# otherwise GitHub will not attribute the commits to you and your contribution
# graph will stay grey. Verify at https://github.com/settings/emails
GIT_AUTHOR_EMAIL="25karthikeyanagisetti@gmail.com"
GIT_AUTHOR_NAME="Karthikeya Nagisetti"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') autopush start =====" >> "$LOG"

if [ ! -d "$REPO/.git" ]; then
  echo "ERROR: repo not found at $REPO" >> "$LOG"
  exit 1
fi

cd "$REPO" || exit 1

# Make sure the repo author identity is set correctly so commits get
# attributed to the GitHub account.
git config user.email "$GIT_AUTHOR_EMAIL"
git config user.name  "$GIT_AUTHOR_NAME"

# Clear any half-applied locks left by the Cowork sandbox.
rm -f .git/index.lock .git/HEAD.lock
git checkout main >> "$LOG" 2>&1

# If there are uncommitted changes (rare — Claude should have committed them),
# capture them in a safety commit.
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "WARNING: uncommitted changes detected, autocommitting" >> "$LOG"
  git add -A
  git commit -m "autopush: safety commit of uncommitted changes" >> "$LOG" 2>&1
fi

# === STREAK GUARANTOR ===
# Count commits authored by us today (since midnight local time).
TODAY_START=$(date '+%Y-%m-%d 00:00:00')
COMMITS_TODAY=$(git log --since="$TODAY_START" --author="$GIT_AUTHOR_EMAIL" --oneline | wc -l | tr -d ' ')
echo "commits today by $GIT_AUTHOR_EMAIL: $COMMITS_TODAY" >> "$LOG"

if [ "$COMMITS_TODAY" -eq 0 ]; then
  echo "no commits today, creating streak heartbeat commit" >> "$LOG"
  # Write a heartbeat line to a tracking file so the commit has a real diff.
  # (Empty commits also count toward GitHub contributions, but a real diff is
  # less weird-looking in the commit history.)
  HEARTBEAT_FILE="$REPO/.streak/heartbeat.log"
  mkdir -p "$REPO/.streak"
  echo "$(date '+%Y-%m-%d %H:%M:%S %z') — no research commit today, autopush heartbeat" >> "$HEARTBEAT_FILE"
  git add "$HEARTBEAT_FILE"
  git commit -m "streak: heartbeat $(date '+%Y-%m-%d')" >> "$LOG" 2>&1
fi

# Push to GitHub. The credential helper stores the PAT from the manual push
# you did earlier, so this will not prompt.
git push origin main >> "$LOG" 2>&1
RC=$?

if [ $RC -eq 0 ]; then
  echo "OK: push succeeded" >> "$LOG"
else
  echo "ERROR: push failed with rc=$RC" >> "$LOG"
fi

echo "===== $(date '+%Y-%m-%d %H:%M:%S') autopush end =====" >> "$LOG"
exit $RC
