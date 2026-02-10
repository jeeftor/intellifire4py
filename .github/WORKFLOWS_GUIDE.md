# GitHub Actions Workflows Guide

## Overview

This repository uses several GitHub Actions workflows to ensure code quality, generate coverage reports, and securely publish packages.

---

## 🔄 Workflows

### 1. **Test & Coverage** (`test.yml`)
**Triggers**: Push to any branch, Pull Requests

**What it does**:
- Runs full test suite with pytest
- Generates coverage report
- Uploads coverage to Codecov
- Runs on **all branches** (including feature branches)

**Why it's important**: Ensures every push gets tested and coverage is tracked, even on feature branches.

### 2. **Coverage Comment** (`coverage-comment.yml`)
**Triggers**: Push to any branch, Pull Requests

**What it does**:
- Runs tests with detailed coverage
- Posts coverage report as PR comment
- Shows coverage changes vs base branch
- Uploads to Codecov with branch-specific flags
- Color-coded badges (green ≥90%, orange ≥80%)

**Why it's important**: Provides immediate visibility into coverage changes directly in PRs.

### 3. **SLSA Provenance** (`slsa-provenance.yml`)
**Triggers**: Release creation, Manual dispatch

**What it does**:
- Builds distribution packages
- Generates SLSA Level 3 provenance attestations
- Creates cryptographic hashes of artifacts
- Publishes to PyPI with attestations
- Provides supply chain security

**Why it's important**: 
- Proves package authenticity and build integrity
- Meets security compliance requirements
- Prevents supply chain attacks
- Required for many enterprise environments

**SLSA Level 3 Benefits**:
- ✅ Build platform attestation
- ✅ Non-falsifiable provenance
- ✅ Tamper-resistant build process
- ✅ Verifiable by consumers

### 4. **Release** (`release.yml`)
**Triggers**: Push to main/master/refactor branches

**What it does**:
- Auto-detects version changes
- Creates git tags
- Builds packages with `uv build`
- Publishes to PyPI (releases) or TestPyPI (dev builds)
- **Now includes SLSA attestations** via `attestations: true`

**Updated**: Now generates SLSA provenance for all PyPI uploads.

### 5. **Lint** (`lint.yml`)
**Triggers**: Push, Pull Requests

**What it does**:
- Runs ruff for code quality checks
- Ensures consistent code style

### 6. **Docs** (`docs.yml`)
**Triggers**: Push to main, Pull Requests

**What it does**:
- Builds Sphinx documentation
- Validates documentation builds correctly

---

## 🔐 SLSA Provenance Details

### What is SLSA?
SLSA (Supply-chain Levels for Software Artifacts) is a security framework that prevents tampering and improves integrity throughout the software supply chain.

### How to Verify SLSA Attestations

Users can verify your package authenticity:

```bash
# Install the SLSA verifier
pip install slsa-verifier

# Download package and attestation from PyPI
pip download intellifire4py --no-deps

# Verify the attestation
slsa-verifier verify-artifact \
  --provenance-path intellifire4py-*.intoto.jsonl \
  --source-uri github.com/YOUR_USERNAME/intellifire4py \
  intellifire4py-*.whl
```

### Benefits for Users
1. **Authenticity**: Proves the package came from your GitHub repository
2. **Integrity**: Ensures package wasn't tampered with after build
3. **Transparency**: Full build process is documented
4. **Compliance**: Meets security requirements for enterprise use

---

## 📊 Coverage Reporting

### Codecov Integration

Coverage reports are uploaded to Codecov on every push. You'll see:
- Overall coverage percentage
- Coverage changes in PRs
- File-by-file coverage breakdown
- Historical coverage trends

### Setting Up Codecov

1. Go to [codecov.io](https://codecov.io)
2. Connect your GitHub repository
3. Add `CODECOV_TOKEN` to repository secrets:
   - Go to Settings → Secrets and variables → Actions
   - Add new secret: `CODECOV_TOKEN`
   - Paste token from Codecov dashboard

### Coverage Badges

Add to your README.md:

```markdown
[![codecov](https://codecov.io/gh/YOUR_USERNAME/intellifire4py/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/intellifire4py)
```

---

## 🚀 Feature Branch Coverage

### Before
- Coverage only ran on `main` branch pushes
- Feature branches needed a PR to get coverage

### After
- Coverage runs on **every push to any branch**
- See coverage immediately when pushing feature branches
- Track coverage changes before creating PR

### Example Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to GitHub - coverage runs automatically!
git push origin feature/my-feature

# Check GitHub Actions tab to see coverage report
```

---

## 🔧 Required Secrets

Add these to your repository secrets (Settings → Secrets and variables → Actions):

| Secret | Purpose | Required For |
|--------|---------|--------------|
| `CODECOV_TOKEN` | Upload coverage to Codecov | Coverage reporting |
| `GITHUB_TOKEN` | Automatically provided | All workflows |

**Note**: PyPI publishing uses Trusted Publishers (no token needed).

---

## 📈 Monitoring

### GitHub Actions Tab
- View all workflow runs
- Check test results
- Download coverage reports
- See SLSA attestations

### Codecov Dashboard
- Track coverage over time
- Compare branches
- Identify uncovered code
- Set coverage targets

### PyPI Package Page
- View SLSA attestations
- Verify package integrity
- Check provenance metadata

---

## 🎯 Best Practices

### For Contributors
1. **Push early, push often**: Coverage runs on all branches
2. **Check coverage**: Review reports before creating PR
3. **Maintain coverage**: Aim for ≥90% (green), minimum 80% (orange)
4. **Write tests**: Add tests for all new features

### For Maintainers
1. **Review coverage changes**: Check PR coverage comments
2. **Verify SLSA**: Ensure attestations are generated on releases
3. **Monitor trends**: Use Codecov dashboard for insights
4. **Update dependencies**: Keep workflow actions up to date

---

## 🐛 Troubleshooting

### Coverage not uploading?
- Check `CODECOV_TOKEN` is set correctly
- Verify coverage.xml is being generated
- Check Codecov dashboard for errors

### SLSA workflow failing?
- Ensure release was created (not just a tag)
- Check permissions are set correctly
- Verify build artifacts are generated

### Tests not running on feature branch?
- Check GitHub Actions tab for workflow runs
- Verify branch name doesn't contain special characters
- Ensure workflow files are in `.github/workflows/`

---

## 📚 Additional Resources

- [SLSA Framework](https://slsa.dev/)
- [Codecov Documentation](https://docs.codecov.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator)

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Push to any branch                                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──► Test & Coverage (test.yml)
                 │    ├─ Run pytest
                 │    ├─ Generate coverage.xml
                 │    └─ Upload to Codecov
                 │
                 └──► Coverage Comment (coverage-comment.yml)
                      ├─ Run pytest with coverage
                      ├─ Upload to Codecov (with flags)
                      └─ Post PR comment (if PR)

┌─────────────────────────────────────────────────────────┐
│  Push to main/master/refactor                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 └──► Release (release.yml)
                      ├─ Detect version change
                      ├─ Build package with uv
                      ├─ Generate SLSA attestations
                      └─ Publish to PyPI/TestPyPI

┌─────────────────────────────────────────────────────────┐
│  Create Release                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 └──► SLSA Provenance (slsa-provenance.yml)
                      ├─ Build distribution
                      ├─ Generate SHA256 hashes
                      ├─ Create SLSA L3 provenance
                      └─ Publish with attestations
```

---

**Last Updated**: 2026-02-10  
**Maintained by**: Repository maintainers
