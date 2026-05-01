# Daily autonomous research — install guide

You now have a two-part system that runs new experiments every day and pushes
the results to GitHub without you having to open Claude.

## Architecture

```
07:00 AM  →  Cowork scheduled task wakes up
              Picks the top hypothesis from docs/research_backlog.md
              Implements + runs a new experiment (~5 min)
              Writes finding.md, chart, CSV
              Updates daily_research_log.md
              git commit (locally — sandbox cannot push)

07:30 AM  →  launchd autopush job wakes up
              Runs scripts/autopush.sh
              git push origin main
              Logs to ~/Library/Logs/snap-time-agent-autopush.log
```

You wake up, pull up GitHub, and there's a fresh experiment + finding committed.

## Part 1 — Cowork scheduled task

Already created. It runs every day at 7:00 AM local time. You can manage it
from the **Scheduled** section in the Cowork sidebar.

To change the time, the hypothesis pool, or anything else, edit:
`~/Documents/Claude/Scheduled/snap-time-agent-daily-research/SKILL.md`

Or just ask me to update it.

To trigger it manually right now (for testing), open the Scheduled sidebar and
click "Run now" on the task.

## Part 2 — launchd auto-push (one-time install)

Open Terminal and paste this whole block:

```bash
# 1. Make the push script executable.
chmod +x ~/Documents/Claude/Projects/"AI system"/snap-time-agent/scripts/autopush.sh

# 2. Make sure git remembers your GitHub PAT so the push doesn't prompt.
#    (You probably already did this when you pushed manually the first time.)
git config --global credential.helper osxkeychain

# 3. Copy the launchd plist into LaunchAgents.
cp ~/Documents/Claude/Projects/"AI system"/snap-time-agent/scripts/com.user.snap-time-agent.autopush.plist \
   ~/Library/LaunchAgents/

# 4. Load the job.
launchctl unload ~/Library/LaunchAgents/com.user.snap-time-agent.autopush.plist 2>/dev/null
launchctl load   ~/Library/LaunchAgents/com.user.snap-time-agent.autopush.plist

# 5. Verify it's registered.
launchctl list | grep snap-time-agent
```

You should see one line ending in `com.user.snap-time-agent.autopush`. That's it —
the auto-push will now run every morning at 7:30 AM.

## Part 3 — Test the push side once, end-to-end

Run the push script by hand to make sure it works:

```bash
~/Documents/Claude/Projects/"AI system"/snap-time-agent/scripts/autopush.sh
echo "exit code: $?"
cat ~/Library/Logs/snap-time-agent-autopush.log
```

If exit code is 0 and the log says `OK: push succeeded`, you're done.

If it says `ERROR: push failed`, the most likely cause is your stored GitHub
credential expired. Re-run a manual `git push` from the repo, enter your
Personal Access Token when prompted, and try `autopush.sh` again.

## How to change the schedule

**Cowork side** (changes when the research runs):
Ask me to update the cron expression on the scheduled task. Right now it's
`0 7 * * *` (7:00 AM daily).

**launchd side** (changes when the push happens):
Edit `~/Library/LaunchAgents/com.user.snap-time-agent.autopush.plist`, change
the `Hour` and `Minute` keys, then:

```bash
launchctl unload ~/Library/LaunchAgents/com.user.snap-time-agent.autopush.plist
launchctl load   ~/Library/LaunchAgents/com.user.snap-time-agent.autopush.plist
```

Make sure the autopush time is at least 15 minutes AFTER the Cowork task time so
the research has time to finish.

## How to disable

To pause the daily research:
- Cowork sidebar → Scheduled → snap-time-agent-daily-research → toggle off

To stop auto-pushing (Cowork can still run, you just push manually):
```bash
launchctl unload ~/Library/LaunchAgents/com.user.snap-time-agent.autopush.plist
rm ~/Library/LaunchAgents/com.user.snap-time-agent.autopush.plist
```

## What gets committed each day

- `src/exp_<name>.py` — the new experiment
- `experiments/<name>_v1/results.csv` — raw sweep data
- `experiments/<name>_v1/<chart>.png` — visualization
- `experiments/<name>_v1/finding.md` — written analysis with headline number
- `docs/daily_research_log.md` — running log of every daily run
- `docs/research_backlog.md` — backlog updated (popped item moved to "Done")

Commit message format: `daily: <name> — <one-line result>`

## Where to look for problems

- **Cowork scheduled task didn't run:** Cowork sidebar → Scheduled → check
  the run history.
- **Push failed:** `cat ~/Library/Logs/snap-time-agent-autopush.log`
- **Want to see what today's experiment found:** `cat ~/Documents/Claude/Projects/"AI system"/snap-time-agent/docs/daily_research_log.md`
- **Want to add a new hypothesis to the queue:** edit `docs/research_backlog.md`
  and add a bullet under `## Queued`. The next day's task will pick it up.
