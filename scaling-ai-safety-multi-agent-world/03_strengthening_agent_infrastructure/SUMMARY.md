# 03. Strengthening Agent Infrastructure

## Why this category matters

Behavioral alignment alone cannot determine who an agent represents, whether a claimed property is true, where an action came from, or how to resolve harm after deployment. Agent infrastructure supplies shared rules and technical rails outside the model: identity, authentication, attestations, provenance, reputation, contracts, delegation, monitoring, and remedies.

## Paper matrix

| Subcategory | Work | Infrastructure primitive | Evidence type | Main contribution |
|---|---|---|---|---|
| Identity, authentication, and admission control | Chan et al. (2024) | Persistent IDs for AI-system instances plus accessible associated claims | Conceptual and implementation sketch | Makes actions and safety claims attributable to a particular deployed instance and responsible actor. |
| Identity, authentication, and admission control | ARIA (2026) | Scalable trust and contract infrastructure | Programme thesis | Frames trustworthy machine interaction as a capability that should scale with autonomous transactions. |
| Verifiable attributes, actions, and provenance | Kirchenbauer et al. (2023) | Statistical watermark embedded through token sampling | Formal and empirical | Open detector returns interpretable p-values without model API or parameter access. |
| Verifiable attributes, actions, and provenance | Sun et al. (2024) | Zero-knowledge proof of LLM inference, including attention and nonlinear operations | Cryptographic system and benchmark | Generates a full inference proof for a 13B-parameter LLM in under 15 minutes while hiding model parameters. |
| Reputation, accountability, and dispute resolution | Chan et al. (2025) | External protocols for attribution, interaction shaping, detection, and remedy | Research agenda | Defines agent infrastructure as systems outside agents that mediate their interactions and impacts. |
| Reputation, accountability, and dispute resolution | Kolt (2025) | Legal and technical institutions for visibility, inclusivity, and liability | Legal/economic analysis | Applies principal-agent theory and agency law to high-speed, opaque autonomous agents. |
| Reputation, accountability, and dispute resolution | Hadfield and Koh (2025) | Market and organizational institutions for an agent economy | Economics survey | Identifies open questions around contracts, organizations, market behavior, and institutional design. |
| Reputation, accountability, and dispute resolution | Tomasev et al. (2025) | Sandbox economies, auctions, mission economies, auditability, and market controls | Conceptual design | Classifies agent economies by origin and permeability and argues for proactive, steerable markets. |
| Commitments and delegation | Tennenholtz (2004) | Inspectible executable strategies in program games | Formal game theory | Program equilibrium can sustain mutual cooperation in one-shot Prisoner's Dilemma and realizes feasible individually rational payoff sets. |
| Commitments and delegation | Google A2A (2025) | Agent-to-agent discovery, task delegation, messaging, and interoperability | Protocol announcement, not a paper | Illustrates the operational layer on which identity, authorization, provenance, and commitments must be enforced. |

## Identity, authentication, and admission control

**Chan et al. (2024) - IDs for AI Systems.** The proposal assigns identifiers to concrete system instances, such as a particular model session, and links each ID to information relevant to users, investigators, and counterparties. An ID can support certification lookup, incident attribution, contact with the responsible deployer, and shutdown or remediation. The paper emphasizes high-impact interactions such as financial transactions and contact with real people, while noting privacy, surveillance, gaming, and adoption risks. [Source](https://arxiv.org/abs/2406.12137)

**ARIA (2026) - Scaling Trust Programme Thesis.** ARIA treats trust as infrastructure for large numbers of machine-speed interactions rather than a property inferred informally from a brand or model name. Its contract-oriented framing is relevant to machine-checkable permissions, obligations, evidence, and remedies. It is a programme thesis and solicitation context, not a peer-reviewed evaluation; its value here is in specifying infrastructure-level research targets. [Source](https://aria.org.uk/opportunity-spaces/trust-everything-everywhere/scaling-trust/)

## Verifiable attributes, actions, and provenance

**Kirchenbauer et al. (2023) - A Watermark for Large Language Models.** At each generation step, a pseudorandom subset of tokens is designated green and softly favored. A detector tests whether the observed green-token count is too large to be chance, producing a z-score and interpretable p-value without querying the original model. This is a precise example of a probability-based concern signal, but it verifies likely text origin, not whether the text or action is unsafe. [Source](https://proceedings.mlr.press/v202/kirchenbauer23a.html)

**Sun, Li, and Zhang (2024) - zkLLM.** zkLLM proves that an output was produced by a specified LLM computation while keeping model parameters private. Its `tlookup` and `zkAttn` components address nonlinear tensor operations and attention, and the CUDA system reports end-to-end proof generation for 13B-parameter models in under 15 minutes. In an agent network, such proofs can support verifiable model identity or policy compliance, though latency and proving scope still limit per-action deployment. [Source](https://dl.acm.org/doi/10.1145/3658644.3670334)

## Reputation, accountability, and dispute resolution

**Chan et al. (2025) - Infrastructure for AI Agents.** The paper defines agent infrastructure as technical systems and shared protocols external to agents. It groups functions into (1) attributing actions and properties, (2) shaping interactions, and (3) detecting and remedying harmful action. The agenda is broad by design and provides the clearest bridge from model-level safety research to population-level governance. [Source](https://arxiv.org/abs/2501.10114)

**Kolt (2025) - Governing AI Agents.** Principal-agent theory highlights information asymmetry, delegated discretion, and loyalty failures; agency law highlights attribution, authority, and liability. Kolt argues that familiar tools such as incentives, monitoring, and enforcement may strain when agents act opaquely at machine speed and scale. The proposed direction combines legal rules with technical infrastructure that improves visibility and assigns responsibility. [Source](https://arxiv.org/abs/2501.07913)

**Hadfield and Koh (2025) - An Economy of AI Agents.** This economics chapter asks how autonomous agents will enter contracts, form organizations, compete, transact with humans, and change market design. It identifies institutional questions rather than running agent experiments. For evaluation, it motivates metrics beyond task completion: market concentration, allocative efficiency, fraud, bargaining power, externalities, and the incidence of losses. [Source](https://arxiv.org/abs/2509.01063)

**Tomasev et al. (2025) - Virtual Agent Economies.** The paper classifies a sandbox economy along two axes: emergent versus intentional origin, and permeable versus impermeable connection to the human economy. It discusses auctions, mission economies, and sociotechnical infrastructure as tools for steering allocation and collective goals. A safety testbed based on this proposal should quantify leakage across the sandbox boundary, market stability, inequality, audit coverage, and recovery after coordinated manipulation. [Source](https://arxiv.org/abs/2509.10147)

## Commitments and delegation

**Tennenholtz (2004) - Program Equilibrium.** Strategies are computer programs that can inspect one another, allowing conditional commitments that ordinary normal-form strategies cannot express. The paper shows mutual cooperation in a one-shot Prisoner's Dilemma under program equilibrium and characterizes the achievable payoffs as the feasible, individually rational set. This is foundational for credible machine commitments, but real deployments must handle imperfect verification, heterogeneous languages, resource bounds, and malicious code. [Source](https://www.sciencedirect.com/science/article/pii/S0899825604000314)

**Google (2025) - A2A: A New Era of Agent Interoperability.** A2A is a cited protocol announcement rather than a research paper. It illustrates discovery, capability description, task exchange, and cross-vendor communication between agents. Those same interfaces create concrete enforcement points for authentication, least-privilege delegation, signed messages, provenance logs, rate limits, and revocation. [Source](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)

## Infrastructure stack for experiments

| Layer | Minimum experimental primitive | Safety question |
|---|---|---|
| Identity | Instance ID, principal/deployer binding, key rotation | Can an action be linked to the correct agent and responsible party? |
| Admission | Capability claims, attestations, authorization policy | Should this agent be allowed into this environment or interaction? |
| Messaging | Signed envelopes, scopes, replay protection, trace IDs | Can messages be authenticated and reconstructed without granting excess authority? |
| Provenance | Model/version claim, watermark or proof, tool and data lineage | Is the claimed origin or computation verifiable? |
| Commitment | Machine-readable contract, deadlines, escrow, revocation | Can counterparties rely on promises without making unsafe irreversible commitments? |
| Reputation | Outcome history with uncertainty and anti-Sybil controls | Does past evidence predict behavior under changed partners and incentives? |
| Remedy | Audit, dispute process, quarantine, compensation, rollback | What happens after a detected failure, and who bears the cost? |

Infrastructure benchmarks should include adversarial identity changes, forged claims, selective disclosure, collusive reputation inflation, Sybil attacks, ambiguous delegation chains, revocation races, and cross-protocol failures. Success should combine security, latency, privacy, interoperability, and task utility.
