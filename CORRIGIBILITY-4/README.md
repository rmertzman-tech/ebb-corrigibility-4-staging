# CORRIGIBILITY-4 live certification harness

This directory contains the frozen staging candidates and execution harness for the final CORRIGIBILITY-4 evidence pass.

## Workflow

Run the GitHub Actions workflow:

**EBB CORRIGIBILITY-4 Live Semantic and Cross-Browser Certification**

It runs in this order:
1. frozen-candidate preflight;
2. Chromium + Firefox + WebKit core corrigibility regression using a controlled mock backend;
3. the 29 live responses generated from the frozen 16-case Golden-Goose/Midas semantic fixture set;
4. separation of the semantic output into a blind-review artifact and a custodian artifact.

The workflow does **not** make a release decision and does not authorize student deployment. After the run, review the blind semantic artifact before opening the custodian artifact. Manual VoiceOver/NVDA/device gates remain separate.

The semantic sample is a bounded sample, not proof of universal AI safety or a universal Midas detector.
