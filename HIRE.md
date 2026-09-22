# Working together

I build the infrastructure AI agents run on, and I ship it with tests that
someone else can check. This page says what I can be hired for, what it costs,
and what the evidence is.

Available for **remote contract work**, based in Türkiye, working in the
European timezone band. English for work, Turkish natively.

---

## What I can be hired for

### 1. MCP / agent security review — from $900, fixed price

You are about to install a third-party MCP server, or you shipped one and want
to know what a reviewer would say about it. I read what the server does before
you run it: install scripts, what executes at install time, what leaves the
machine, what the tool descriptions tell a model to do.

That last one is the part most reviews miss. An MCP tool description is read by
the model on every call, and nobody scrolls past it — so text that tells the
model to hide its activity, to fetch a `.env` file, or to call some other tool
first is an attack that a normal code review walks straight past.

**You get:** a report per server — what it does, what it would do to your
machine, what is worth acting on and what is noise, each finding quoted with
file and line. Plus the scan tooling, so you can re-run it yourself.

**Why me:** I wrote [mcp-vet](https://github.com/Furkiozknn/mcp-vet) — 289
tests — and ran it against 17 widely-used MCP servers. Roughly half of all
findings landed outside the code a server actually ships: test fixtures, issue
templates, developer scripts. That is the number that matters, because it is
why nobody reads scanner output. I spent the work separating the two rather
than publishing the bigger number.

### 2. Make it shippable — from $1,500, fixed price

You have code that works on your machine. It has no tests, or tests that pass
without proving anything, and releasing it is a manual ritual nobody enjoys.

**You get:** a test suite that fails when the code is wrong, CI that runs it on
every push, and a release path that cannot ship a broken artifact. Every number
I report traces back to the run that printed it.

**Why me:** doing this to my own repositories found three defects that would
have shipped — a package that could not build because of a stray carriage
return in its manifest, a published summary that had drifted from the code, and
three servers that installed cleanly but had no entry point to run. All three
were invisible to every passing test in those repositories, because nothing
tested the packaging. They are now gated in CI.

### 3. Ongoing contract — $50/hour

Agent and MCP systems, Python and TypeScript, job orchestration, pipelines,
provenance and cost accounting. Windows and Turkish-locale environments, where
things break that nobody documents: cp1254 killing a tool before it prints its
first line, PowerShell 5.1 without `&&`, a heredoc quietly eating a backslash.

---

## The evidence

- **[4,593 tests across 22 repositories](TESTLER.md)** — every count traced to
  the suite run that printed it, not grepped from the source. An earlier version
  of this profile said 1,426 and was wrong; that file exists so the claim is
  checkable rather than believable.
- **Everything is public.** [Play the game](https://furkiozknn.github.io/nova-drift/),
  [read a story](https://furkiozknn.github.io/masal/), read the tests.
- **The demos are real runs**, captured by scripts committed in their
  repositories — not mockups.

## Getting in touch

- Open an issue on any of [my repositories](https://github.com/Furkiozknn?tab=repositories)
- [@furkiozkan on X](https://x.com/furkiozkan)

Happy to do a short paid trial task before any larger engagement. If what you
need is not on this page, ask anyway — the worst case is I tell you who is
better suited.
