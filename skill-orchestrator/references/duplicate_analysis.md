# Duplicate Skills Analysis Report
Generated: analyze_duplicates.py
Total candidates analyzed: 5

## Executive Summary

This report analyzes 5 duplicate/redundant skill candidates:
- 3 symlink duplicates (HIGH priority deletion)
- 2 deprecated versions (HIGH priority deletion)

---

## 1. stitch-enhance-prompt2 vs stitch-enhance-prompt

**Duplicate Type:** symlink duplicate

**stitch-enhance-prompt2** is a symlink → `../../../.agents/skills/enhance-prompt`

### Directory Structure Comparison

| Feature | stitch-enhance-prompt2 | stitch-enhance-prompt |
|---------|----------------------|---------------------|
| Exists | True | True |
| Is Symlink | True | False |
| Has SKILL.md | True | True |
| Has scripts/ | False | False |
| Script Count | 0 | 0 |
| Has references/ | True | True |

### Content Similarity: 100.0%

**Analysis:** Nearly identical content - clear duplicate.

### Recommendation

**Action:** DELETE `stitch-enhance-prompt2` (symlink duplicate)

**Reason:** This is a symlink pointing to external location. The canonical version `stitch-enhance-prompt` should be used.

**Impact:** None - symlink removal has no functional impact.

**Command:**
```bash
rm ~/.gemini/antigravity/skills/stitch-enhance-prompt2
```

---

## 2. stitch-react-components 2 vs stitch-react-components

**Duplicate Type:** symlink duplicate

**stitch-react-components 2** is a symlink → `../../../.agents/skills/react-components`

### Directory Structure Comparison

| Feature | stitch-react-components 2 | stitch-react-components |
|---------|-------------------------|-----------------------|
| Exists | True | True |
| Is Symlink | True | False |
| Has SKILL.md | True | True |
| Has scripts/ | True | True |
| Script Count | 1 | 1 |
| Has references/ | False | False |

### Content Similarity: 100.0%

**Analysis:** Nearly identical content - clear duplicate.

### Recommendation

**Action:** DELETE `stitch-react-components 2` (symlink duplicate)

**Reason:** This is a symlink pointing to external location. The canonical version `stitch-react-components` should be used.

**Impact:** None - symlink removal has no functional impact.

**Command:**
```bash
rm ~/.gemini/antigravity/skills/stitch-react-components 2
```

---

## 3. heic-converter vs heif-converter

**Duplicate Type:** incomplete symlink

### Directory Structure Comparison

| Feature | heic-converter | heif-converter |
|---------|--------------|--------------|
| Exists | True | True |
| Is Symlink | False | False |
| Has SKILL.md | False | True |
| Has scripts/ | False | True |
| Script Count | 0 | 1 |
| Has references/ | False | False |

### Recommendation

**Action:** DELETE `heic-converter` (symlink duplicate)

**Reason:** This is a symlink pointing to external location. The canonical version `heif-converter` should be used.

**Impact:** None - symlink removal has no functional impact.

**Command:**
```bash
rm ~/.gemini/antigravity/skills/heic-converter
```

---

## 4. continuous-learning vs continuous-learning-v2

**Duplicate Type:** deprecated version

**continuous-learning** is a symlink → `/Users/vecsatfoxmailcom/.gemini/antigravity/external/everything-claude-code/skills/continuous-learning-v2`

### Directory Structure Comparison

| Feature | continuous-learning | continuous-learning-v2 |
|---------|-------------------|----------------------|
| Exists | True | True |
| Is Symlink | True | False |
| Has SKILL.md | True | True |
| Has scripts/ | True | True |
| Script Count | 5 | 5 |
| Has references/ | False | False |

### Content Similarity: 100.0%

**Analysis:** Nearly identical content - clear duplicate.

### Recommendation

**Action:** DELETE `continuous-learning` (deprecated/older version)

**Reason:** Superseded by `continuous-learning-v2` which has better architecture/features.

**Impact:** Low - users should migrate to newer version.

**Command:**
```bash
rm -rf ~/.gemini/antigravity/skills/continuous-learning
```

---

## 5. to-notebooklm-artifacts vs media-to-notebooklm-artifacts

**Duplicate Type:** older version

### Directory Structure Comparison

| Feature | to-notebooklm-artifacts | media-to-notebooklm-artifacts |
|---------|-----------------------|-----------------------------|
| Exists | True | True |
| Is Symlink | False | False |
| Has SKILL.md | True | True |
| Has scripts/ | False | False |
| Script Count | 0 | 0 |
| Has references/ | False | False |

### Content Similarity: 50.4%

**Analysis:** Moderate similarity - may have overlapping functionality.

### Recommendation

**Action:** DELETE `to-notebooklm-artifacts` (deprecated/older version)

**Reason:** Superseded by `media-to-notebooklm-artifacts` which has better architecture/features.

**Impact:** Low - users should migrate to newer version.

**Command:**
```bash
rm -rf ~/.gemini/antigravity/skills/to-notebooklm-artifacts
```

---

## Deletion Summary

| Skill to Delete | Reason | Priority | Command |
|----------------|--------|----------|----------|
| stitch-enhance-prompt2 | symlink duplicate | HIGH | `rm stitch-enhance-prompt2` |
| stitch-react-components 2 | symlink duplicate | HIGH | `rm stitch-react-components 2` |
| heic-converter | incomplete symlink | HIGH | `rm heic-converter` |
| continuous-learning | deprecated version | HIGH | `rm -rf continuous-learning` |
| to-notebooklm-artifacts | older version | MEDIUM | `rm -rf to-notebooklm-artifacts` |

## Next Steps

1. Review each duplicate candidate above
2. Verify no active dependencies on skills marked for deletion
3. Execute deletion commands for approved candidates
4. Update `installation_log.md` with deletion entries
5. Commit changes to skills repository
