# GitHub Actions Workflows

This directory contains automated workflows for the IDX-BEI project.

## 📋 Workflows

### 1. **Refresh Warrant Data** ([refresh-data.yml](refresh-data.yml))
Automatically collects fresh data from IDX daily.

- **Schedule**: Daily at 8 AM UTC (4 PM Jakarta time)
- **Manual trigger**: Available via GitHub Actions UI
- **Actions**:
  - Scrapes structured warrants data
  - Fetches underlying OHLC from Yahoo Finance
  - Gets warrant trading prices
  - Auto-commits changes to the repository

### 2. **Deploy Dashboard to GitHub Pages** ([deploy-pages.yml](deploy-pages.yml))
Deploys the HTML dashboard whenever data changes.

- **Trigger**: Automatically runs when data files are updated
- **Manual trigger**: Available via GitHub Actions UI
- **Actions**:
  - Configures GitHub Pages
  - Deploys the `data/` directory as a static site

### 3. **Test Data Collection** ([test-scraper.yml](test-scraper.yml))
Tests the data collection scripts on pull requests.

- **Trigger**: When scraper scripts are modified
- **Manual trigger**: Available via GitHub Actions UI
- **Actions**:
  - Runs the scraper pipeline
  - Verifies all output files are created
  - Uploads test data as artifacts

---

## 🚀 Setup Instructions

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (left sidebar)
3. Under **Build and deployment**:
   - **Source**: Deploy from a branch
   - **Branch**: `main` (or your default branch)
   - **Folder**: `/ (root)`
4. Click **Save**

Your dashboard will be available at:
```
https://<your-username>.github.io/<repo-name>/structured_warrants.html
```

### Step 2: Enable Workflow Permissions

1. Go to **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

### Step 3: Test the Workflows

**Option A: Push the workflows**
```bash
git add .github/
git commit -m "ci: add GitHub Actions workflows"
git push
```

**Option B: Manual trigger**
1. Go to **Actions** tab in your repository
2. Select **Refresh Warrant Data**
3. Click **Run workflow**
4. Choose branch and click **Run workflow**

---

## 📊 Monitoring

### View Workflow Runs
- Go to the **Actions** tab in your repository
- Click on any workflow to see its execution history

### Check Latest Data Update
- Check the commit history for automated commits from `github-actions[bot]`
- Commits are timestamped: `chore: refresh warrant data - YYYY-MM-DD HH:MM:SS UTC`

### View Live Dashboard
Once deployed, your dashboard will be accessible at:
```
https://<your-username>.github.io/<repo-name>/structured_warrants.html
```

---

## 🔧 Customization

### Change Schedule
Edit [refresh-data.yml](refresh-data.yml):
```yaml
schedule:
  - cron: '0 8 * * *'  # Daily at 8 AM UTC
  # - cron: '0 */6 * * *'  # Every 6 hours
  # - cron: '0 0 * * 1'  # Every Monday at midnight
```

### Change Python Version
Edit the `python-version` in any workflow:
```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.13'  # Change here
```

---

## 🐛 Troubleshooting

### Workflow fails with "Permission denied"
- Make sure workflow permissions are set to "Read and write"
- Check Settings → Actions → General → Workflow permissions

### Pages deployment fails
- Ensure GitHub Pages is enabled in Settings → Pages
- Verify the `data/` directory contains `structured_warrants.html`

### Data collection fails
- Check the Actions logs for specific error messages
- Test locally with: `python python/scrape_sw_combined.py`
- Verify all dependencies are listed in the workflow

---

## 📦 Free Tier Limits

GitHub Actions free tier includes:
- **2,000 minutes/month** for private repositories
- **Unlimited minutes** for public repositories
- **500 MB storage** for artifacts

Your workflow uses approximately:
- **~3-5 minutes** per data refresh run
- **~600 runs/month** (daily schedule = ~30 runs)
- **Well within free tier limits** ✅

---

## 📝 Notes

- Data is automatically committed with `[skip ci]` to prevent infinite loops
- Workflows can be manually triggered from the Actions tab
- All workflows have proper error handling and summary outputs
- Artifacts from test runs are kept for 7 days
