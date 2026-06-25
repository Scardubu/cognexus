# Cognexus v3.3.1 Repository Inventory

**Distribution:** `nexus-openai`
**Version:** `3.3.1`
**Inventoried source files:** **515**
**Inventoried bytes:** **2,431,097**

This inventory is generated deterministically by `scripts/generate_repository_inventory.py`. Generated build, distribution, coverage, cache, database, local virtual-environment, secret environment, and evidence-artifact state is excluded. The inventory document itself is excluded to avoid a self-referential digest.

## Architecture surfaces

| Path | Responsibility |
|---|---|
| `config/` | validated settings, registry and stack manifests |
| `orchestrator/` | classification, execution modes, routing, conflicts and response assembly |
| `nexus_agents/` | specialist construction and registry |
| `server/` | FastAPI application, schemas, middleware and launcher |
| `sessions/` | SQLite/Redis persistence, compaction and continuity intelligence |
| `observability/` | structured logging, metrics, tracing and privacy processors |
| `security/` | identifier, policy, rate-limit, sanitization and secret controls |
| `skill_runtime/` | portable skill loading, validation, packaging and tool exposure |
| `.agents/skills/` | canonical portable skill definitions and operational assets |
| `deploy/` | OpenTelemetry and Kubernetes deployment resources |
| `scripts/` | quality, release, SBOM, inventory and deployment verification tooling |
| `tests/` | unit, integration, regression, failure and security tests |
| `.github/workflows/` | CI, security, release, container and deployment gates |

## Console entry points

| Command | Target |
|---|---|
| `cognexus` | `orchestrator.run:main` |
| `cognexus-server` | `server.run:main` |
| `cognexus-skills` | `skill_runtime.cli:main` |

## Files by top-level path

| Path | Files |
|---|---:|
| `.agents` | 166 |
| `.codex` | 1 |
| `.cursorrules` | 1 |
| `.dockerignore` | 1 |
| `.env.example` | 1 |
| `.github` | 7 |
| `.gitignore` | 1 |
| `AGENTS.md` | 1 |
| `CHANGELOG.md` | 1 |
| `CONTRIBUTING.md` | 1 |
| `DELIVERY.md` | 1 |
| `Dockerfile` | 1 |
| `FAQ.md` | 1 |
| `MANIFEST.in` | 1 |
| `Makefile` | 1 |
| `QUICKSTART.md` | 1 |
| `README.md` | 1 |
| `SECURITY.md` | 1 |
| `TROUBLESHOOTING.md` | 1 |
| `config` | 4 |
| `constraints` | 1 |
| `deploy` | 11 |
| `docker-compose.yml` | 1 |
| `docs` | 26 |
| `evals` | 2 |
| `middleware` | 6 |
| `nexus_agents` | 4 |
| `observability` | 5 |
| `orchestrator` | 12 |
| `pyproject.toml` | 1 |
| `requirements-dev.txt` | 1 |
| `requirements.txt` | 1 |
| `scripts` | 19 |
| `security` | 6 |
| `server` | 8 |
| `sessions` | 6 |
| `skill_runtime` | 173 |
| `skills` | 1 |
| `tests` | 25 |
| `tools` | 5 |
| `tracing` | 2 |
| `validators` | 5 |

## Files by extension

| Extension | Files |
|---|---:|
| `.example` | 1 |
| `.in` | 1 |
| `.json` | 2 |
| `.md` | 357 |
| `.py` | 117 |
| `.sh` | 1 |
| `.toml` | 1 |
| `.txt` | 3 |
| `.yaml` | 20 |
| `.yml` | 7 |
| `<none>` | 5 |

## Complete source file manifest

| Path | Bytes | SHA-256 |
|---|---:|---|
| `.agents/skills/accessibility-system-architect/SKILL.md` | 5049 | `11805714c61c11b926a582922e4cf25540a28958a3564ed1a97eb5e0a2493200` |
| `.agents/skills/accessibility-system-architect/examples/usage.md` | 1131 | `569d123d9874c533c3cc754eba3f627be6ccc3e18e68a9c6ab3bedfd7c5517fa` |
| `.agents/skills/accessibility-system-architect/references/checklist.md` | 1577 | `933e45ec35325456e20b85716406c8172acf474e6c8de272a9a31319fa76a390` |
| `.agents/skills/accessibility-system-architect/references/guidance.md` | 13780 | `f34abdea4b5dd71457afb033d391b9abdc82f5e171cfa7dff052702a4af84546` |
| `.agents/skills/agent-prompt-upgrade/SKILL.md` | 5311 | `377f8d66937020ba18c960117ba40b999dc2b75ab08f61f31a61823fa355e865` |
| `.agents/skills/agent-prompt-upgrade/examples/usage.md` | 1109 | `cf08d972a1c1f8e904e6a4cd0330a41e359e6c095c21ee9ccc640818b5b1c885` |
| `.agents/skills/agent-prompt-upgrade/references/checklist.md` | 1550 | `245221cd6cf15d3ba716de8f269baf877b3fd7e7970af24d81184c73eb2f25cb` |
| `.agents/skills/agent-prompt-upgrade/references/guidance.md` | 5667 | `15720d517c6e8d6d5e3553f3ec8a732d6d5c1fe4d4773990b279f53d372149dc` |
| `.agents/skills/ai-feature-architect/SKILL.md` | 5233 | `28025813c0278c697321dfb6c94e91b2511e2649b3b4c7efaac7001c9ad009d8` |
| `.agents/skills/ai-feature-architect/examples/usage.md` | 1081 | `26c4cd25edbb1255b4a273097fdceea7fee457e2648cd6b291c9f98ffe03e38e` |
| `.agents/skills/ai-feature-architect/references/checklist.md` | 1558 | `ea92c766cb42473f4902e08ede89b06995559a42910dd3d7a12617e174f39c45` |
| `.agents/skills/ai-feature-architect/references/guidance.md` | 11348 | `dc0059b166e9c463686f5cf358f18c4a43695710fef52b8479daee74150b49e7` |
| `.agents/skills/api-automation-architect/SKILL.md` | 5282 | `31692d5322ef702d531ae28d8150484d886a2df994ac4841ab9538ba0e17bc3f` |
| `.agents/skills/api-automation-architect/examples/usage.md` | 1101 | `465c502ce1d62d95cdfa9b37a39a6f3a0b5ef8ad1b131d2997ec42a4bdb52eae` |
| `.agents/skills/api-automation-architect/references/checklist.md` | 1643 | `7dea48905d36b06ae05ccf72a42ae815e22e76569b5c25c30c12450585bcaf8d` |
| `.agents/skills/api-automation-architect/references/guidance.md` | 6184 | `5620f75e4315b381f0706aa6fb57742f8046df2fdb99ee31d57ce341b1af8c30` |
| `.agents/skills/api-contract-governance-architect/SKILL.md` | 3873 | `f3e6f50e040310e998be199a3cc4ded3d31deef62db830631be323e9ef980d6f` |
| `.agents/skills/api-contract-governance-architect/assets/openapi-governance-policy.yaml` | 831 | `465478125086d123f5664d32ffe795d02f5431483677b154d4162fc1181ff340` |
| `.agents/skills/api-contract-governance-architect/examples/usage.md` | 3548 | `324dfb58d3e25372bf3f94f6f1a87722ae532c63dd3f8f484c7e4e37214165c7` |
| `.agents/skills/api-contract-governance-architect/references/checklist.md` | 2742 | `bb9cd411934894eb57fc879c4e0e03bdf4ebc2e9b5b189823f0ffd0cb0cd347c` |
| `.agents/skills/api-contract-governance-architect/references/guidance.md` | 21883 | `da820d10463c24cd9568546bab1d0be11e74fa54f5a6526808949a7e0476338c` |
| `.agents/skills/api-contract-governance-architect/references/playbooks.md` | 2331 | `589688fff1b898e1989c0c68dd6ef01fdd1182cbd71426ab53c40734981a515d` |
| `.agents/skills/api-contract-governance-architect/scripts/validate_contract_policy.py` | 3804 | `d4aa4477d2831b8680eef09ff2b913f6ede66a9b8aec58ae70e20a17bd8b165d` |
| `.agents/skills/backend-domain-model-architect/SKILL.md` | 5222 | `73099ad0cd3ae7ce46136fb907326625dbb6538794360cf7d0bec160858eefc7` |
| `.agents/skills/backend-domain-model-architect/examples/usage.md` | 1131 | `b3ea61acf7a1e5b2ffa53b4e44cc0a875155347f21b8ecd423ea8489f97d0893` |
| `.agents/skills/backend-domain-model-architect/references/checklist.md` | 1622 | `9b32ea690c27e0f763919f0e16993b0221ed4277a82875e5ce7303435645a1a6` |
| `.agents/skills/backend-domain-model-architect/references/guidance.md` | 10782 | `cee7445f8dc9082865b1766e1a871f69f2cd56c4268d94d82d9e25e74a956bea` |
| `.agents/skills/backend-systems-auditor/SKILL.md` | 5487 | `627cc826b19d22f47213f4f029a2ebd16507caf18e35d71ee7fc96de6d77c6ce` |
| `.agents/skills/backend-systems-auditor/examples/usage.md` | 1096 | `a534dac803bed3be176ee2c81ebc9ef3a11588ddf4dec181340caf6846a9f9f1` |
| `.agents/skills/backend-systems-auditor/references/checklist.md` | 1780 | `d49643d8170c12649f08c217be81c849d7f7a08cb8766989432d009ff9daa9d1` |
| `.agents/skills/backend-systems-auditor/references/guidance.md` | 7310 | `0dee0e3cb7afac46aaef28825515a3b0e7733d48b64d59dbd5919b9b52e4e05e` |
| `.agents/skills/bullmq-job-architect/SKILL.md` | 5320 | `db4ef9431eb3c630c9ee250dffb82a8c66b08bc6f433ae4fcba81edad15ae429` |
| `.agents/skills/bullmq-job-architect/examples/usage.md` | 1081 | `37ae2d8f153ab2d6a101892e72bce362d2590bdbeb12a0a219ac24d5c932db02` |
| `.agents/skills/bullmq-job-architect/references/checklist.md` | 1666 | `9e6a2d8777c76ceb24fea625c4a7f3826d9c664c4a3b21ae3510b1057d3303ca` |
| `.agents/skills/bullmq-job-architect/references/guidance.md` | 11588 | `07c6b5d88f3434bb08389c57d54e95b362de9ca74cc13e70351088ca5c31e0be` |
| `.agents/skills/codebase-zip-audit/SKILL.md` | 5040 | `e83774b2e63204e5a704437ea04b1b86d116119cb1701a044f6d5cc3f713b790` |
| `.agents/skills/codebase-zip-audit/examples/usage.md` | 1084 | `568b3229fd20b07afc6caac9cabca859ec5f5c99dcd083057f347792fc16b31a` |
| `.agents/skills/codebase-zip-audit/references/checklist.md` | 1630 | `795216e8c1fb51cdc5dea41184e00c63b60f4ae4e9a3dc74ce03da049a6ecbb5` |
| `.agents/skills/codebase-zip-audit/references/guidance.md` | 5744 | `6d8fbc9460d9cb534963809f4a6f3cf39a45fd045c2d1de154d3fae3f92e52c9` |
| `.agents/skills/component-quality-gate/SKILL.md` | 5295 | `c81bd47af354629fc3e4cd564b215a78342dbdba19230f01afa0f0060d024771` |
| `.agents/skills/component-quality-gate/examples/usage.md` | 1091 | `13255749fbcb0e80756759f9697db01468d29b509a19c9af0f6847af198208aa` |
| `.agents/skills/component-quality-gate/references/checklist.md` | 1659 | `6eb44006cdd9994e1ffc2494cb8239d8572b9cd0b62ab3fe8d589f6ae32ead35` |
| `.agents/skills/component-quality-gate/references/guidance.md` | 9250 | `99822e744f7bfc8444a72c06fd733a631d8cb13c35b8b038a2ad6954c138245c` |
| `.agents/skills/data-visualization-architect/SKILL.md` | 5575 | `8bdab5d7d612554d4856c254b71d2347a2599326ecc67eb7beb989efcc20c51c` |
| `.agents/skills/data-visualization-architect/examples/usage.md` | 1121 | `be73ec02ed23a29152fdbd061e8dfee8793b3cc900ed00ae9c3c4e8f8511d7d9` |
| `.agents/skills/data-visualization-architect/references/checklist.md` | 1532 | `98e8a962b31714843336bd6f8f354e3fcc93b339d5006d7b3ec31cdd6189e609` |
| `.agents/skills/data-visualization-architect/references/guidance.md` | 14252 | `d8cae66ab8690a390ae72117c9a8017ccc8d1655084a8bc946dd242f03eded61` |
| `.agents/skills/design-token-system-architect/SKILL.md` | 5294 | `227b807856b5d324ea98b70a80ec55eaeded42115d663733ec0847ebba0caeda` |
| `.agents/skills/design-token-system-architect/examples/usage.md` | 1126 | `3c4f4a4c4356bfe62d238b3902df703e996d2944d13a19eeb9a02c7d3dad0fca` |
| `.agents/skills/design-token-system-architect/references/checklist.md` | 1596 | `8e0e83f1e528518567be1af52d37f214042ddfce8a605572ecdd5744b40e315b` |
| `.agents/skills/design-token-system-architect/references/guidance.md` | 15378 | `0964cee228ed4f4910c92d42058b458ea8119afeaaf6b421ae9a53af4cde682a` |
| `.agents/skills/edge-cache-architecture-architect/SKILL.md` | 3772 | `91ef88b6ba790e3d7dfe18591a5a153434939c9c6f8726ebe4691cedd4a87c29` |
| `.agents/skills/edge-cache-architecture-architect/assets/cache-policy.yaml` | 1098 | `6a1abff1de2470857a8499e12bac585d6b0d7f83ef12404ff9650206c62cb5a2` |
| `.agents/skills/edge-cache-architecture-architect/examples/usage.md` | 3576 | `6c5c8ee76fae2af2fca6063958697d62d244d61fa84c2e3f0371844a2a7aa1be` |
| `.agents/skills/edge-cache-architecture-architect/references/checklist.md` | 3124 | `d7b185d22cc0efbb7d256f35019a46b1e58381fa938ea15ffd2a46794e2593b2` |
| `.agents/skills/edge-cache-architecture-architect/references/guidance.md` | 17826 | `7cf29a5d60cdb13d3fe300cad22d3f8d3dfb394099914c7f2bb9175b1cae92d3` |
| `.agents/skills/edge-cache-architecture-architect/references/playbooks.md` | 1994 | `3b32a59155f80e51c5e08c0a1fd7b1f39173ca9f62a50dbee7cb027b13fa7b22` |
| `.agents/skills/edge-cache-architecture-architect/scripts/validate_cache_policy.py` | 4114 | `b13108ea555460600386df1ba13abc11d75a6e009f4f2e4e8d0cbb5dcc41a022` |
| `.agents/skills/effect-ts-layer-architect/SKILL.md` | 5263 | `63ea1b1220aafa59b4f008660623357e8811855f0a67b3d044b1c86a4206dd2d` |
| `.agents/skills/effect-ts-layer-architect/examples/usage.md` | 1106 | `ce06b60ffd992922347cb84b3ae5f32885d3d1fe2236287cf3e6c9ba71bfa07e` |
| `.agents/skills/effect-ts-layer-architect/references/checklist.md` | 1616 | `3acaf4f248f2465fb28442f0aef66c245c987b859cec7222590683bc22da2319` |
| `.agents/skills/effect-ts-layer-architect/references/guidance.md` | 5619 | `23568ed28f38bbed931628a3f8548c3284f0fcb9ab7dd42885c1117191fb9f25` |
| `.agents/skills/elite-skill-forge/SKILL.md` | 5048 | `a5282f8146606b1bf68096a688b177323c7d0b3f2b6e588adeb46be63567061e` |
| `.agents/skills/elite-skill-forge/examples/usage.md` | 1066 | `21182b5ff83df8a974a96e5176fd082929e09280432648b16fbc9be5137aa056` |
| `.agents/skills/elite-skill-forge/references/checklist.md` | 1679 | `f5fd9415c578160d47ddb682d6a5765fce107579f5cb8ad82e108ee746570cb2` |
| `.agents/skills/elite-skill-forge/references/guidance.md` | 9186 | `8a92402cd7e41b8669776cd5d13467ec457666c5e2c4163add2868049d972967` |
| `.agents/skills/frontend-design-auditor/SKILL.md` | 5362 | `c4506074aec44eed01e56392ce70835bcab001d5e2b1ef350477861994cb6b3b` |
| `.agents/skills/frontend-design-auditor/examples/usage.md` | 1096 | `41b6bc061781e35c8bbbc96dcc93d7ee276111b0918ef3f56a7ce8e839459bd8` |
| `.agents/skills/frontend-design-auditor/references/checklist.md` | 1754 | `4157369d764f4f532ff405a5e5c80a7570db4aff6284856539482f07507b1862` |
| `.agents/skills/frontend-design-auditor/references/guidance.md` | 6234 | `0f545a6c0d38c9865c627eab0bf0a1208bccae7708f5c257b0b18946201c2d08` |
| `.agents/skills/frontend-product-design-architect/SKILL.md` | 5282 | `04873a9c936143157c284a8e966f89d4453ce80e9e908bf30094f61bbf84d551` |
| `.agents/skills/frontend-product-design-architect/examples/usage.md` | 1146 | `f4676731a79a4ac22220a8a8bc8d0fcf57cf853ac5c39b7b5ef63853a59ba07d` |
| `.agents/skills/frontend-product-design-architect/references/checklist.md` | 1704 | `ed180624c1db19c917e7eb215d2cd33d42c150d77caa3df79c30bfe5db12c064` |
| `.agents/skills/frontend-product-design-architect/references/guidance.md` | 9974 | `5663e132bec6add9caa8590cc8f953536953c1434ef0b130ca0e798326510a34` |
| `.agents/skills/git-workflow-architect/SKILL.md` | 5335 | `75cd42e418d3ad042988f0423ed092614830cc64281ec89bd50c48e58306f882` |
| `.agents/skills/git-workflow-architect/examples/usage.md` | 1087 | `39c989d7e2a7216d9b1436d33dcdb5032e8a860df934c7d144188d755aa09302` |
| `.agents/skills/git-workflow-architect/references/checklist.md` | 1587 | `211ed505492a1b6a9d093b73859d735da912af35605b4359b0f31e581716c827` |
| `.agents/skills/git-workflow-architect/references/guidance.md` | 12576 | `f91d88b7c8a8d6e4ea0fd48262cd308146760a65734b87889d32ab1c8031432e` |
| `.agents/skills/motion-interaction-architect/SKILL.md` | 5407 | `630dcb538f780e02223430c88d5593441b07cd3553ee4dd49e69020ea953ede6` |
| `.agents/skills/motion-interaction-architect/examples/usage.md` | 1123 | `72ad4a559e83a0a8f7c272d934c53ae9c7b1768143f2fc69103a02d4d76a79fb` |
| `.agents/skills/motion-interaction-architect/references/checklist.md` | 1535 | `531bd5c2b05765e4defef9d9ac1ed6749c3c059a3d690ca92a8a451da22cd7ab` |
| `.agents/skills/motion-interaction-architect/references/guidance.md` | 10760 | `9ec66b6dbd9a359cf83bf50d9ae47f2bfc4885f7da148a1da11926df1f7f8eaa` |
| `.agents/skills/motion-performance-architect/SKILL.md` | 5157 | `f8e8e2759f939fe2ff3facff5029c818ab15cc25d5f543c575d819986586721b` |
| `.agents/skills/motion-performance-architect/examples/usage.md` | 1121 | `fe59b1976cd0eaf3733dabb268bdc0cde00fc24df1f8be563e055f3479fd517a` |
| `.agents/skills/motion-performance-architect/references/checklist.md` | 1804 | `c9fe6a2452c75411ffe3d6c5411d183555a04ee398913646c643f6973c18eb3d` |
| `.agents/skills/motion-performance-architect/references/guidance.md` | 8906 | `d8ed9a5d28a0964dff1e427957176a89deabdc9819ba40a4876cb35f1c13ffc9` |
| `.agents/skills/multi-agent-orchestration-architect/SKILL.md` | 5316 | `d0180dd4db68c4e5c78e6ecfbc959269152d5676fbf4930dc1b3d1584094a2d0` |
| `.agents/skills/multi-agent-orchestration-architect/examples/usage.md` | 1156 | `9e3dad77ec4e6cabf7ecdda6bc361b1b368ac6dbe7fdb099843991e33c07cfea` |
| `.agents/skills/multi-agent-orchestration-architect/references/checklist.md` | 1561 | `434355deb587684d507c34cd7e61258a6d069d089bc1c68c338e2d798cf17f52` |
| `.agents/skills/multi-agent-orchestration-architect/references/guidance.md` | 13288 | `e3cbd00441e50c47dd927c00466c763d75bef0f32705c643bdea54030d4d985b` |
| `.agents/skills/nextjs-performance-architect/SKILL.md` | 5264 | `a16b48c12ad6749730f9a17d9d605c1cf915b480aefdc91151992ec3be4ce893` |
| `.agents/skills/nextjs-performance-architect/examples/usage.md` | 1122 | `fafdd016dd92fcdbadad16543effbbaf59e5709053f0db8ab53edc6daef9b93f` |
| `.agents/skills/nextjs-performance-architect/references/checklist.md` | 1562 | `bdd2bc845c0c106528f8938e6f3149769cf2bb5d83d108839c4bbcc5c991d959` |
| `.agents/skills/nextjs-performance-architect/references/guidance.md` | 10525 | `641f54c042dd3bd40266883d57eac243b03fcc73bd7f85924fb6ac49e53349a3` |
| `.agents/skills/nigerian-fintech-compliance-architect/SKILL.md` | 5650 | `8207ecfa6ece7c3e5ef8c6a564d41128c1bded53eb2cc1c7d4d025a7cdbf4095` |
| `.agents/skills/nigerian-fintech-compliance-architect/examples/usage.md` | 1166 | `5eb8cefca93549373a3e9382715b19ee6232ebfd5eb53aa35199a113cda5724a` |
| `.agents/skills/nigerian-fintech-compliance-architect/references/checklist.md` | 1668 | `fcc1ac865519dd9aeacf2b0c31727fa176a9cdd76af9e35cd252f305b41cf5f8` |
| `.agents/skills/nigerian-fintech-compliance-architect/references/guidance.md` | 12825 | `40a0980c8813c5122c6532fcc17f0b759c9e1470e05a75101e8df66301f3ac55` |
| `.agents/skills/opentelemetry-observability-architect/SKILL.md` | 5502 | `787bf96a1cebac1b5db488dede76f809cfa77f8dca6136fe287617594d20e6f6` |
| `.agents/skills/opentelemetry-observability-architect/examples/usage.md` | 1166 | `310bd30a1a9aa34a461bf013800fb4815ea45ec354688836e9819ba9d4dbf50d` |
| `.agents/skills/opentelemetry-observability-architect/references/checklist.md` | 1593 | `df4f2d348bc836f34841e327ad00a6814c181f9b74af596af59658dd83189862` |
| `.agents/skills/opentelemetry-observability-architect/references/guidance.md` | 12105 | `cac71ffbe722a32dbd1c131c78924630a2d15d1b2c581bfb379e46a574bf8881` |
| `.agents/skills/portfolio-conviction-engine/SKILL.md` | 5462 | `0d67c9d1c5d25dc2a2de3fdfad0b9847f9bddf472b64f1bc3447471ba5354fb3` |
| `.agents/skills/portfolio-conviction-engine/examples/usage.md` | 1122 | `dd328bc6710c26002b77feedf69ce4b2bde6f63129e8c59997d3badc02b6d481` |
| `.agents/skills/portfolio-conviction-engine/references/checklist.md` | 1607 | `cf5aaed2b8adcdffe1d3ccd373f48d62cf435f29183d8c8f586a44c3e659dea8` |
| `.agents/skills/portfolio-conviction-engine/references/guidance.md` | 7067 | `16babeeb29347d74c45ea21972716745c2de319a346185a1e9f262c12733e338` |
| `.agents/skills/prisma-database-architect/SKILL.md` | 5169 | `e96405d641826e8288dbbc24f937a601202de4fa2b1c14bbd8824bf5c296293d` |
| `.agents/skills/prisma-database-architect/examples/usage.md` | 1106 | `db636ffd23c8d18ab19c6e4fc5d0db192b0719afab79d39c4ae7df8552c2bff8` |
| `.agents/skills/prisma-database-architect/references/checklist.md` | 1545 | `77d03d22d87993cf05a1528c0b0bbe40bea245a7b4eff41cfe0cee6e4dbdac63` |
| `.agents/skills/prisma-database-architect/references/guidance.md` | 11238 | `60d3eb9b51bea665a4427c6105dc3a74b8d44cd3e0ecfb99d3f6010d858d5943` |
| `.agents/skills/prompt-engineering-architect/SKILL.md` | 5405 | `a4b8fb59e7c4df8a4ffe70bca5358a9ed3d1ce4e3b1938cc025ae4815552c7f7` |
| `.agents/skills/prompt-engineering-architect/examples/usage.md` | 1121 | `5dbdd5261cf59d1c63cbdbdbf39f0b7abfb532688a5c67d3d757d6989c676e44` |
| `.agents/skills/prompt-engineering-architect/references/checklist.md` | 1637 | `3832ba4abbeb8b884eb1f31290dc095228ab466458e040ad7026c53742cd743a` |
| `.agents/skills/prompt-engineering-architect/references/guidance.md` | 10938 | `b4c850d9fc622accc308ac3b9749b9cca9cebff430b95fc7348e00c20ad1d3cf` |
| `.agents/skills/react-native-expo-architect/SKILL.md` | 5374 | `057717c312b09f30a9715f2867177116e295db8b6d9ca85ff27b420f375cf7fe` |
| `.agents/skills/react-native-expo-architect/examples/usage.md` | 1116 | `e5cbd114e74a309201b570352dcaa017b1201ddd2f8880291ec4e58821a5d87e` |
| `.agents/skills/react-native-expo-architect/references/checklist.md` | 1508 | `b96e62003693dec6d644c882895ea97d574cd0a9901607efc9159cb75dd6e92e` |
| `.agents/skills/react-native-expo-architect/references/guidance.md` | 9886 | `e651e86cde5ddddc9c9e51371d2c0ff87432607c10999e73024735167be30b38` |
| `.agents/skills/real-time-systems-architect/SKILL.md` | 5407 | `9dac159c3630022ca4dfe3f38d4323493e79be8a7793a2e31965b858c8028515` |
| `.agents/skills/real-time-systems-architect/examples/usage.md` | 1116 | `4340efc73aae9abb4fb662c72a3491910eef76509799056c0e0ccf1f466a5abd` |
| `.agents/skills/real-time-systems-architect/references/checklist.md` | 1588 | `5b3227f1c0864ce2a5ad1cfb7fab33dad02beac534e028f26dd9d13e9432fed8` |
| `.agents/skills/real-time-systems-architect/references/guidance.md` | 14090 | `f9315bda178fbddfd5df4fd5b5a792f4f6b7ac26b653600cee4617bd7419198b` |
| `.agents/skills/release-incident-operations-architect/SKILL.md` | 3588 | `ba9ba410f1d52027b578534879ea852930043cf81364cceda42c15c33901084b` |
| `.agents/skills/release-incident-operations-architect/assets/incident-command-template.md` | 952 | `f474e3e735237352581885b3492e9aa8846bca7a2d478ce61926d22ea5d06322` |
| `.agents/skills/release-incident-operations-architect/assets/release-verification-policy.yaml` | 1084 | `6b5834e9c9159ff78ea4e4fd6c747de76de90a2c0593e5ce763081a747f090b6` |
| `.agents/skills/release-incident-operations-architect/examples/usage.md` | 3823 | `d0ef620b47598eb24e5b1bdd66f44879305ced242e4bc2dd46d036844b2aaebf` |
| `.agents/skills/release-incident-operations-architect/references/checklist.md` | 3092 | `5ba20c077bef96b5e5e10ac865579b36236cf4fb872506a0467c8c18ab7c8e9f` |
| `.agents/skills/release-incident-operations-architect/references/guidance.md` | 19757 | `3f790e049951753d8882084648da7f0b8e2b8dc321c0fdb71f2007c7485234fb` |
| `.agents/skills/release-incident-operations-architect/references/playbooks.md` | 2244 | `68abe231ceea4602685b4d56ded9d71e05d1df590ba665d8eab82df858edfbe8` |
| `.agents/skills/release-incident-operations-architect/scripts/validate_release_policy.py` | 4533 | `26b8b96923704b3908e3ecbacb0f9c961224f9d57e03d3b7551012591c633955` |
| `.agents/skills/security-hardening-auditor/SKILL.md` | 5581 | `d5a460cdfb594e6ebeab4e400433da31050e3d6fba1cb5315d9520b81534ae4d` |
| `.agents/skills/security-hardening-auditor/examples/usage.md` | 1111 | `efcb9200790afd75ef57908626aba2653ea167b4a5653bd5b88835a1876ac5a7` |
| `.agents/skills/security-hardening-auditor/references/checklist.md` | 1802 | `4b25050f3ca25a61203e88e60927de7de72953949c4686df4646c6c2ceffd569` |
| `.agents/skills/security-hardening-auditor/references/guidance.md` | 12109 | `0d99a806c613699d572b6cdeca2aad08d5511b0d0aa668e6d5c36f4107aaae66` |
| `.agents/skills/shell-cognitive-os/SKILL.md` | 5188 | `9008c8cd4fa93fba7ddf1f0503f0b5fd24d0feaf1dea8cc73c21090e1452622b` |
| `.agents/skills/shell-cognitive-os/examples/usage.md` | 1086 | `6f25539f275e28d566c0e3e974aa3663d2982286a40ca4f6f7df91472087ebb1` |
| `.agents/skills/shell-cognitive-os/references/checklist.md` | 1516 | `2e76381198fbf7f9842c096674dab46a838c9b20d196525a11a2b28683174cd3` |
| `.agents/skills/shell-cognitive-os/references/guidance.md` | 5926 | `b83b50351a1a4016e9f89df6cd45ab0ee9429a1d4903ae441ff71ae484564324` |
| `.agents/skills/surgical-merge/SKILL.md` | 5177 | `f475ef27c3626149f527ab68a5ed675719fc4f746f45754bb43d858eefbb2e24` |
| `.agents/skills/surgical-merge/examples/usage.md` | 1061 | `5f3b34d1f7120ac89e2873de7deffdc257c0e7c358a9c5063db6a5a16c0194b5` |
| `.agents/skills/surgical-merge/references/checklist.md` | 1542 | `0223fe875406244c061a31d4f89bbbed76df64210058529c083b6e9957208fee` |
| `.agents/skills/surgical-merge/references/guidance.md` | 4631 | `96fccc64898f43550c24c48f5bd8ea712e62e7819b6e27c7c203a125d8b23b32` |
| `.agents/skills/testing-strategy-architect/SKILL.md` | 5345 | `73fee5e5c3e5a14e2c8e0fb035c83c7a01c8d222283b4057141307b29601acf6` |
| `.agents/skills/testing-strategy-architect/examples/usage.md` | 1111 | `f299b10454dc4b3142fbc4ec5869ecb1ab8222b8b384fe93cf5c743a7aca344c` |
| `.agents/skills/testing-strategy-architect/references/checklist.md` | 1571 | `5cbb49d2c50440d45071b23aa725bf828012279048291a19442d295ba3c316d1` |
| `.agents/skills/testing-strategy-architect/references/guidance.md` | 12515 | `54548a16774f5584e888531c26b0a9a8456afae5a65c09953b707eb3ffa1f496` |
| `.agents/skills/typescript-config-surgeon/SKILL.md` | 5482 | `c030b0c8d9eff8aa2c3fed3fcd2fac97939aaaca60006d20099b41bf07d3369e` |
| `.agents/skills/typescript-config-surgeon/examples/usage.md` | 1106 | `64b23deb75fe4814f025a4f1e7ce3c3d2e10b97bb1670f77f2c4fc3db867ef47` |
| `.agents/skills/typescript-config-surgeon/references/checklist.md` | 1519 | `1adf06fed670ce51a3b990deb298c110c4a39281455d18d55338c0f2b69bf9a4` |
| `.agents/skills/typescript-config-surgeon/references/guidance.md` | 13492 | `6ba1491984e44ffe88643942a5285b9f35a240cc10429a2a5bb6f863fa9d5a4a` |
| `.agents/skills/vscode-ai-agent-stack/SKILL.md` | 5319 | `cc88360b5e4fd20f5e4fefd1c938d56629ebaf09f7736ca441e6e259f8efdf94` |
| `.agents/skills/vscode-ai-agent-stack/examples/usage.md` | 1087 | `db1d9bff6f31740674ee678712dc9bad1bd20f01cf093a2193d445529f163661` |
| `.agents/skills/vscode-ai-agent-stack/references/checklist.md` | 1777 | `a4301e9484cf13e743bda881a8846e238e3b14fe6a0fa005e352667a8f58d644` |
| `.agents/skills/vscode-ai-agent-stack/references/guidance.md` | 9514 | `aac84a93717fa1863385652a91b727f340019cb5e6f3d6b2d4b4f3e59fe161d5` |
| `.agents/skills/vscode-cognitive-os/SKILL.md` | 5125 | `1a61696556764a01f9888bb298f5dc00e0d95ff41a55935dca157d4db62a1749` |
| `.agents/skills/vscode-cognitive-os/examples/usage.md` | 1073 | `25d9110d163c6092a671c4903f9ffabf0901369e869de73827b839675afd1700` |
| `.agents/skills/vscode-cognitive-os/references/checklist.md` | 1416 | `64ad39a88a9e31d659e9d90e7159c254dcb6c351cef42941ddff4cb2efda904c` |
| `.agents/skills/vscode-cognitive-os/references/guidance.md` | 5637 | `bd3c8f7efe019958616e4299c1ab7577ac9fd75541826ed506188f6cc129cffc` |
| `.agents/skills/vscode-debug-profiler/SKILL.md` | 5369 | `1f1e0424a2dad40156937361a1e787cde47c4ec4c2de270ca00d6d2332bc9aad` |
| `.agents/skills/vscode-debug-profiler/examples/usage.md` | 1085 | `fbf0b981c15f215e08b82a878f4655b791dfca17bb603ba7a9cd50b9ff0dd181` |
| `.agents/skills/vscode-debug-profiler/references/checklist.md` | 1607 | `3db454d01a79734784f544ab4b81c632d7624acfb85ee346d4a194d71ef56033` |
| `.agents/skills/vscode-debug-profiler/references/guidance.md` | 11233 | `869a91e3952dcc66448b4cfc2d3b24b244360c3ba1c90b0ff668e7c0317e8852` |
| `.agents/skills/vscode-monorepo-forge/SKILL.md` | 5207 | `32b49c71231179a4f4be5d78239a15c332dd803252a4a94ec0fa73e60d67b326` |
| `.agents/skills/vscode-monorepo-forge/examples/usage.md` | 1083 | `6d4b6f2e446a68b456ad6c48110aaa52d87c6b14950ebe3414d25de45815ac08` |
| `.agents/skills/vscode-monorepo-forge/references/checklist.md` | 1555 | `cbe277364d974dd51690a27b02c95a43e36e3b6e069b3b81241e8b83dd4afc50` |
| `.agents/skills/vscode-monorepo-forge/references/guidance.md` | 13449 | `a25cf20e6d56f34d787914d26f1247c8322885296064e49f2a0062ada5639db9` |
| `.codex/instructions.md` | 655 | `f339b37e17c4504ce4b92c32f522e3beabe9105a664a823df801119354a1f862` |
| `.cursorrules` | 448 | `6790b05066eee8b7e8a062644ff721561abc9acb21ebc5257350ebaf23fe0f26` |
| `.dockerignore` | 197 | `86169a0966c4768a2160a10ede8be6e8877990268effd994503b717e76582b1b` |
| `.env.example` | 3175 | `1a6b2036e09b8a5dbc2bd6a865ea2bf6838c8063dc8121f3f531e6a5212ada9b` |
| `.github/dependabot.yml` | 627 | `29ce91a2f25d3a4134ba5888b58c0fc5f3767a88361d6e8d8e7580637b8e8444` |
| `.github/pull_request_template.md` | 564 | `36665683af24ed4dfadeab965181ad3beecdb63e864a710df0d9f9921ee371cd` |
| `.github/workflows/ci.yml` | 7045 | `6be4ecf1614d0349eda2830a41def45a96ac9fe34101a80a8232303711b70791` |
| `.github/workflows/deployment-verification.yml` | 1413 | `a59258573e523385058ff75e9a27ef8b62a22cdfba6d4d7860a41216a8c20c5d` |
| `.github/workflows/docker.yml` | 2243 | `b018ef8cf919efc57811dbb5d430b3a62a40027079486b9104232554cb61f550` |
| `.github/workflows/release.yml` | 4591 | `c41494b74efe12bd2483dc82feba2d73b9d94422ac7b4ad6e3b84affef0bcaed` |
| `.github/workflows/security.yml` | 1987 | `d14d5c37abd0a4e57afae613b5f08328ae0664810b0a521f84c5adf465203669` |
| `.gitignore` | 235 | `e81a03e65dcd97841aede647998e21a1341dcb402499048a25562099bbd47c5b` |
| `AGENTS.md` | 3394 | `1701f32bb437cedc519bd38e1058c6d75394c3f1ab99d65624d4a912de29ea40` |
| `CHANGELOG.md` | 15696 | `117a287a518db038cbe93babb4acd25c29cbffcd30f021f7c03b6d6d495a32d2` |
| `CONTRIBUTING.md` | 2218 | `58a950f83cf5f8368026561ec13d35ed35cd745bfa8d97b0de6b2993dda9b5ad` |
| `DELIVERY.md` | 2266 | `818dd3ce6b93d4387edc21988792cb09393555a3f29ab91a06bb6616a472c868` |
| `Dockerfile` | 2352 | `b27f61a40d04e8cbf35c8224516d35c2ab6be22c65dd4b1b9964c4205325dee0` |
| `FAQ.md` | 2681 | `21018ffcde812bcb1ac30f9c93bfdedafb66e87b2088bb9440040ffbe7b4dbe4` |
| `MANIFEST.in` | 868 | `7903bde41a41b5f03996f6dcfd953e0eb440f3d22de2a1ff820d3851a4d92b49` |
| `Makefile` | 3407 | `f68d5786d68a4373355a203fc00e7c8d229e76a21db52aebcdcc8bcf208d2ffe` |
| `QUICKSTART.md` | 2982 | `8bd0d17467ac9fab38fc97b9bb1dfd812963daefe3ba86a289ed225607a4ec08` |
| `README.md` | 42605 | `aac7bbc57fb550a80b130e4dbc310f5e283b87f0814db862b1202e7961c2da2f` |
| `SECURITY.md` | 1708 | `0bd9bc33a6837fbdd30aa1a3d24861c0678e44367d46aa725d39366fa86b44af` |
| `TROUBLESHOOTING.md` | 3947 | `c669c1eb5b69031c1127e4f1bd34d766a33f14b964a121f167b4f6604b0f6e6f` |
| `config/__init__.py` | 28 | `c6d125ccf2d5439ceae3ab56e834ee27bf2aa7830108226213a26a855a12be94` |
| `config/agent_registry.json` | 16530 | `6404c56e89dc39c363eaa51b2184b4e3e94f080814e5fbe36490d5be62e025b9` |
| `config/settings.py` | 20310 | `d3cb871a918acefe26908ca860110c0ca78a8b26776029e391dcdb64f146dd3a` |
| `config/stack_manifest.json` | 4158 | `be8406804cc46f0c8c53d19634b07962b0e9d3914c7071a8179844b8f7da94f8` |
| `constraints/runtime.txt` | 2179 | `2bbb21cde4f6e799b630a62cfe00b0680acbe96463ea99e71933c78c3f0dc296` |
| `deploy/kubernetes/configmap.yaml` | 771 | `9a0354af20f102f1fbe0d15be6e9ad1a9b7dabdb34885fdb820626ccb2d025cb` |
| `deploy/kubernetes/deployment.yaml` | 2694 | `3f8718823a4730690ecb82c2a022b29d904cf73509497903990e70019e1d9e26` |
| `deploy/kubernetes/hpa.yaml` | 664 | `e0bc3a70d94c8c6bcb3f16b56dcd83b7ee0f33032976a74916fd8fa9fac0db1c` |
| `deploy/kubernetes/kustomization.yaml` | 277 | `7101f1e222fec37d0b8b6121c4f16da92bdce11331ba3e6079bd934d31214191` |
| `deploy/kubernetes/namespace.yaml` | 253 | `838df4270f99c3797e93805cce618df1a9115083fe7f42de0184dbfa10d876b2` |
| `deploy/kubernetes/network-policy.yaml` | 956 | `f68c4913006accf099a19f7d6f2f97cd512a5aa87b6acf359fcc6af0d8fd9b49` |
| `deploy/kubernetes/pdb.yaml` | 228 | `b36f1f66512795952ecce08712199e78359e9ba3f8c76f640e859ae3e653105f` |
| `deploy/kubernetes/secret.example.yaml` | 510 | `7815e69cbecb3189d581dd4f029d5a00d02ca427e4dec216aa816e821e8dee5c` |
| `deploy/kubernetes/service-account.yaml` | 121 | `a9ee3e1284c80a56fc6195b921a9ecb9d9e422399e5a2003d92cecf9c73e0f7e` |
| `deploy/kubernetes/service.yaml` | 299 | `92732a9d16b2751739a80f6c4c715b329df7303edddb8940b14c21a5d2e06623` |
| `deploy/otel-collector-config.yaml` | 501 | `e16f418698f1df0b0ba3de68dc9ab678ae24dc7cef5c196d44e2d9e82326c653` |
| `docker-compose.yml` | 2785 | `3735a180913558e8208da7803652e533f74f96e7749c829b2efd3dd06a598df7` |
| `docs/API.md` | 2950 | `b9d3734bb26d70017c3a036f8d12290b7a57adfa45da7333d2e51b83df965c8e` |
| `docs/ARCHITECTURE.md` | 8817 | `118d8a8e1a86dec8620e5bc801cbc99a7318c68e285774e9ab6e8abb07e79f00` |
| `docs/DEPLOYMENT.md` | 9817 | `ca2c48c691f5fbccb28d5632cf654656391ce2eace083a3e22c6af396cdd6c97` |
| `docs/ENTERPRISE_AUDIT.md` | 12629 | `986483f076c9ab4f7ef56c0c4a8f80c7b2d72fc73f97234e8fcba40c4bb32b2b` |
| `docs/EVALS.md` | 3541 | `2ef5e3b562bae08ef1d8e02696ffdcd9dd8d52683ad90ad824b8078e829e3490` |
| `docs/FILE_INVENTORY.md` | 18564 | `0d5f2a5aefc49642aa9d2949bbaecce5375486e3c3920719df94412c11c85b9a` |
| `docs/FINAL_PRODUCTION_READINESS_REPORT.md` | 3344 | `505b970da0b3763969686dbd52b3c7920b783a7a48b645a27e9e6c6901998371` |
| `docs/GLOSSARY.md` | 1665 | `bbb9c9b8e1b94061d56aa4ee24a85c0fe9dc6152620b01326d2f2f7fe498138e` |
| `docs/NEXUS_PROMPT_CONTRACT.md` | 7096 | `a66e40391e19b0e9ce6347ba5561b07e1c1c42c0bdb7017060486555b675b182` |
| `docs/OPERATIONS.md` | 6813 | `584b2f099df6ffc48e0a0df34b5e8c6e9adfdc7740f9e6e9d61e99c934752559` |
| `docs/README.md` | 1283 | `1955b0523c54b21e1cbafe574ed76db0e634a775eabc9745e5cde9fcf83cf144` |
| `docs/RELEASE_CHECKLIST.md` | 4983 | `05d8114fc5a24104063075f175673209431933f189f0727a1f6171cb49b91120` |
| `docs/RESEARCH_BASELINE.md` | 5238 | `d5b76e6aa0606a7a4084b48ac34334bfaa351d6c28758f706fa26276f7950952` |
| `docs/SECURITY.md` | 6606 | `8821a1784f74208629107ede8b324640266819c752e2df4f5492c14b6bc193ee` |
| `docs/SETUP.md` | 9753 | `f4158875e0f6f930b52aee90b46c46fd63424d5cb90b4a5d1d0a1191d98b3693` |
| `docs/SETUP_AND_IMPLEMENTATION.md` | 9769 | `533d0a8166bdee2041c07c1240cca5323a06e59cc55dd63e2eca3b8f356dff9f` |
| `docs/SKILLS.md` | 7861 | `12854354a113d738311cd7ecbf4d59d4261061467afcef4a639430ce7dc4676d` |
| `docs/SLO.md` | 2600 | `3347a7146d6a3f567f034f311281f1e73423e903d6b0fafd3e6da38ff135aff6` |
| `docs/THREAT_MODEL.md` | 4927 | `720b4bb283d3f32ba42b2a2f779e62b2641560267131fec0e125e16bc6f4c1bb` |
| `docs/UPGRADE_REPORT.md` | 9035 | `b3a4826ce13b44a99fbe3001db5d2e212d92b0467abb60011d9654545ab2e694` |
| `docs/USER_GUIDE.md` | 3631 | `0175c917d77db11a8a3fabe5c167691ac60f623f8408c6c354e53baf07dd8e77` |
| `docs/V3_3_0_ENTERPRISE_HARDENING_REPORT.md` | 30024 | `af5d0a2d045316796d0e3dfcae8065d7e7c2276c06542e356714199317987219` |
| `docs/V3_3_1_ENTERPRISE_FINALIZATION_REPORT.md` | 15776 | `f369ac8c3fe77776e975a57b0df674d87343df0f22edf4e59bc4c24375e2a6bf` |
| `docs/V3_3_1_PRODUCTION_READINESS_REPORT.md` | 1820 | `c5664262792d9a6faf787cc5717dfbfe84a0c7ec732eff378a2a118916522abc` |
| `docs/VALIDATION_REPORT.md` | 6509 | `d60799266107136ec258fed1767b9b449c3dd49e8eb63eae05461a659991b30e` |
| `docs/migration_checklist.md` | 2824 | `11a128745a46d02b5a512f1b80985d414109f3399ae4a36daa76bf13d9210199` |
| `evals/cases/basic.yaml` | 889 | `5ff461486def0a5dd475c1a4c66ac6254f2eaf023e10cc948013a96b6b091ce2` |
| `evals/promptfoo.yaml` | 571 | `7c334cf06b185ee387228f32377b8bf843ecd4c4d74f11050d6aafcb0e5d49b1` |
| `middleware/__init__.py` | 32 | `fffe2c2837adcac82fea61988065d347967bcdc5c87cc9b801b9eb3cc74e01d5` |
| `middleware/constraint_validator.py` | 208 | `11de9f881e730538a529b0a368e9025a54ab25d8743ea18d8616efc8457c60c9` |
| `middleware/guardrails.py` | 427 | `68befc53256119b832238b0961e898e11aa09f86201f7db9ed6dc1a926052cc9` |
| `middleware/input_guardrail.py` | 2409 | `5d13cd26c4c02af4fe8da920a1a2f5a4e968aeed67f1f84d68f4b990a44de438` |
| `middleware/output_guardrail.py` | 2944 | `9fded60709a788c86169f82964a99e30591e1a2c73f75c7359bcdc9d51a9e09b` |
| `middleware/trace_block_validator.py` | 9121 | `ab95e7c43d024a7b2c721b0c3fb16e011e2f3ed3cc9a24d6493901767947f814` |
| `nexus_agents/__init__.py` | 223 | `ccb5f4648c96562a65336f7b8e1e693e5c11644dc0ea11362a1c21a67a625f41` |
| `nexus_agents/base_agent.py` | 2930 | `03a412ec4ecb9fd2e279a8d7f482f8d7476c5c582364f5575268cc9a5754a04e` |
| `nexus_agents/registry.py` | 3779 | `71d8f859a9a76cd660e11b4bb84e6bf9f6683050e10afb2f76c15044912964ba` |
| `nexus_agents/specialists.py` | 24340 | `a77a37433f08828eb381f4c02c5fc0e5ad1ec22ca4f2df362b366fbe005b6b26` |
| `observability/__init__.py` | 382 | `ceeb16505eb0a099164e5f92752171958bb078a7490e936bbe525a39a12cf70b` |
| `observability/logging.py` | 1508 | `6f7f9161aa55c49c1b984c7b66ef95e8f8b799aed9311e80581087c9770e0ce3` |
| `observability/metrics.py` | 5454 | `86bb3f87e3a021f2fedd467053305d78904039674782795ccdd67b84682d409d` |
| `observability/privacy.py` | 2371 | `514d45a648d896b4c138c291061e376b43055a08b751257a9f7f03aeb42c9884` |
| `observability/tracing.py` | 7318 | `d91e46904a9ce5e1d622174cfc0655653f639dca6b03b81565de9a6a4b9b0618` |
| `orchestrator/__init__.py` | 34 | `294d31fbc6106ff74d56097399036d50ff7b18ee1c70bb2f94fdc82e61915f41` |
| `orchestrator/conflict_resolver.py` | 4400 | `1e40dc9d1b2c39e6598f2a4c580ac253ea1051d89fccf9e8506ad557338ebe9a` |
| `orchestrator/errors.py` | 464 | `f3133421de1aa05669128b05703bf80a9fefba0f4f17bbf94234ffdba0ea7fc9` |
| `orchestrator/execution_modes.py` | 8952 | `1c10dec545c6edbb323999fcfe5d04f19e8666fdf7507b95f6cf703e6759278c` |
| `orchestrator/model_router.py` | 5749 | `69ceada7a2c062556c69be82298172a0de7873940e878150c123a074dc6e1ce9` |
| `orchestrator/nexus_agent.py` | 22783 | `d14ad0c55045a84e383523cc62295861ccd8a65849e6d49dcbf9cd7b6a744bab` |
| `orchestrator/nexus_prompt.py` | 14380 | `d5a1b4581c09d4582cc8576b254b6b35f06c953c065db5892b725e8be3eabaea` |
| `orchestrator/response_metadata.py` | 3132 | `d6dc270c0ccd030c0126a530ff5624a09e89e1350327c6b93d9aa17cff0b70a5` |
| `orchestrator/run.py` | 2346 | `c4e823aee5f23ba985a84fa82e64b8adc6eada10e994c280dd4de5cbcd03d1fe` |
| `orchestrator/runtime.py` | 4242 | `a4b049c84d726d7bac712a817c0352fa956e4c2a8fc91a02873a2dbf3c053340` |
| `orchestrator/skill_recommender.py` | 10142 | `debb0d4c1be7e30db6723b2a2ed9ed41f1fc96ed87991c70277af2165847f2a2` |
| `orchestrator/tier_classifier.py` | 6082 | `f281189d4e79f4440d98ded2a6ff974b7643e3332625a6d76bb4b821368cc000` |
| `pyproject.toml` | 2767 | `d1bd1623d92270a0bedde930188ae4c264f0c4617a4378652c97bcf71a7ea364` |
| `requirements-dev.txt` | 404 | `424d0cd4ba0970de6ee60d68014a9ff79e9104df549a4fe86db62e3bd3ea3998` |
| `requirements.txt` | 762 | `0a99a0b9225f0a026360aca2a443094e0612dd5d6914d7e7c8ad047c1a250ead` |
| `scripts/__init__.py` | 50 | `e5fe8652bc6f4fdff554f6a9bf2a968628d10a0842332bcb5ffa70c2c84dc420` |
| `scripts/bootstrap.py` | 15870 | `745306033baa8ccde48eec47d7e1ff9da182143e14171aadb04f116cac21367a` |
| `scripts/build_distribution.py` | 2932 | `e01b54c31bb6bf6e6c02cb0b136d0532671ee9d11be5304fc55eece88745698e` |
| `scripts/create_checksums.py` | 3288 | `02ebe9c3546d9a6c7e5f2e2ad54d73dd63816345d4502e1bec2a844b1e1c4d04` |
| `scripts/create_release_manifest.py` | 3477 | `f5ca0155f5ae01496192abfb8579d9534c72b84eeb923bddec74cd636df64695` |
| `scripts/generate_repository_inventory.py` | 7708 | `da5f081be206bc09045f97083ac15c2374d6fa468045702e4d74c934a5af6ee1` |
| `scripts/generate_sbom.py` | 13133 | `4d5b1c9b6c509ffe71a551864862302f93ad2b0b831ce02de0424c96a1aaeb8f` |
| `scripts/install_skills.py` | 4090 | `515961d19e7469ceabdc274190494d29139f4210edd3d759cc658a7a842245ba` |
| `scripts/quality_gate.py` | 10272 | `98bc221b657f724e6b83052ed58453ff38315468ee20cbd350e4cf46a247cda9` |
| `scripts/setup.sh` | 919 | `7f309ce306329efb125cc2bc777c6aff1d955de1ebf7263cc41c5ff12e112160` |
| `scripts/start.py` | 5898 | `0084219fe25d48116daea890f4249bb69b99c8c593d7617e4bfc65df0bd5e59b` |
| `scripts/sync_skill_pack.py` | 1870 | `a18e1cf968244c3864a87ee4b698fa47aad6b92e40f7355784218271c68729e1` |
| `scripts/test_nexus.py` | 3043 | `1c9fd8725beb5bb600b14fb099bbaeb1239957af63623bb8cc479dbac5f849ba` |
| `scripts/validate_repository.py` | 4364 | `b1702b71cc254a2d86d9820d17f6448a9cfdc5c93b8ecc0e6a3273edda705995` |
| `scripts/verify_deployment.py` | 9674 | `ad62c1fe42839740b000d16b6d87a008894d404934f49b2e9391f5ccb7232d0b` |
| `scripts/verify_distribution.py` | 11173 | `fbfdcbff409d3e6bf00b272013dd8d1f9b6049d85f3745a981dc6f3184f3f101` |
| `scripts/verify_release.py` | 10054 | `85b20082c6c9442d22e2ff990ddeb9933ffc51a9e7e0bdd90e7696c8f89ecf8b` |
| `scripts/verify_runtime_lock.py` | 8065 | `ec5a801745f8668ffb2433fc05ad2244e2ef10414ba91605d8ea1480185427de` |
| `scripts/verify_version.py` | 4478 | `c51c5aff9ef9ebc5537055f3c82123cd800d9a1411621644e9cb23475eb20c22` |
| `security/__init__.py` | 34 | `3eac13d55b447aff758fe202abd835d3b163edcfa6c2c73423715fb391c4c9d8` |
| `security/identifiers.py` | 2866 | `87b8203299742aa82a885b465be9cb1806742ef2efc62f2da2b518fd0584057e` |
| `security/policies.py` | 1658 | `7803285611f11c7f36e11f11aeb56dfea38eb95a2244cc44bdde127d79cddc3c` |
| `security/rate_limits.py` | 591 | `15fc7e3aecfec48a77587b95f8040ef9fcba6402e2b8580f64aa7979192257e6` |
| `security/sanitization.py` | 1281 | `29adbb80043c94e653d1ecb362b47bea9db3927d9e35fbc46260f15adbce21c1` |
| `security/secrets.py` | 535 | `122f8c1ce9afd32f08a768d653f0de9eb072769a4d166d220ae7fb46d2b9b995` |
| `server/__init__.py` | 40 | `0713239f276ea4c87d10a0d1f2e143c679da44c70fdd6fa3eb4e44ffd6de3ead` |
| `server/app.py` | 20107 | `a6f4bbc57699e7494284190fa7031348dbd4838160598bb5e6eb0b35a5f7b0ac` |
| `server/body_limit.py` | 3766 | `f9851743c334f722d27843c74197e46eac4aa54723052e90be7bb4bcb8cf4a6f` |
| `server/dependencies.py` | 2324 | `bd309aadf97f5ba524854acfa9451c587eed21248369377a84a0fc18d4f4696c` |
| `server/errors.py` | 4602 | `fd3f8087bc8cfc1fc28b6a7be923c3ad20bff0ec4ff975dc376b7d210249db45` |
| `server/middleware.py` | 3998 | `fd7c8317beac20550dd7297dad2d1b23beba167fb86172fca5a259a64ecb91ad` |
| `server/run.py` | 1770 | `9bd968f68508f173902442ce34cc56b9c12028aed92de33762692fd84d7f27b5` |
| `server/schemas.py` | 5748 | `f4f1813013acd07cc692fca7b754197757ac4607da68ff30663515be3981fdf2` |
| `sessions/__init__.py` | 184 | `455347e91eece5f3d8fe90e6432c9b1bb64ec3311d7b06f2fc01e36a88907432` |
| `sessions/compaction.py` | 870 | `19fc8351e78674195e2146072293dfe61764b33e88a6c5129aa391a2915d826c` |
| `sessions/intelligence.py` | 4310 | `ef800d7f280faa27a66dfc4be9804bd3584d66c623f52dac30d2b84b9e395c88` |
| `sessions/redis_session.py` | 1207 | `4401e62baa4532c627702cf0697f8ef2c58e8ebb963d13907fdcfaa9da07daf0` |
| `sessions/session_manager.py` | 18789 | `8d187fd34bff537a15b6d88a8b8cd8b45b9f06e0393adf6261a55954cd5837ad` |
| `sessions/sqlite_session.py` | 468 | `e241b8b6d4e0b11d3f6ae25544b084d6d3b2a206b446a47454c678d92c72e81f` |
| `skill_runtime/__init__.py` | 421 | `1113d01031f0f754595b177c505c6ab4de1474f315bb4f3dcfcaf92b49fe4757` |
| `skill_runtime/bundled_skills/accessibility-system-architect/SKILL.md` | 5049 | `11805714c61c11b926a582922e4cf25540a28958a3564ed1a97eb5e0a2493200` |
| `skill_runtime/bundled_skills/accessibility-system-architect/examples/usage.md` | 1131 | `569d123d9874c533c3cc754eba3f627be6ccc3e18e68a9c6ab3bedfd7c5517fa` |
| `skill_runtime/bundled_skills/accessibility-system-architect/references/checklist.md` | 1577 | `933e45ec35325456e20b85716406c8172acf474e6c8de272a9a31319fa76a390` |
| `skill_runtime/bundled_skills/accessibility-system-architect/references/guidance.md` | 13780 | `f34abdea4b5dd71457afb033d391b9abdc82f5e171cfa7dff052702a4af84546` |
| `skill_runtime/bundled_skills/agent-prompt-upgrade/SKILL.md` | 5311 | `377f8d66937020ba18c960117ba40b999dc2b75ab08f61f31a61823fa355e865` |
| `skill_runtime/bundled_skills/agent-prompt-upgrade/examples/usage.md` | 1109 | `cf08d972a1c1f8e904e6a4cd0330a41e359e6c095c21ee9ccc640818b5b1c885` |
| `skill_runtime/bundled_skills/agent-prompt-upgrade/references/checklist.md` | 1550 | `245221cd6cf15d3ba716de8f269baf877b3fd7e7970af24d81184c73eb2f25cb` |
| `skill_runtime/bundled_skills/agent-prompt-upgrade/references/guidance.md` | 5667 | `15720d517c6e8d6d5e3553f3ec8a732d6d5c1fe4d4773990b279f53d372149dc` |
| `skill_runtime/bundled_skills/ai-feature-architect/SKILL.md` | 5233 | `28025813c0278c697321dfb6c94e91b2511e2649b3b4c7efaac7001c9ad009d8` |
| `skill_runtime/bundled_skills/ai-feature-architect/examples/usage.md` | 1081 | `26c4cd25edbb1255b4a273097fdceea7fee457e2648cd6b291c9f98ffe03e38e` |
| `skill_runtime/bundled_skills/ai-feature-architect/references/checklist.md` | 1558 | `ea92c766cb42473f4902e08ede89b06995559a42910dd3d7a12617e174f39c45` |
| `skill_runtime/bundled_skills/ai-feature-architect/references/guidance.md` | 11348 | `dc0059b166e9c463686f5cf358f18c4a43695710fef52b8479daee74150b49e7` |
| `skill_runtime/bundled_skills/api-automation-architect/SKILL.md` | 5282 | `31692d5322ef702d531ae28d8150484d886a2df994ac4841ab9538ba0e17bc3f` |
| `skill_runtime/bundled_skills/api-automation-architect/examples/usage.md` | 1101 | `465c502ce1d62d95cdfa9b37a39a6f3a0b5ef8ad1b131d2997ec42a4bdb52eae` |
| `skill_runtime/bundled_skills/api-automation-architect/references/checklist.md` | 1643 | `7dea48905d36b06ae05ccf72a42ae815e22e76569b5c25c30c12450585bcaf8d` |
| `skill_runtime/bundled_skills/api-automation-architect/references/guidance.md` | 6184 | `5620f75e4315b381f0706aa6fb57742f8046df2fdb99ee31d57ce341b1af8c30` |
| `skill_runtime/bundled_skills/api-contract-governance-architect/SKILL.md` | 3873 | `f3e6f50e040310e998be199a3cc4ded3d31deef62db830631be323e9ef980d6f` |
| `skill_runtime/bundled_skills/api-contract-governance-architect/assets/openapi-governance-policy.yaml` | 831 | `465478125086d123f5664d32ffe795d02f5431483677b154d4162fc1181ff340` |
| `skill_runtime/bundled_skills/api-contract-governance-architect/examples/usage.md` | 3548 | `324dfb58d3e25372bf3f94f6f1a87722ae532c63dd3f8f484c7e4e37214165c7` |
| `skill_runtime/bundled_skills/api-contract-governance-architect/references/checklist.md` | 2742 | `bb9cd411934894eb57fc879c4e0e03bdf4ebc2e9b5b189823f0ffd0cb0cd347c` |
| `skill_runtime/bundled_skills/api-contract-governance-architect/references/guidance.md` | 21883 | `da820d10463c24cd9568546bab1d0be11e74fa54f5a6526808949a7e0476338c` |
| `skill_runtime/bundled_skills/api-contract-governance-architect/references/playbooks.md` | 2331 | `589688fff1b898e1989c0c68dd6ef01fdd1182cbd71426ab53c40734981a515d` |
| `skill_runtime/bundled_skills/api-contract-governance-architect/scripts/validate_contract_policy.py` | 3804 | `d4aa4477d2831b8680eef09ff2b913f6ede66a9b8aec58ae70e20a17bd8b165d` |
| `skill_runtime/bundled_skills/backend-domain-model-architect/SKILL.md` | 5222 | `73099ad0cd3ae7ce46136fb907326625dbb6538794360cf7d0bec160858eefc7` |
| `skill_runtime/bundled_skills/backend-domain-model-architect/examples/usage.md` | 1131 | `b3ea61acf7a1e5b2ffa53b4e44cc0a875155347f21b8ecd423ea8489f97d0893` |
| `skill_runtime/bundled_skills/backend-domain-model-architect/references/checklist.md` | 1622 | `9b32ea690c27e0f763919f0e16993b0221ed4277a82875e5ce7303435645a1a6` |
| `skill_runtime/bundled_skills/backend-domain-model-architect/references/guidance.md` | 10782 | `cee7445f8dc9082865b1766e1a871f69f2cd56c4268d94d82d9e25e74a956bea` |
| `skill_runtime/bundled_skills/backend-systems-auditor/SKILL.md` | 5487 | `627cc826b19d22f47213f4f029a2ebd16507caf18e35d71ee7fc96de6d77c6ce` |
| `skill_runtime/bundled_skills/backend-systems-auditor/examples/usage.md` | 1096 | `a534dac803bed3be176ee2c81ebc9ef3a11588ddf4dec181340caf6846a9f9f1` |
| `skill_runtime/bundled_skills/backend-systems-auditor/references/checklist.md` | 1780 | `d49643d8170c12649f08c217be81c849d7f7a08cb8766989432d009ff9daa9d1` |
| `skill_runtime/bundled_skills/backend-systems-auditor/references/guidance.md` | 7310 | `0dee0e3cb7afac46aaef28825515a3b0e7733d48b64d59dbd5919b9b52e4e05e` |
| `skill_runtime/bundled_skills/bullmq-job-architect/SKILL.md` | 5320 | `db4ef9431eb3c630c9ee250dffb82a8c66b08bc6f433ae4fcba81edad15ae429` |
| `skill_runtime/bundled_skills/bullmq-job-architect/examples/usage.md` | 1081 | `37ae2d8f153ab2d6a101892e72bce362d2590bdbeb12a0a219ac24d5c932db02` |
| `skill_runtime/bundled_skills/bullmq-job-architect/references/checklist.md` | 1666 | `9e6a2d8777c76ceb24fea625c4a7f3826d9c664c4a3b21ae3510b1057d3303ca` |
| `skill_runtime/bundled_skills/bullmq-job-architect/references/guidance.md` | 11588 | `07c6b5d88f3434bb08389c57d54e95b362de9ca74cc13e70351088ca5c31e0be` |
| `skill_runtime/bundled_skills/codebase-zip-audit/SKILL.md` | 5040 | `e83774b2e63204e5a704437ea04b1b86d116119cb1701a044f6d5cc3f713b790` |
| `skill_runtime/bundled_skills/codebase-zip-audit/examples/usage.md` | 1084 | `568b3229fd20b07afc6caac9cabca859ec5f5c99dcd083057f347792fc16b31a` |
| `skill_runtime/bundled_skills/codebase-zip-audit/references/checklist.md` | 1630 | `795216e8c1fb51cdc5dea41184e00c63b60f4ae4e9a3dc74ce03da049a6ecbb5` |
| `skill_runtime/bundled_skills/codebase-zip-audit/references/guidance.md` | 5744 | `6d8fbc9460d9cb534963809f4a6f3cf39a45fd045c2d1de154d3fae3f92e52c9` |
| `skill_runtime/bundled_skills/component-quality-gate/SKILL.md` | 5295 | `c81bd47af354629fc3e4cd564b215a78342dbdba19230f01afa0f0060d024771` |
| `skill_runtime/bundled_skills/component-quality-gate/examples/usage.md` | 1091 | `13255749fbcb0e80756759f9697db01468d29b509a19c9af0f6847af198208aa` |
| `skill_runtime/bundled_skills/component-quality-gate/references/checklist.md` | 1659 | `6eb44006cdd9994e1ffc2494cb8239d8572b9cd0b62ab3fe8d589f6ae32ead35` |
| `skill_runtime/bundled_skills/component-quality-gate/references/guidance.md` | 9250 | `99822e744f7bfc8444a72c06fd733a631d8cb13c35b8b038a2ad6954c138245c` |
| `skill_runtime/bundled_skills/data-visualization-architect/SKILL.md` | 5575 | `8bdab5d7d612554d4856c254b71d2347a2599326ecc67eb7beb989efcc20c51c` |
| `skill_runtime/bundled_skills/data-visualization-architect/examples/usage.md` | 1121 | `be73ec02ed23a29152fdbd061e8dfee8793b3cc900ed00ae9c3c4e8f8511d7d9` |
| `skill_runtime/bundled_skills/data-visualization-architect/references/checklist.md` | 1532 | `98e8a962b31714843336bd6f8f354e3fcc93b339d5006d7b3ec31cdd6189e609` |
| `skill_runtime/bundled_skills/data-visualization-architect/references/guidance.md` | 14252 | `d8cae66ab8690a390ae72117c9a8017ccc8d1655084a8bc946dd242f03eded61` |
| `skill_runtime/bundled_skills/design-token-system-architect/SKILL.md` | 5294 | `227b807856b5d324ea98b70a80ec55eaeded42115d663733ec0847ebba0caeda` |
| `skill_runtime/bundled_skills/design-token-system-architect/examples/usage.md` | 1126 | `3c4f4a4c4356bfe62d238b3902df703e996d2944d13a19eeb9a02c7d3dad0fca` |
| `skill_runtime/bundled_skills/design-token-system-architect/references/checklist.md` | 1596 | `8e0e83f1e528518567be1af52d37f214042ddfce8a605572ecdd5744b40e315b` |
| `skill_runtime/bundled_skills/design-token-system-architect/references/guidance.md` | 15378 | `0964cee228ed4f4910c92d42058b458ea8119afeaaf6b421ae9a53af4cde682a` |
| `skill_runtime/bundled_skills/edge-cache-architecture-architect/SKILL.md` | 3772 | `91ef88b6ba790e3d7dfe18591a5a153434939c9c6f8726ebe4691cedd4a87c29` |
| `skill_runtime/bundled_skills/edge-cache-architecture-architect/assets/cache-policy.yaml` | 1098 | `6a1abff1de2470857a8499e12bac585d6b0d7f83ef12404ff9650206c62cb5a2` |
| `skill_runtime/bundled_skills/edge-cache-architecture-architect/examples/usage.md` | 3576 | `6c5c8ee76fae2af2fca6063958697d62d244d61fa84c2e3f0371844a2a7aa1be` |
| `skill_runtime/bundled_skills/edge-cache-architecture-architect/references/checklist.md` | 3124 | `d7b185d22cc0efbb7d256f35019a46b1e58381fa938ea15ffd2a46794e2593b2` |
| `skill_runtime/bundled_skills/edge-cache-architecture-architect/references/guidance.md` | 17826 | `7cf29a5d60cdb13d3fe300cad22d3f8d3dfb394099914c7f2bb9175b1cae92d3` |
| `skill_runtime/bundled_skills/edge-cache-architecture-architect/references/playbooks.md` | 1994 | `3b32a59155f80e51c5e08c0a1fd7b1f39173ca9f62a50dbee7cb027b13fa7b22` |
| `skill_runtime/bundled_skills/edge-cache-architecture-architect/scripts/validate_cache_policy.py` | 4114 | `b13108ea555460600386df1ba13abc11d75a6e009f4f2e4e8d0cbb5dcc41a022` |
| `skill_runtime/bundled_skills/effect-ts-layer-architect/SKILL.md` | 5263 | `63ea1b1220aafa59b4f008660623357e8811855f0a67b3d044b1c86a4206dd2d` |
| `skill_runtime/bundled_skills/effect-ts-layer-architect/examples/usage.md` | 1106 | `ce06b60ffd992922347cb84b3ae5f32885d3d1fe2236287cf3e6c9ba71bfa07e` |
| `skill_runtime/bundled_skills/effect-ts-layer-architect/references/checklist.md` | 1616 | `3acaf4f248f2465fb28442f0aef66c245c987b859cec7222590683bc22da2319` |
| `skill_runtime/bundled_skills/effect-ts-layer-architect/references/guidance.md` | 5619 | `23568ed28f38bbed931628a3f8548c3284f0fcb9ab7dd42885c1117191fb9f25` |
| `skill_runtime/bundled_skills/elite-skill-forge/SKILL.md` | 5048 | `a5282f8146606b1bf68096a688b177323c7d0b3f2b6e588adeb46be63567061e` |
| `skill_runtime/bundled_skills/elite-skill-forge/examples/usage.md` | 1066 | `21182b5ff83df8a974a96e5176fd082929e09280432648b16fbc9be5137aa056` |
| `skill_runtime/bundled_skills/elite-skill-forge/references/checklist.md` | 1679 | `f5fd9415c578160d47ddb682d6a5765fce107579f5cb8ad82e108ee746570cb2` |
| `skill_runtime/bundled_skills/elite-skill-forge/references/guidance.md` | 9186 | `8a92402cd7e41b8669776cd5d13467ec457666c5e2c4163add2868049d972967` |
| `skill_runtime/bundled_skills/frontend-design-auditor/SKILL.md` | 5362 | `c4506074aec44eed01e56392ce70835bcab001d5e2b1ef350477861994cb6b3b` |
| `skill_runtime/bundled_skills/frontend-design-auditor/examples/usage.md` | 1096 | `41b6bc061781e35c8bbbc96dcc93d7ee276111b0918ef3f56a7ce8e839459bd8` |
| `skill_runtime/bundled_skills/frontend-design-auditor/references/checklist.md` | 1754 | `4157369d764f4f532ff405a5e5c80a7570db4aff6284856539482f07507b1862` |
| `skill_runtime/bundled_skills/frontend-design-auditor/references/guidance.md` | 6234 | `0f545a6c0d38c9865c627eab0bf0a1208bccae7708f5c257b0b18946201c2d08` |
| `skill_runtime/bundled_skills/frontend-product-design-architect/SKILL.md` | 5282 | `04873a9c936143157c284a8e966f89d4453ce80e9e908bf30094f61bbf84d551` |
| `skill_runtime/bundled_skills/frontend-product-design-architect/examples/usage.md` | 1146 | `f4676731a79a4ac22220a8a8bc8d0fcf57cf853ac5c39b7b5ef63853a59ba07d` |
| `skill_runtime/bundled_skills/frontend-product-design-architect/references/checklist.md` | 1704 | `ed180624c1db19c917e7eb215d2cd33d42c150d77caa3df79c30bfe5db12c064` |
| `skill_runtime/bundled_skills/frontend-product-design-architect/references/guidance.md` | 9974 | `5663e132bec6add9caa8590cc8f953536953c1434ef0b130ca0e798326510a34` |
| `skill_runtime/bundled_skills/git-workflow-architect/SKILL.md` | 5335 | `75cd42e418d3ad042988f0423ed092614830cc64281ec89bd50c48e58306f882` |
| `skill_runtime/bundled_skills/git-workflow-architect/examples/usage.md` | 1087 | `39c989d7e2a7216d9b1436d33dcdb5032e8a860df934c7d144188d755aa09302` |
| `skill_runtime/bundled_skills/git-workflow-architect/references/checklist.md` | 1587 | `211ed505492a1b6a9d093b73859d735da912af35605b4359b0f31e581716c827` |
| `skill_runtime/bundled_skills/git-workflow-architect/references/guidance.md` | 12576 | `f91d88b7c8a8d6e4ea0fd48262cd308146760a65734b87889d32ab1c8031432e` |
| `skill_runtime/bundled_skills/motion-interaction-architect/SKILL.md` | 5407 | `630dcb538f780e02223430c88d5593441b07cd3553ee4dd49e69020ea953ede6` |
| `skill_runtime/bundled_skills/motion-interaction-architect/examples/usage.md` | 1123 | `72ad4a559e83a0a8f7c272d934c53ae9c7b1768143f2fc69103a02d4d76a79fb` |
| `skill_runtime/bundled_skills/motion-interaction-architect/references/checklist.md` | 1535 | `531bd5c2b05765e4defef9d9ac1ed6749c3c059a3d690ca92a8a451da22cd7ab` |
| `skill_runtime/bundled_skills/motion-interaction-architect/references/guidance.md` | 10760 | `9ec66b6dbd9a359cf83bf50d9ae47f2bfc4885f7da148a1da11926df1f7f8eaa` |
| `skill_runtime/bundled_skills/motion-performance-architect/SKILL.md` | 5157 | `f8e8e2759f939fe2ff3facff5029c818ab15cc25d5f543c575d819986586721b` |
| `skill_runtime/bundled_skills/motion-performance-architect/examples/usage.md` | 1121 | `fe59b1976cd0eaf3733dabb268bdc0cde00fc24df1f8be563e055f3479fd517a` |
| `skill_runtime/bundled_skills/motion-performance-architect/references/checklist.md` | 1804 | `c9fe6a2452c75411ffe3d6c5411d183555a04ee398913646c643f6973c18eb3d` |
| `skill_runtime/bundled_skills/motion-performance-architect/references/guidance.md` | 8906 | `d8ed9a5d28a0964dff1e427957176a89deabdc9819ba40a4876cb35f1c13ffc9` |
| `skill_runtime/bundled_skills/multi-agent-orchestration-architect/SKILL.md` | 5316 | `d0180dd4db68c4e5c78e6ecfbc959269152d5676fbf4930dc1b3d1584094a2d0` |
| `skill_runtime/bundled_skills/multi-agent-orchestration-architect/examples/usage.md` | 1156 | `9e3dad77ec4e6cabf7ecdda6bc361b1b368ac6dbe7fdb099843991e33c07cfea` |
| `skill_runtime/bundled_skills/multi-agent-orchestration-architect/references/checklist.md` | 1561 | `434355deb587684d507c34cd7e61258a6d069d089bc1c68c338e2d798cf17f52` |
| `skill_runtime/bundled_skills/multi-agent-orchestration-architect/references/guidance.md` | 13288 | `e3cbd00441e50c47dd927c00466c763d75bef0f32705c643bdea54030d4d985b` |
| `skill_runtime/bundled_skills/nextjs-performance-architect/SKILL.md` | 5264 | `a16b48c12ad6749730f9a17d9d605c1cf915b480aefdc91151992ec3be4ce893` |
| `skill_runtime/bundled_skills/nextjs-performance-architect/examples/usage.md` | 1122 | `fafdd016dd92fcdbadad16543effbbaf59e5709053f0db8ab53edc6daef9b93f` |
| `skill_runtime/bundled_skills/nextjs-performance-architect/references/checklist.md` | 1562 | `bdd2bc845c0c106528f8938e6f3149769cf2bb5d83d108839c4bbcc5c991d959` |
| `skill_runtime/bundled_skills/nextjs-performance-architect/references/guidance.md` | 10525 | `641f54c042dd3bd40266883d57eac243b03fcc73bd7f85924fb6ac49e53349a3` |
| `skill_runtime/bundled_skills/nigerian-fintech-compliance-architect/SKILL.md` | 5650 | `8207ecfa6ece7c3e5ef8c6a564d41128c1bded53eb2cc1c7d4d025a7cdbf4095` |
| `skill_runtime/bundled_skills/nigerian-fintech-compliance-architect/examples/usage.md` | 1166 | `5eb8cefca93549373a3e9382715b19ee6232ebfd5eb53aa35199a113cda5724a` |
| `skill_runtime/bundled_skills/nigerian-fintech-compliance-architect/references/checklist.md` | 1668 | `fcc1ac865519dd9aeacf2b0c31727fa176a9cdd76af9e35cd252f305b41cf5f8` |
| `skill_runtime/bundled_skills/nigerian-fintech-compliance-architect/references/guidance.md` | 12825 | `40a0980c8813c5122c6532fcc17f0b759c9e1470e05a75101e8df66301f3ac55` |
| `skill_runtime/bundled_skills/opentelemetry-observability-architect/SKILL.md` | 5502 | `787bf96a1cebac1b5db488dede76f809cfa77f8dca6136fe287617594d20e6f6` |
| `skill_runtime/bundled_skills/opentelemetry-observability-architect/examples/usage.md` | 1166 | `310bd30a1a9aa34a461bf013800fb4815ea45ec354688836e9819ba9d4dbf50d` |
| `skill_runtime/bundled_skills/opentelemetry-observability-architect/references/checklist.md` | 1593 | `df4f2d348bc836f34841e327ad00a6814c181f9b74af596af59658dd83189862` |
| `skill_runtime/bundled_skills/opentelemetry-observability-architect/references/guidance.md` | 12105 | `cac71ffbe722a32dbd1c131c78924630a2d15d1b2c581bfb379e46a574bf8881` |
| `skill_runtime/bundled_skills/portfolio-conviction-engine/SKILL.md` | 5462 | `0d67c9d1c5d25dc2a2de3fdfad0b9847f9bddf472b64f1bc3447471ba5354fb3` |
| `skill_runtime/bundled_skills/portfolio-conviction-engine/examples/usage.md` | 1122 | `dd328bc6710c26002b77feedf69ce4b2bde6f63129e8c59997d3badc02b6d481` |
| `skill_runtime/bundled_skills/portfolio-conviction-engine/references/checklist.md` | 1607 | `cf5aaed2b8adcdffe1d3ccd373f48d62cf435f29183d8c8f586a44c3e659dea8` |
| `skill_runtime/bundled_skills/portfolio-conviction-engine/references/guidance.md` | 7067 | `16babeeb29347d74c45ea21972716745c2de319a346185a1e9f262c12733e338` |
| `skill_runtime/bundled_skills/prisma-database-architect/SKILL.md` | 5169 | `e96405d641826e8288dbbc24f937a601202de4fa2b1c14bbd8824bf5c296293d` |
| `skill_runtime/bundled_skills/prisma-database-architect/examples/usage.md` | 1106 | `db636ffd23c8d18ab19c6e4fc5d0db192b0719afab79d39c4ae7df8552c2bff8` |
| `skill_runtime/bundled_skills/prisma-database-architect/references/checklist.md` | 1545 | `77d03d22d87993cf05a1528c0b0bbe40bea245a7b4eff41cfe0cee6e4dbdac63` |
| `skill_runtime/bundled_skills/prisma-database-architect/references/guidance.md` | 11238 | `60d3eb9b51bea665a4427c6105dc3a74b8d44cd3e0ecfb99d3f6010d858d5943` |
| `skill_runtime/bundled_skills/prompt-engineering-architect/SKILL.md` | 5405 | `a4b8fb59e7c4df8a4ffe70bca5358a9ed3d1ce4e3b1938cc025ae4815552c7f7` |
| `skill_runtime/bundled_skills/prompt-engineering-architect/examples/usage.md` | 1121 | `5dbdd5261cf59d1c63cbdbdbf39f0b7abfb532688a5c67d3d757d6989c676e44` |
| `skill_runtime/bundled_skills/prompt-engineering-architect/references/checklist.md` | 1637 | `3832ba4abbeb8b884eb1f31290dc095228ab466458e040ad7026c53742cd743a` |
| `skill_runtime/bundled_skills/prompt-engineering-architect/references/guidance.md` | 10938 | `b4c850d9fc622accc308ac3b9749b9cca9cebff430b95fc7348e00c20ad1d3cf` |
| `skill_runtime/bundled_skills/react-native-expo-architect/SKILL.md` | 5374 | `057717c312b09f30a9715f2867177116e295db8b6d9ca85ff27b420f375cf7fe` |
| `skill_runtime/bundled_skills/react-native-expo-architect/examples/usage.md` | 1116 | `e5cbd114e74a309201b570352dcaa017b1201ddd2f8880291ec4e58821a5d87e` |
| `skill_runtime/bundled_skills/react-native-expo-architect/references/checklist.md` | 1508 | `b96e62003693dec6d644c882895ea97d574cd0a9901607efc9159cb75dd6e92e` |
| `skill_runtime/bundled_skills/react-native-expo-architect/references/guidance.md` | 9886 | `e651e86cde5ddddc9c9e51371d2c0ff87432607c10999e73024735167be30b38` |
| `skill_runtime/bundled_skills/real-time-systems-architect/SKILL.md` | 5407 | `9dac159c3630022ca4dfe3f38d4323493e79be8a7793a2e31965b858c8028515` |
| `skill_runtime/bundled_skills/real-time-systems-architect/examples/usage.md` | 1116 | `4340efc73aae9abb4fb662c72a3491910eef76509799056c0e0ccf1f466a5abd` |
| `skill_runtime/bundled_skills/real-time-systems-architect/references/checklist.md` | 1588 | `5b3227f1c0864ce2a5ad1cfb7fab33dad02beac534e028f26dd9d13e9432fed8` |
| `skill_runtime/bundled_skills/real-time-systems-architect/references/guidance.md` | 14090 | `f9315bda178fbddfd5df4fd5b5a792f4f6b7ac26b653600cee4617bd7419198b` |
| `skill_runtime/bundled_skills/release-incident-operations-architect/SKILL.md` | 3588 | `ba9ba410f1d52027b578534879ea852930043cf81364cceda42c15c33901084b` |
| `skill_runtime/bundled_skills/release-incident-operations-architect/assets/incident-command-template.md` | 952 | `f474e3e735237352581885b3492e9aa8846bca7a2d478ce61926d22ea5d06322` |
| `skill_runtime/bundled_skills/release-incident-operations-architect/assets/release-verification-policy.yaml` | 1084 | `6b5834e9c9159ff78ea4e4fd6c747de76de90a2c0593e5ce763081a747f090b6` |
| `skill_runtime/bundled_skills/release-incident-operations-architect/examples/usage.md` | 3823 | `d0ef620b47598eb24e5b1bdd66f44879305ced242e4bc2dd46d036844b2aaebf` |
| `skill_runtime/bundled_skills/release-incident-operations-architect/references/checklist.md` | 3092 | `5ba20c077bef96b5e5e10ac865579b36236cf4fb872506a0467c8c18ab7c8e9f` |
| `skill_runtime/bundled_skills/release-incident-operations-architect/references/guidance.md` | 19757 | `3f790e049951753d8882084648da7f0b8e2b8dc321c0fdb71f2007c7485234fb` |
| `skill_runtime/bundled_skills/release-incident-operations-architect/references/playbooks.md` | 2244 | `68abe231ceea4602685b4d56ded9d71e05d1df590ba665d8eab82df858edfbe8` |
| `skill_runtime/bundled_skills/release-incident-operations-architect/scripts/validate_release_policy.py` | 4533 | `26b8b96923704b3908e3ecbacb0f9c961224f9d57e03d3b7551012591c633955` |
| `skill_runtime/bundled_skills/security-hardening-auditor/SKILL.md` | 5581 | `d5a460cdfb594e6ebeab4e400433da31050e3d6fba1cb5315d9520b81534ae4d` |
| `skill_runtime/bundled_skills/security-hardening-auditor/examples/usage.md` | 1111 | `efcb9200790afd75ef57908626aba2653ea167b4a5653bd5b88835a1876ac5a7` |
| `skill_runtime/bundled_skills/security-hardening-auditor/references/checklist.md` | 1802 | `4b25050f3ca25a61203e88e60927de7de72953949c4686df4646c6c2ceffd569` |
| `skill_runtime/bundled_skills/security-hardening-auditor/references/guidance.md` | 12109 | `0d99a806c613699d572b6cdeca2aad08d5511b0d0aa668e6d5c36f4107aaae66` |
| `skill_runtime/bundled_skills/shell-cognitive-os/SKILL.md` | 5188 | `9008c8cd4fa93fba7ddf1f0503f0b5fd24d0feaf1dea8cc73c21090e1452622b` |
| `skill_runtime/bundled_skills/shell-cognitive-os/examples/usage.md` | 1086 | `6f25539f275e28d566c0e3e974aa3663d2982286a40ca4f6f7df91472087ebb1` |
| `skill_runtime/bundled_skills/shell-cognitive-os/references/checklist.md` | 1516 | `2e76381198fbf7f9842c096674dab46a838c9b20d196525a11a2b28683174cd3` |
| `skill_runtime/bundled_skills/shell-cognitive-os/references/guidance.md` | 5926 | `b83b50351a1a4016e9f89df6cd45ab0ee9429a1d4903ae441ff71ae484564324` |
| `skill_runtime/bundled_skills/surgical-merge/SKILL.md` | 5177 | `f475ef27c3626149f527ab68a5ed675719fc4f746f45754bb43d858eefbb2e24` |
| `skill_runtime/bundled_skills/surgical-merge/examples/usage.md` | 1061 | `5f3b34d1f7120ac89e2873de7deffdc257c0e7c358a9c5063db6a5a16c0194b5` |
| `skill_runtime/bundled_skills/surgical-merge/references/checklist.md` | 1542 | `0223fe875406244c061a31d4f89bbbed76df64210058529c083b6e9957208fee` |
| `skill_runtime/bundled_skills/surgical-merge/references/guidance.md` | 4631 | `96fccc64898f43550c24c48f5bd8ea712e62e7819b6e27c7c203a125d8b23b32` |
| `skill_runtime/bundled_skills/testing-strategy-architect/SKILL.md` | 5345 | `73fee5e5c3e5a14e2c8e0fb035c83c7a01c8d222283b4057141307b29601acf6` |
| `skill_runtime/bundled_skills/testing-strategy-architect/examples/usage.md` | 1111 | `f299b10454dc4b3142fbc4ec5869ecb1ab8222b8b384fe93cf5c743a7aca344c` |
| `skill_runtime/bundled_skills/testing-strategy-architect/references/checklist.md` | 1571 | `5cbb49d2c50440d45071b23aa725bf828012279048291a19442d295ba3c316d1` |
| `skill_runtime/bundled_skills/testing-strategy-architect/references/guidance.md` | 12515 | `54548a16774f5584e888531c26b0a9a8456afae5a65c09953b707eb3ffa1f496` |
| `skill_runtime/bundled_skills/typescript-config-surgeon/SKILL.md` | 5482 | `c030b0c8d9eff8aa2c3fed3fcd2fac97939aaaca60006d20099b41bf07d3369e` |
| `skill_runtime/bundled_skills/typescript-config-surgeon/examples/usage.md` | 1106 | `64b23deb75fe4814f025a4f1e7ce3c3d2e10b97bb1670f77f2c4fc3db867ef47` |
| `skill_runtime/bundled_skills/typescript-config-surgeon/references/checklist.md` | 1519 | `1adf06fed670ce51a3b990deb298c110c4a39281455d18d55338c0f2b69bf9a4` |
| `skill_runtime/bundled_skills/typescript-config-surgeon/references/guidance.md` | 13492 | `6ba1491984e44ffe88643942a5285b9f35a240cc10429a2a5bb6f863fa9d5a4a` |
| `skill_runtime/bundled_skills/vscode-ai-agent-stack/SKILL.md` | 5319 | `cc88360b5e4fd20f5e4fefd1c938d56629ebaf09f7736ca441e6e259f8efdf94` |
| `skill_runtime/bundled_skills/vscode-ai-agent-stack/examples/usage.md` | 1087 | `db1d9bff6f31740674ee678712dc9bad1bd20f01cf093a2193d445529f163661` |
| `skill_runtime/bundled_skills/vscode-ai-agent-stack/references/checklist.md` | 1777 | `a4301e9484cf13e743bda881a8846e238e3b14fe6a0fa005e352667a8f58d644` |
| `skill_runtime/bundled_skills/vscode-ai-agent-stack/references/guidance.md` | 9514 | `aac84a93717fa1863385652a91b727f340019cb5e6f3d6b2d4b4f3e59fe161d5` |
| `skill_runtime/bundled_skills/vscode-cognitive-os/SKILL.md` | 5125 | `1a61696556764a01f9888bb298f5dc00e0d95ff41a55935dca157d4db62a1749` |
| `skill_runtime/bundled_skills/vscode-cognitive-os/examples/usage.md` | 1073 | `25d9110d163c6092a671c4903f9ffabf0901369e869de73827b839675afd1700` |
| `skill_runtime/bundled_skills/vscode-cognitive-os/references/checklist.md` | 1416 | `64ad39a88a9e31d659e9d90e7159c254dcb6c351cef42941ddff4cb2efda904c` |
| `skill_runtime/bundled_skills/vscode-cognitive-os/references/guidance.md` | 5637 | `bd3c8f7efe019958616e4299c1ab7577ac9fd75541826ed506188f6cc129cffc` |
| `skill_runtime/bundled_skills/vscode-debug-profiler/SKILL.md` | 5369 | `1f1e0424a2dad40156937361a1e787cde47c4ec4c2de270ca00d6d2332bc9aad` |
| `skill_runtime/bundled_skills/vscode-debug-profiler/examples/usage.md` | 1085 | `fbf0b981c15f215e08b82a878f4655b791dfca17bb603ba7a9cd50b9ff0dd181` |
| `skill_runtime/bundled_skills/vscode-debug-profiler/references/checklist.md` | 1607 | `3db454d01a79734784f544ab4b81c632d7624acfb85ee346d4a194d71ef56033` |
| `skill_runtime/bundled_skills/vscode-debug-profiler/references/guidance.md` | 11233 | `869a91e3952dcc66448b4cfc2d3b24b244360c3ba1c90b0ff668e7c0317e8852` |
| `skill_runtime/bundled_skills/vscode-monorepo-forge/SKILL.md` | 5207 | `32b49c71231179a4f4be5d78239a15c332dd803252a4a94ec0fa73e60d67b326` |
| `skill_runtime/bundled_skills/vscode-monorepo-forge/examples/usage.md` | 1083 | `6d4b6f2e446a68b456ad6c48110aaa52d87c6b14950ebe3414d25de45815ac08` |
| `skill_runtime/bundled_skills/vscode-monorepo-forge/references/checklist.md` | 1555 | `cbe277364d974dd51690a27b02c95a43e36e3b6e069b3b81241e8b83dd4afc50` |
| `skill_runtime/bundled_skills/vscode-monorepo-forge/references/guidance.md` | 13449 | `a25cf20e6d56f34d787914d26f1247c8322885296064e49f2a0062ada5639db9` |
| `skill_runtime/catalog.py` | 1358 | `7531aee03f8e5e90fc2713fafc558e9706b74970361cb70df3d1f457f5ce22c4` |
| `skill_runtime/cli.py` | 6871 | `4a805990fef0698db8af28e23acd544c2a4987cf52ba81bfddca3165c0354cf6` |
| `skill_runtime/loader.py` | 17416 | `a5f526b616842bb8215cf368b670f971c1b3885db767503107955755f327492d` |
| `skill_runtime/models.py` | 1980 | `3ce50991703845433a248ba28d8727c101671a27113728760afea4bfdb4ad940` |
| `skill_runtime/security.py` | 5199 | `15425ac7169bac3b85b65ea23144aebaca62ea2056996aed907d914192542941` |
| `skill_runtime/tools.py` | 4247 | `993e76c6cc463dce24541a9b62aff92306e3b079d991c2951e4b11f232285ef8` |
| `skills/catalog.yaml` | 27346 | `8b74fa1b44d0f2144fe2d6e25702e2951fa228096e3e01cea06b3d8dc4dd063c` |
| `tests/conftest.py` | 1707 | `8c52cf05bb958dddc7d238b24fb009d17292f5e95c4fcf337405e554653d64eb` |
| `tests/test_bootstrap.py` | 6129 | `4f4ddd6519a0666d464c5d11afe22a3bd9c0d723dd348313381b495ee450254e` |
| `tests/test_cli.py` | 1686 | `f1da791f36df14a6f8794d0b5fa799d916509a9c353bdce597b042b5d9583663` |
| `tests/test_deployment_verification.py` | 748 | `70520cf62947a441a5269527ed0e70a8b3842796dc26a48f5f2a565172594e28` |
| `tests/test_docs_beginner.py` | 2592 | `fcff256547b7e857783b28acbc1c67a72d27de571980f2c5ae413d1f51f4066b` |
| `tests/test_guardrails.py` | 2266 | `56bcb58942e653b60975724e7b7f763f4b335a647b503e72528c375260edcb57` |
| `tests/test_health.py` | 508 | `1fc8fa6288f8da62ed62f6f9877830e32ee2556e2ee84b43c3820ffa3e12a395` |
| `tests/test_intelligence_upgrades.py` | 12859 | `3eebed64c331e457243b3c4511ea5ae19a1c6d2aed675b3b71aa96eb69f8d845` |
| `tests/test_model_router.py` | 4310 | `3de51baa670995c1737f663211ec48aefff7837037ab17f2267e7f94970415f7` |
| `tests/test_nexus_prompt.py` | 3251 | `8b2dd089a7454145f7fee84b4c7b577031398a445bd2737fbac2bbc6708abdfc` |
| `tests/test_observability.py` | 3748 | `653e58f66d0d816024844fa537f88c5bf0f418661388cb54c3390e9af59482f9` |
| `tests/test_quality_gate.py` | 2670 | `31fe61469c993329d7e78986fcd2cca7c1755018bf713b747ba1ed0f7fd68d04` |
| `tests/test_registry.py` | 1026 | `6d48f82b90c6e2b0007748668f35e875ceac26e103c49ac0f4ab794310892858` |
| `tests/test_release_manifest.py` | 4142 | `87647b637e626cafff99bd29120faf85a7b0b36fac4eb98a0ad49cfca4193726` |
| `tests/test_runtime.py` | 3486 | `d9f5f79e47b68f01a3215bd7bb4a40424d4de0ae7d7af48aa96b3d6746696c7d` |
| `tests/test_runtime_lock.py` | 3109 | `fda37c3189511f8101b02db18f5168e84099ac5b45847aca6fdc5223ee16863f` |
| `tests/test_security_hardening.py` | 14922 | `a4f92cfd0f2fa036ac94b9d3f256e4fdf1dc40791947206237c5e0f3127860d9` |
| `tests/test_server_launcher.py` | 1073 | `539f10cd5a416f4c9cb7d2ff242e41f553bf57b92004db1a6e11027234c81184` |
| `tests/test_server_run.py` | 2241 | `d01ebd3753c573dea7d98e7793f38ab27ed4e7691bcfa4cdb0f1e91e00dcbc20` |
| `tests/test_sessions.py` | 7538 | `a62a86c104eb844da2f481c5941dbce28214435b0281c61d0bc85b242f336202` |
| `tests/test_skill_api.py` | 1516 | `b1fbfe28a5d7bfd01816a6ccfa523de02b20dcbffc26486b9144c06c15d38902` |
| `tests/test_skill_runtime.py` | 4304 | `d7384b18c893ea6731476f123cb6d83a424ffb97f1b7221881d605cd67c992ff` |
| `tests/test_startup.py` | 3190 | `e0d75616ac7eab8b03c206971d173530354dc7ab5536768e3f9ca39bb626ee34` |
| `tests/test_validators.py` | 1376 | `917e334e7bf0ce930a30bf656519a2e786f2e2c5e9f7bf9cb346918d62bf608d` |
| `tests/test_versioning.py` | 1714 | `75eda9160dcf0058db74913f51c2f6bcf29171d49057a5aa3dbd69db9030d10e` |
| `tools/__init__.py` | 217 | `c34cd0b5966403d494755dbfe53a9b22d47978add2a8126ccb9670df24b58b37` |
| `tools/_handlers.py` | 5363 | `606c4d50f62177df18768f683fa0cb91f37f2881765f341d6e146b1b448742a7` |
| `tools/namespaces.py` | 15143 | `643c254f62c5e478bbe3b64272f9d2b6437401792ef835b89819121f310ddbfe` |
| `tools/registry.py` | 3821 | `a83e75b5ee38ac43e99b924645ed885efcc9d7236580f29eaf2cda2b96f3ac6c` |
| `tools/search_tool.py` | 454 | `db297ebf7e36f969e3316d988971a9da5a3e5e4ab0ac901449a60061c5d69a84` |
| `tracing/__init__.py` | 29 | `9c9fc8638c2520231249467fe163990c2e37c6adaa1544f32f33b10f3a8eaeed` |
| `tracing/otel_setup.py` | 219 | `3b15d1c3213dfdd442fdc786ceed888cd39b1b0e99d3e0d61ad80841142795d0` |
| `validators/__init__.py` | 32 | `e489ce99990282c0acf494b8206913a2c13fc54f01688789452811578287e44d` |
| `validators/arch02_validator.py` | 1020 | `35101672282a53446c0cda420e6907e7839551ee0a1713efb6d5b90624ea55d3` |
| `validators/arch04_validator.py` | 1370 | `f58d797d4fea3425283f11cb1d720aaccfc541a19ec54bf84c6c727cff20c6f4` |
| `validators/constraint_validator.py` | 5099 | `4c0ce5dafa341076035c3568918edbdedd05a37976d3bc2af9f771867997e5e9` |
| `validators/trace_block_validator.py` | 175 | `d8dcebc748265bd26cb9746e449983eb5091260b0351998a388847180abedd84` |
