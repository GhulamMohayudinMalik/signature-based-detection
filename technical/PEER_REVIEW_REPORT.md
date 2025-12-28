# Peer Review Report: MalGuard Technical Paper

**Manuscript Title:** MalGuard: A Cross-Platform Signature-Based Malware Detection System with HMAC-Protected Signature Database

**Review Date:** December 28, 2025

**Reviewer Role:** Expert Peer Reviewer (Cybersecurity Journal)

---

## Executive Summary

This paper presents MalGuard, an open-source cross-platform malware detection system combining SHA-256 hash matching with YARA pattern detection. While the system implementation is technically sound and the paper is well-written, several issues require attention before publication, primarily related to **evaluation methodology**, **novelty claims**, and **statistical consistency**.

**Overall Recommendation:** Major Revision Required

---

## 1. Technical Soundness

### ✅ Strengths

| Aspect | Assessment |
|--------|------------|
| SHA-256 hash matching implementation | Correct; chunked reading (64KB) is appropriate |
| HMAC-SHA256 database protection | Valid security measure against tampering |
| Two-stage detection pipeline | Sound architecture (hash → YARA fallback) |
| Algorithm pseudocode | Correct and matches implementation description |
| RESTful API design | Follows proper REST conventions |
| Cross-platform architecture | Well-designed client-server paradigm |

### ⚠️ Issues

| Priority | Issue | Location | Recommendation |
|----------|-------|----------|----------------|
| **MEDIUM** | **HMAC key management not addressed** | Section III-E | The paper describes HMAC protection but doesn't explain how the secret key is stored/managed. If stored alongside the database, it defeats the purpose. Clarify key derivation/storage strategy. |
| **MEDIUM** | **Quarantine bypass not discussed** | Section III-B | Auto-quarantine could be evaded by malware that runs before being scanned. Add threat model discussion for on-demand vs real-time scanning. |
| **LOW** | **64KB chunk size claim** | Section IV-C | States "64KB chunk size was empirically determined" but no empirical data is presented. Either provide benchmarks or rephrase as "commonly recommended." |

---

## 2. Novelty Assessment

### ⚠️ Concerns

| Priority | Issue | Recommendation |
|----------|-------|----------------|
| **HIGH** | **Limited novelty claim** | The core techniques (SHA-256 hashing, YARA rules) are well-established. The paper's contribution is primarily **engineering integration** rather than algorithmic innovation. Consider reframing the contribution as "unified cross-platform implementation" rather than implying novel detection methods. |
| **MEDIUM** | **HMAC protection not novel** | Section III-E cites RFC 2104 (1997). HMAC for database integrity is standard practice. Rephrase to "applies established HMAC protection" rather than suggesting novelty. |
| **LOW** | **Comparison with ClamAV unfair** | Table VII claims ClamAV lacks "REST API" and "Web Interface" but ClamAV-REST and ClamAV web interfaces exist as third-party projects. Update comparison or add footnote. |

---

## 3. Evaluation Quality

### 🔴 Critical Issues

| Priority | Issue | Location | Details |
|----------|-------|----------|---------|
| **HIGH** | **Extremely small test corpus** | Section V-B | Only **25 malware samples** and **400 benign files** were tested. Modern malware research uses datasets of 100K+ samples (e.g., VirusShare, EMBER). This severely limits generalizability claims. |
| **HIGH** | **No external malware dataset** | Section V-B | The paper uses "curated malware signatures" rather than actual malware samples. Testing hashes in a database against themselves is trivially 100% accurate—this is **not a meaningful detection test**. |
| **HIGH** | **YARA evaluation missing** | Section V-C | Claims "8 custom YARA rules" but provides no detection results specifically for YARA. How many files did YARA catch that hash matching missed? |

### ⚠️ Methodology Issues

| Priority | Issue | Location | Recommendation |
|----------|-------|----------|----------------|
| **MEDIUM** | **No standard benchmark dataset** | Section V-B | Consider using EMBER, MalwareBazaar, or VirusShare subsets. Add limitation statement about dataset size. |
| **MEDIUM** | **Single hardware configuration** | Section V-B | Tests run only on i7-12700H. Add mobile device benchmarks since mobile is a claimed platform. |
| **MEDIUM** | **No memory leak testing** | Section V-D | Claims "memory consumption remained stable at 25-45MB" but no methodology for measuring this over time or under stress. |
| **LOW** | **"3 runs averaged" insufficient** | Section V-B | Statistical rigor requires more runs or confidence intervals. Consider 10+ runs with proper statistical analysis. |

---

## 4. Abstract vs. Results Cross-Reference

### 🔴 Statistical Discrepancies Found

| Claim in Abstract | Evidence in Results | Assessment |
|-------------------|---------------------|------------|
| "100% detection accuracy" | Table IV: 25/25 detected | ✅ **Consistent** but misleading—this is trivially expected for signature matching against known hashes |
| "zero false positives" | Eq. 7: FPR = 0/400 = 0% | ✅ **Consistent** |
| "scan throughput exceeding 120 files per second" | Section V-D: "120-150 files/second" | ✅ **Consistent** |
| "Cross-platform compatibility testing verified" | Table VI: All platforms "Full Support" | ⚠️ **Vague** - No specific test metrics or procedures described |

### ⚠️ Misleading Claims

| Priority | Issue | Recommendation |
|----------|-------|----------------|
| **HIGH** | **"100% detection accuracy" is misleading** | 100% is guaranteed by design for exact hash matching. This is like claiming a dictionary lookup achieves 100% accuracy. Rephrase to "100% for known signatures in the database" and discuss detection gap for unknown malware. |
| **MEDIUM** | **Abstract omits sample sizes** | 25 malware samples and 400 benign files should be mentioned to set appropriate expectations. |

---

## 5. Writing Quality

### ✅ Strengths

| Aspect | Assessment |
|--------|------------|
| Organization | Excellent; follows standard IEEE structure |
| Grammar/spelling | Professional quality, minimal errors |
| Figure quality | Diagrams are clear and informative |
| Algorithm presentation | Well-formatted pseudocode |
| Related work coverage | Good breadth of citations |

### ⚠️ Issues

| Priority | Issue | Location | Recommendation |
|----------|-------|----------|----------------|
| **LOW** | **Inconsistent "we" usage** | Throughout | Some sections use "we" while others are passive. Standardize. |
| **LOW** | **Missing React Native citation** | References | `reactnative2024` and `expo2024` are in .bib but not cited in paper. Either cite or remove. |
| **LOW** | **Version specificity** | Section V-B | Hardware specs (i7-12700H) are good, but Python 3.11.5 patch version is unnecessary. Use "Python 3.11" consistently. |

---

## 6. References Quality

### ⚠️ Issues

| Priority | Issue | Details |
|----------|-------|---------|
| **LOW** | **Old benchmarks** | Core detection techniques cite papers from 2007-2014 (Idika 2007, Gandotra 2014). Consider adding recent surveys (2021-2024). |
| **LOW** | **"2024" tool citations** | ClamAV, FastAPI, SQLite cited as 2024 but these are evergreen tools. Consider using "n.d." or last access date format. |
| **LOW** | **Unused references** | `reactnative2024` and `expo2024` defined but not cited in paper body. |

---

## 7. Priority Summary

### 🔴 HIGH Priority (Must Fix Before Publication)

1. **Expand evaluation dataset** - 25 malware samples is insufficient. Use at least a subset of a standard malware dataset (e.g., 1000+ samples from MalwareBazaar).
2. **Test with actual malware files** - Currently testing if hashes match a database of hashes. Need to test actual malware binaries against signatures.
3. **Clarify "100% accuracy" claim** - Rephrase to avoid misleading readers; explain this is for known signatures only.
4. **Add YARA-specific evaluation** - Show what YARA detects that hash matching misses.
5. **Explain HMAC key management** - Critical security detail is missing.

### ⚠️ MEDIUM Priority (Strongly Recommended)

6. **Add dataset size to abstract** - Set appropriate expectations.
7. **Include mobile device benchmarks** - Since mobile is a claimed platform.
8. **Discuss threat model limitations** - On-demand scanning vs. real-time.
9. **Reframe novelty claims** - Focus on integration, not techniques.
10. **Update ClamAV comparison** - Account for ecosystem tools.

### 📝 LOW Priority (Minor Improvements)

11. **Standardize passive/active voice**
12. **Remove or cite unused references**
13. **Add recent 2021-2024 references**
14. **Fix Python version specificity**
15. **Provide data for 64KB chunk claim**

---

## Recommendation Matrix

| Criterion | Score (1-5) | Comments |
|-----------|-------------|----------|
| Technical Soundness | 4/5 | Sound implementation, minor gaps |
| Novelty | 2/5 | Engineering contribution, not algorithmic |
| Evaluation Quality | 2/5 | Severely limited by sample size |
| Writing Quality | 4/5 | Professional, minor issues |
| Reproducibility | 3/5 | Open source helps, but test data missing |
| **Overall** | **3/5** | Major revision needed for evaluation |

---

## Final Verdict

**Decision:** Major Revision Required

The paper presents a well-implemented cross-platform malware detection system with sound architecture. However, the evaluation methodology is fundamentally flawed—testing signature matching against its own database guarantees 100% accuracy and provides no meaningful validation. The authors must:

1. Evaluate against a recognized malware dataset with actual malware samples
2. Clarify that 100% accuracy applies only to known signatures
3. Demonstrate YARA's incremental value quantitatively
4. Address HMAC key management security

With these revisions, the paper would make a solid contribution to open-source security tooling literature.

---

*Reviewed by: Expert Peer Reviewer (Cybersecurity)*
*Review Confidence: High*
