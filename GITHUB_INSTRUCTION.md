# GitHub Deployment Instructions

## 1. Create Private Repository

1. Go to https://github.com/new
2. Repository name: `prompt-strategist-bot`
3. Select **Private**
4. Do NOT initialize with README
5. Click **Create repository**

## 2. Link Local Repository

Run these commands in terminal:

```bash
cd "C:\Users\vipvo\Documents\Проект\Промтинг"
git remote add origin https://github.com/YOUR_USERNAME/prompt-strategist-bot.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## 3. Verify

Open: https://github.com/YOUR_USERNAME/prompt-strategist-bot

You should see all project files.

---

## Security Notes

- `.env` file is **NOT committed** to Git (in `.gitignore`)
- After cloning, copy `.env.example` to `.env`
- Fill in your API keys locally
- **Never commit `.env` with keys!**

---

## Future Commits

After making changes:

```bash
git add .
git commit -m "Description"
git push
```
