# Probability and Statistics for Quant Interviews

> - **Source:** lecture transcript `GMT20260816-005926_Recording.cc.vtt` (2026-08-16),
>   and `QT_worksheet_1-3.pdf` §§ 2–3.
> - **What it is:** the probability and statistics apparatus a quant interview assumes —
>   stated precisely, with the points flagged as commonly got wrong, and the problem set
>   that goes with it.
> - **Provenance:** content is from the lecture or the worksheet unless a passage says
>   otherwise. A block opening with *Added* was worked out afterwards.
> - **See also:** [Market 101 — Structure, Volatility, and Short Selling](market-101-foundations.md).

---

## 1. Probability

### 1.1 The probability space

A **probability space** is the triple $(\Omega, F, P)$. Four objects, one role each:

| Symbol | What it is | Die example |
| --- | --- | --- |
| $\Omega$ | Every possible **outcome** | $\{1, 2, 3, 4, 5, 6\}$ |
| $E$ | One **event** — a subset of $\Omega$ | "even" $= \{2, 4, 6\}$ |
| $F$ | The **list of every event you may talk about** | The collection of all 64 subsets |
| $P$ | The function that puts a number on an event | $P(\{2, 4, 6\}) = 1/2$ |

The whole relationship is two lines of notation:

$$E \in F, \qquad P : F \to [0, 1]$$

An event must be **on the list** before it can be given a probability, and $P$ takes its
input **from** that list.

**The menu.** $F$ is the menu, $E$ is a dish on it, $P$ is the price list. You can only
order what the menu carries, and the price list only prices what the menu carries. Asking
the price of something not on the menu is not expensive — it is **meaningless**, and a set
outside $F$ is the same: $P$ of it is undefined, not small.

So the triple reads left to right: **$\Omega$ says what can happen, $F$ says which events
may be asked about, $P$ says how likely each of those is.** All three are needed before
the game is specified — which faces exist, which bets are allowed, what each bet pays.

**Why $F$ is not simply every subset.** When $\Omega$ is countable it can be, and you never
think about it again. When it is uncountable it cannot: no countably-additive,
translation-invariant probability exists on *all* subsets of $[0,1]$, so the
non-measurable sets have to be left off the menu.

**The axioms are the three questions probability has to keep askable.**

| Axiom on $F$ | Keeps this askable |
| --- | --- |
| $\Omega \in F$ | Did **anything** happen? |
| Closed under complement | Did $E$ **not** happen? |
| Closed under countable union | Did **at least one** of $E_1, E_2, \ldots$ happen? |

Countable rather than merely finite, because events like "the sequence converges" are
built from countably many operations. $P$ carries the matching three — it lands in
$[0,1]$, gives $\Omega$ probability 1, and is additive on disjoint events, so
$P(A) = \sum_{\omega \in A} P(\omega)$ and two events are **mutually exclusive** when
$A \cap B = \emptyset$.

*Added.* **$F$ is information, and that is the part that matters.** Same $\Omega$,
different $F$:

| What you observe of a die roll | $F$ | Can you ask "was it a 3?" |
| --- | --- | --- |
| The face | All 64 subsets | Yes |
| Only the parity | $\emptyset$, $\{1,3,5\}$, $\{2,4,6\}$, $\Omega$ — four events | **No** — that set is not in $F$ |

A smaller $F$ means you know less. A **filtration** $F_t$ is a family of sigma-algebras
growing with time — the information available at $t$ — and saying $X$ is
$F_t$-**measurable** says exactly that $X$ is knowable at $t$. That is the formal
statement of no look-ahead: a signal computed at $t$ must be measurable with respect to
what was known at $t$. The lecture waved the sigma-algebra away as bookkeeping, which is
fair for an interview and not fair for anyone working on time series.

### 1.2 Counting

| Tool | Count | For |
| --- | --- | --- |
| **Basic principle** | $n_1 n_2 \ldots n_k$ | Length-$k$ sequences with $n_i$ choices at step $i$ |
| **Combination** | $\frac{n!}{(n-k)! k!}$ | Choosing $k$ of $n$, order **irrelevant** — committees |
| **Permutation** | $\frac{n!}{(n-k)!}$ | Arranging $k$ of $n$, order **matters** |
| **With repeats** | $\frac{n!}{n_1! n_2! \ldots n_k!}$ | Permuting $n$ objects of which $n_1$ are alike, etc. |

A permutation is a combination followed by an ordering: $nPk = nCk \cdot k!$, because
there are $k!$ ways to permute the chosen $k$.

**Inclusion-exclusion** alternates: add the singles, subtract the pairs, add the triples,
and so on, with $\left( \frac{N!}{r! (N-r)!} \right)$ terms at order $r$. It is worth
knowing and rarely worth using — most interview problems have a shorter route through
complementary counting or symmetry.

**Counting only works when the outcomes are equally likely.** If $\Omega$ is finite and
every outcome has probability $1 / |\Omega|$, then

$$P(E) = \frac{|E|}{|\Omega|}$$

and you may replace probability with a count. **This is the single most reliable trap in
the set.** Textbook problems are always constructed to satisfy it; interview problems
often *look* as though they do and do not — see § 5.1, where the paths of a random walk
turn out to carry unequal probabilities.

### 1.3 Conditional probability

$$P(A \mid B) = \frac{P(A \cap B)}{P(B)}$$

Read backwards it is the more useful form: $P(A \cap B) = P(A \mid B) P(B)$ computes an
intersection from a conditional.

**Law of total probability.** For mutually exclusive $F_1, \ldots, F_n$ whose union is
$\Omega$:

$$P(E) = \sum_{i=1}^{n} P(E \mid F_i) P(F_i)$$

**Bayes.** Rearranging the same two facts:

$$P(F_j \mid E) = \frac{P(E \mid F_j) P(F_j)}{\sum_{i=1}^{n} P(E \mid F_i) P(F_i)}$$

**Why this is tested so heavily.** Trading is conditional in its entirety — you always
know *something*, and the question is what that does to the distribution of everything
else. As information arrives, the distribution changes. An interview that tests
conditional probability is testing the shape of the job.

### 1.4 Independence of events

$$P(E \cap F) = P(E) P(F) \quad \Longleftrightarrow \quad P(E \mid F) = P(E)$$

Independence is symmetric. Do not confuse it with mutual exclusivity — mutually exclusive
events with positive probability are **maximally dependent**, since one occurring rules
the other out.

---

## 2. Random variables

### 2.1 What a random variable is

A **random variable** is nothing more than a function $X : \Omega \to R$. Its
**distribution** is the collection of $P(X \in S)$ over subsets $S$ of the real line.

| Type | When | Example |
| --- | --- | --- |
| **Discrete** | A finite or countably infinite set $S$ carries all the probability | A die roll; the count in the St Petersburg paradox |
| **Continuous** | A nonnegative density $f$ exists with $P(a \leq X \leq b)$ equal to its integral | Uniform, normal |
| **Neither** | — | Flip a coin: heads, draw from Uniform(0,1); tails, return $-1$ |

**A random variable need not be one or the other.** People forget the third row.

**Note (a precision that is usually skipped).** Loosely, a continuous random variable has
$P(X = x) = 0$ for every $x$ — because there are uncountably many outcomes in any
interval. That is **necessary but not sufficient**; the correct term is *absolutely
continuous*. Graduate texts insist on it because the analysis breaks without it. For
interview purposes the loose version is fine.

### 2.2 CDF, PDF, PMF

| | Definition | Exists when |
| --- | --- | --- |
| **CDF** $F_X(x)$ | $P(X \leq x)$ | **Always**, for any random variable |
| **PDF** $p_X(x)$ | The derivative of the CDF | Only where the CDF is differentiable — for us, iff $X$ is continuous |
| **PMF** $p_X(x)$ | $P(X = x)$ | Discrete $X$. Applied to a continuous variable it returns 0 everywhere |

Every property of the CDF follows from the definition rather than being an extra
assumption: non-decreasing, right-continuous, limit 0 at $-\infty$ and 1 at $+\infty$.

---

## 3. Expectation and variance

**Expectation** is the probability-weighted average — a sum over a discrete variable, an
integral against the density for a continuous one. The same substitution gives $E[g(X)]$:
put $g(x)$ where $x$ stood.

**Expectation is linear**, and this is the most underrated fact in the subject:

$$E[aX + bY] = a E[X] + b E[Y]$$

It needs **no assumption whatsoever** — not independence, not any knowledge of the joint
structure, not even that the variables are related. Most expectation problems that look
hard are linearity applied to a well-chosen decomposition.

**Variance** and standard deviation:

$$\text{Var}[X] = E \left[ (X - E[X])^2 \right] = E[X^2] - \left( E[X] \right)^2$$

The second form is the one you compute with; the first is the one that says what it means.

**Iterated expectation.**

$$E[X] = E \left[ E[X \mid Y] \right]$$

where the outer expectation is over $Y$. Often the conditional is far easier than the
thing itself, and this is the whole trick. **The difficulty is that $Y$ is usually not in
the problem** — you have to invent the right conditioning variable, and nothing tells you
what it should be. Taking $X$ as an indicator gives the same statement for probabilities:
$P(A) = E[P(A \mid Y)]$.

---

## 4. Several random variables

**Joint, marginal, conditional.**

| | What it answers |
| --- | --- |
| **Joint** $p_{X,Y}(x,y)$ | The probability of the pair — where the co-structure lives |
| **Marginal** $p_X(x)$ | The distribution of $X$ alone, summing or integrating $Y$ away |
| **Conditional** $p_{X \mid Y}(x \mid y)$ | The distribution of $X$ once $Y$ is known — the joint divided by the marginal |

The conditional is the one that matters for trading: information arrives, and the question
is how the view of $X$ changes.

**Covariance and correlation.**

$$\text{Cov}[X,Y] = E[XY] - E[X] E[Y], \qquad \rho_{X,Y} = \frac{\text{Cov}[X,Y]}{\sigma_X \sigma_Y}$$

**Independence of random variables.** Four equivalent characterizations:

1. $F_{X,Y}(x,y) = F_X(x) F_Y(y)$
2. $p_{X,Y}(x,y) = p_X(x) p_Y(y)$
3. $E[g(X) h(Y)] = E[g(X)] E[h(Y)]$ **for all bounded continuous** $g, h$
4. $p_{X \mid Y}(x \mid y) = p_X(x)$

**The trap lives in (3).** Independence gives $E[XY] = E[X] E[Y]$, hence zero covariance
and zero correlation — but **the converse is false.** $E[XY] = E[X] E[Y]$ is a statement
about *one* pair of functions, the identity. Independence demands it for *every* bounded
continuous pair. Zero correlation is necessary, not sufficient.

**Order statistics.** $X_{(k)}$ is the $k$-th smallest of a sample. It is itself a random
variable. For i.i.d. draws the maximum has CDF

$$F_{X_{(n)}}(x) = \left( F_X(x) \right)^n$$

because all $n$ must fall below $x$. Do not memorise the general formula — it appears
rarely and is quicker to re-derive on the spot than to recall.

---

## 5. Worked problems

The three the lecture actually worked through.

### 5.1 Grid paths, and the counting trap

A 4 by 4 grid. Walk from corner A to corner B, one step per second, **right or up only**.

**Part A — how many paths?** Every path is exactly 8 steps: 4 right and 4 up. Choosing
which 4 of the 8 are "up" fixes the path.

$$\text{paths} = \left( \frac{8!}{4! 4!} \right) = 70$$

**Part B — two walkers.** A second walker starts at B and moves **left or down only**.
Each walker picks between its available moves with probability one half, and has no choice
when only one move is legal. What is the probability they meet?

- They move in lockstep, so they can only meet after **4 steps each** — on the
  anti-diagonal. Any other square is the wrong number of moves away.
- When they meet, their two half-paths **join into one complete A-to-B path**. So the
  number of meeting configurations is exactly Part A's answer, 70.
- Within its first 4 moves neither walker can be forced: forcing only begins once a
  walker reaches an edge, which takes 4 moves, so the constraint bites on move 5 and
  never arrives. Every one of the 8 moves is a genuine coin flip.

$$P(\text{meet}) = \frac{70}{2^8} = \frac{70}{256} = \frac{35}{128}$$

**The trap.** Having computed 70 in Part A, it is tempting to treat those 70 complete
paths as equally likely under the random walk. **They are not.** A path that reaches an
edge early spends its remaining moves on forced steps, which cost no probability — so a
boundary-hugging path is *more* likely than an interior one. The counting argument
survives here only because the meeting happens at step 4, before any forcing can occur.

This is § 1.2's warning made concrete: you may only count outcomes when the outcomes are
equally likely.

### 5.2 Rolling until a six

**Roll a die until a 6 appears. What is the probability the sum of all rolls, including
the 6, is even?** (Worksheet § 2, Problem 9.)

Let $p$ be that probability, and condition on the first roll:

| First roll | Probability | Effect |
| --- | --- | --- |
| 6 | 1/6 | Stop. Sum is 6 — even. Success |
| 2 or 4 | 2/6 | Even; parity unchanged; continue needing even → contributes $p$ |
| 1, 3, or 5 | 3/6 | Odd; parity flips; continue needing **odd** → contributes $1 - p$ |

$$p = \frac{1}{6} + \frac{2}{6} p + \frac{3}{6} \left( 1 - p \right) \quad \Longrightarrow \quad \frac{7}{6} p = \frac{2}{3} \quad \Longrightarrow \quad p = \frac{4}{7}$$

### 5.3 Minimum spacing of 101 uniform points

**Sample 101 points independently from Uniform(0, 1). (a) What is the probability the
minimum distance between any two points does not exceed 1/1000? (b) What is the expected
shortest distance?** (Worksheet § 3, Problem 10.)

*Added. Posed in class and left unanswered; the derivation below is worked out here.*

Let $M$ be the smallest gap between adjacent order statistics. For $n$ uniform points the
standard spacings result gives, for $0 \leq d \leq 1 / (n-1)$:

$$P(M > d) = \left( 1 - (n-1) d \right)^n$$

**(a)** With $n = 101$ and $d = 1/1000$:

$$P(M > 0.001) = \left( 1 - 0.1 \right)^{101} = 0.9^{101} \approx 0.0000239$$

$$P(M \leq 0.001) \approx 0.99998$$

Nearly certain — with 101 points the average gap is only about 1/100, so gaps an order of
magnitude tighter are commonplace.

**(b)** Integrating the survival function over $0 \leq d \leq 1/100$:

$$E[M] = \frac{1}{(100)(102)} = \frac{1}{10200} \approx 0.000098$$

---

## 6. The problem set

*Added: the technique tags. The worksheet gives the problems only.* Solutions are
deliberately **not** written out — the worksheet withholds them by design, and the work is
the point. Each row names the tool the problem wants and where the difficulty sits.

### 6.1 Probability (worksheet § 2)

| # | Problem | Wants | Where it bites |
| --- | --- | --- | --- |
| 1 | Poker: 8♥9♥ on a 2♥ 7♦ 10♥ flop — P(flush or straight by the river) | Counting outs over two cards, inclusion-exclusion | The flush and straight events **overlap** (straight flush); subtract once |
| 2 | 10 people, choose 3 — P(Alice is on the committee) | Symmetry | Do not count committees; every person is equally likely |
| 3 | Deal 4 cards — P(at least one pair), P(exactly one pair) | Complementary counting | "At least" is easy by complement; "exactly one" must exclude two pair and trips |
| 4 | Claw machine, 4 slots from 1–5 — wild in slot 1 or slot 3? | Symmetry | The position is irrelevant. The trap is believing it is not |
| 5 | 1000 coins, one two-headed, 10 heads in a row | **Bayes** | The prior is tiny and the likelihood ratio is $2^{10}$ — they fight |
| 6 | Flip until the first Ace — next card A♠ or 2♠? | Symmetry | A♠ must not already have *been* the first Ace; 2♠ has no such constraint |
| 7 | Coin with $P(H) = 0.3$ — simulate a fair coin, then a 1/3 coin | Von Neumann trick | Pair the flips: HT and TH are equally likely. The 1/3 case needs a different construction |
| 8 | Russian roulette, **two adjacent** bullets, spin once | Conditioning on chamber position | Adjacency changes the conditional after a survived first pull. Generalise to $k$ of $n$ |
| 9 | Roll until a 6 — P(sum even) | First-step recursion | **Worked in § 5.2** |
| 10 | 50 good and 50 bad jelly beans, two identical boxes | Optimisation over an asymmetric split | The even split is not optimal; make one box near-certain |
| 11 | 100 passengers, first one drunk — P(you get seat 100) | Symmetry, or recursion | The state collapses to a two-way symmetry between seat 1 and seat 100 |
| 12 | 10 red, 20 blue, 30 green — P(≥1 blue and ≥1 green left when the reds run out) | Complementary counting on relative order | Only the **order of the last of each colour** matters; the counts of draws do not |

### 6.2 Statistics (worksheet § 3)

| # | Problem | Wants | Where it bites |
| --- | --- | --- | --- |
| 1 | U[0,100] difference game — value a redraw gadget vs a swap gadget | Order statistics, expectation | Answer the "which is worth more" part by argument before computing either |
| 2 | Die with one optional re-roll — EV of the final roll; EV of the max | Optimal stopping | The two questions have **different optimal policies** |
| 3 | 10 balls into 10 bins — E[bins with exactly 2] | **Linearity** + binomial | Indicator per bin. The bins are dependent and linearity does not care |
| 4 | 5 marbles, 10-step staircase, step probability $p$ — E[stopping on level 3] | Linearity + geometric | Per-marble probability first, then multiply by 5 |
| 5 | Coin $P(H) = 0.7$, first flip T — E[flips until #H = #T] | Random-walk hitting time | The walk is **biased**, so the answer is finite; the fair-coin version is not |
| 6 | E[rolls to get two sixes in a row] | First-step analysis / Markov chain | Two states — "no six yet" and "one six" — set up and solve |
| 7 | Urn with $m$ red and $n$ blue, draw till one colour is gone — E[remaining] | Symmetry + linearity | Indicator on each ball being after the last of the other colour |
| 8 | Village coin flips — expected **frequency** of tails per household | Ratio versus expectation | E[ratio] is **not** ratio of expectations. That gap is the whole problem |
| 9 | $X_1, X_2, X_3$ i.i.d. U[0,1] — P(max > sum of the other two) | Geometric probability | Volume of a region in the unit cube |
| 10 | 101 points from U[0,1] — min spacing | Spacings / order statistics | **Worked in § 5.3** |
| 11 | Stick cut twice — P(the three pieces form a triangle) | Geometric probability | Triangle inequality gives three constraints on the unit square |
| 12 | Die paying face value, re-roll on 4/5/6 | Self-referential expectation | One equation in $E$; it solves in a line |

---

## Key terms (EN ↔ ZH)

| English | 中文 | Meaning here |
| --- | --- | --- |
| sample space | 样本空间 | The set of all outcomes $\Omega$ |
| event | 事件 | A subset of the sample space |
| mutually exclusive | 互斥 | Empty intersection — **not** the same as independent |
| combination / permutation | 组合 / 排列 | Order irrelevant vs order matters |
| inclusion-exclusion | 容斥原理 | Alternating sum over intersections |
| conditional probability | 条件概率 | The distribution once something is known |
| law of total probability | 全概率公式 | Split by a partition and recombine |
| Bayes' formula | 贝叶斯公式 | Invert a conditional using the prior |
| independence | 独立 | Joint factorises for **all** bounded continuous test functions |
| CDF / PDF / PMF | 分布函数 / 密度函数 / 概率质量函数 | Always exists / continuous only / discrete only |
| expectation | 期望 | Probability-weighted average; **linear with no assumptions** |
| iterated expectation | 全期望公式 | $E[X] = E[E[X \mid Y]]$ — the hard part is choosing $Y$ |
| covariance / correlation | 协方差 / 相关系数 | Zero correlation does **not** imply independence |
| order statistic | 次序统计量 | The $k$-th smallest of a sample; itself a random variable |
