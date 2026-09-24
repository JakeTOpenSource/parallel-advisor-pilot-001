# Parallel Advisor System: pilot-001

An eval-of-evals harness. It does not grade models. It grades the eval:
were the answers locked before the run, did two independent parties
reproduce them, what happened when they disagreed, and can a stranger
re-run the whole thing.

## What this is

pilot-001 is the first clause run through the system: a small deterministic
test suite (seeded RNG, deterministic sorting, float comparison within a
declared tolerance, a negative-control rejection canary, a seed-file
integrity tripwire). Two independent tracks ran the identical frozen
procedure: Track M (Muse, Linux) and Track C (Claude Code, Windows). Both
matched the pre-registered expectations. When the tracks disagreed by 5.55e-16 on
one float, the system flagged it, traced it to platform libm differences,
classified it, and fixed the checker with the judge's approval instead of
averaging it away. An independent auditor then re-ran every check, attacked
the checker itself, found real holes (including one in the advisor's own
log), and all of it was fixed on the record.

## What the pilot demonstrates

1. The answers were locked before anyone ran the test: pre-registered, and
   recomputable by anyone from the public procedure.
2. Two independent parties ran the identical frozen procedure on different
   machines and operating systems, and both matched the locked answers
   within the tolerances declared up front.
3. When the two runs disagreed, even by a hair, the system stopped and
   investigated instead of averaging it away.
4. An independent auditor re-ran every check, attacked the checker, and
   found real flaws that were fixed on the record.
5. Every step of that is re-runnable by a stranger. The receipts are public.

## What it does not prove

It does not prove the executors are smart, honest in general, or aligned.
This pilot was deterministic; they just ran code. It proves the machinery,
not the models. It does not prove the system works on judgment-based tasks
where an executor could actually drift. That is the next frontier, stated
openly.

## Verify it yourself

See VERIFY.md. Seven steps, Python 3 standard library only. PROBES.md
specifies nine tamper probes against the checker. diff-tool/versions keeps
every checker version with hashes, so the historical findings stay
reproducible. No trust in the author required.

## Roles

- Advisor (Ed): writes clauses, pre-registers expectations, compares outputs,
  investigates contradictions, maintains baselines.
- Track M: executes public clauses through Muse-side subagents.
- Track C: executes the identical public clause through Claude Code.
- Judge (Jacob Tiller): approves clauses and amendments, resolves
  contradictions, and gives final sign-off. Sign-off requires two passing tracks.

## License

MIT. See [LICENSE](LICENSE).
