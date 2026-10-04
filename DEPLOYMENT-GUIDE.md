# Beginner guide: publish the frontend on GitHub Pages

This guide is for the separate frontend repository:
`Simran096/INDY-MONEY---Mutual-Fund-FAQ-Front-End`.

The frontend deployment workflow supports either of these layouts:

- A frontend copied into the repository root (`package.json` is at the top
  level). This is the recommended layout for the frontend-only repository.
- The full project layout with the frontend in `app/`.

## Part A: Copy the frontend into your GitHub repository

1. Install and open [GitHub Desktop](https://desktop.github.com/).
2. Sign in to GitHub Desktop.
3. In GitHub Desktop, choose **File → Clone repository**.
4. Select the **URL** tab and paste:
   `https://github.com/Simran096/INDY-MONEY---Mutual-Fund-FAQ-Front-End`
5. Choose where to save the repository on your computer and click **Clone**.
6. Open the newly cloned repository folder in File Explorer.
7. In another File Explorer window, open:
   `C:\Users\hp\Downloads\RAG Bot\app`
8. Copy the frontend project files and folders into the cloned repository's
   top level. Copy `src`, `package.json`, `package-lock.json`,
   `next.config.js`, `next-env.d.ts`, `postcss.config.js`,
   `tailwind.config.ts`, and `tsconfig.json` if present.
9. Do **not** copy `.env.local`, `node_modules`, `.next`, `out`,
   `build-output.txt`, `buildlog.txt`, or `tsconfig.tsbuildinfo`.
10. In the cloned repository, create the folder path
    `.github/workflows/`. Copy this deployment workflow into that folder as
    `deploy-pages.yml`:
    `.github/workflows/deploy-pages.yml` from the full project folder.
11. In GitHub Desktop, review the **Changes** list. Confirm `.env.local` is
    absent. Enter a summary such as `Add frontend and Pages deployment`,
    click **Commit to main**, then click **Push origin**.

The frontend folder's `next.config.js` must include static export settings
(`output: "export"`, `trailingSlash: true`, and `images.unoptimized: true`).
The project copy in this workspace is already configured that way.

## Part B: Turn on GitHub Pages

1. Open the repository page on GitHub.
2. Click **Settings**.
3. In the left menu, click **Pages**.
4. Under **Build and deployment → Source**, choose **GitHub Actions**.

## Part C: Connect the API (optional for the first UI deployment)

The frontend can be published before the backend is ready. Without an API URL,
the page shows that chat is not connected and does not try to call `localhost`.
To enable answers after the backend is deployed:

1. In the repository, go to **Settings → Secrets and variables → Actions →
   Variables**.
2. Click **New repository variable**.
3. Enter the name `NEXT_PUBLIC_API_URL`.
4. For the value, enter the Render service URL only, for example
   `https://your-service.onrender.com`. Do not add `/api` or a trailing slash.
5. Click **Add variable**.
Do not add `OPENAI_API_KEY` to GitHub. Keep it secret in Render.
Do not add `OPENAI_API_KEY` to GitHub. Keep it secret in Render.

After adding or changing `NEXT_PUBLIC_API_URL`, rerun the Pages workflow so
the new value is included in the static site.

## Part D: Run the deployment

1. Click the repository's **Actions** tab.
2. Select **Deploy frontend to GitHub Pages** in the workflows list.
3. Click **Run workflow**, keep the branch set to `main`, then confirm **Run
   workflow**.
4. Wait for the run to finish with a green check.
5. Open **Settings → Pages** or the Actions deployment summary to find the
   published site URL.

For this repository, the expected website address is:
`https://simran096.github.io/INDY-MONEY---Mutual-Fund-FAQ-Front-End/`

## Part E: Test it

Open the website and confirm that the frontend loads. Until the API is
connected, the page displays a notice and chat requests explain that the
service is unavailable. After connecting the API, ask a factual question and
confirm that a reply and official citation appear. If chat cannot connect,
confirm that `NEXT_PUBLIC_API_URL` is correct and the Render service is running.

In Render, set `ALLOWED_ORIGINS` to this origin (no repo path and no trailing
slash):
`https://simran096.github.io`

After changing `NEXT_PUBLIC_API_URL`, run the GitHub Actions workflow again.
After changing Render's `ALLOWED_ORIGINS`, redeploy or restart the Render
service.
