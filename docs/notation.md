# Notation — DD-000

## General framework

| Symbol | Meaning | Conditions |
|---|---|---|
| \(\Omega,\omega\) | world space and realized world | finite or measurable |
| \(\mu\) | prior on worlds | probability measure |
| \(E\) | evidence-generating kernel | includes dependence/provenance |
| \(I\) | information architecture | agents, messages, histories, timing |
| \(A_i,A\) | agent and joint action spaces | \(A=\prod_i A_i\) before constraints |
| \(\Gamma\) | coverage/discovery technology | world + actions to outcomes/value |
| \(B\) | action/resource budget | scalar or general constraint |
| \(\tau\) | timing, feedback, adaptation, stopping | part of feasibility |
| \(R\) | reward/credit rule | agent utilities, not necessarily social value |
| \(\Pi\) | action protocol | stochastic kernel from information histories to joint actions |
| \(S_\Pi\) | induced action set/multiset/sequence | representation must match \(\Gamma\) |
| \(v_\omega(S)\) | realized discovery value | bounded for stated expectation |
| \(G_B(\Pi;I)\) | expected discovery | social objective |
| \(\mathcal P_B(I)\) | feasible protocol class | must be declared |
| \(V_B(I)\) | information frontier | \(\sup_{\Pi\in\mathcal P_B(I)}G_B\) |
| \(L_B(\Pi;I)\) | protocol loss | \(V_B-G_B\) for feasible \(\Pi\) |

## Atomic one-target model

| Symbol | Meaning |
|---|---|
| \(M,N\) | number of candidate boxes and searchers/actions |
| \(\theta\) | unique target location |
| \(X_i\) | private signal/report of agent \(i\) |
| \(p\) | clue accuracy; false labels have probability \((1-p)/(M-1)\) |
| \(C_j\) | number of reports naming candidate \(j\) |
| \(Q\) | average standalone action quality |
| \(K\) | number of actions that hit the target |
| \(G\) | union discovery probability \(\Pr(K\ge1)\) |
| \(D\) | number of distinct proposed/action labels when specified |
| \(L^*\) | recovery budget for a stated information architecture/benchmark |
| \(c\) | upstream common-cue copying probability, not pairwise correlation |
| \(N_{\mathrm{eff}}\) | upstream model-specific effective-channel count |

Use \(B\) for a general budget and \(L\) for atomic action count. Use \(L_B\) only with its arguments to avoid confusing protocol loss with action count.
