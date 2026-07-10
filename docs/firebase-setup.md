# Firebase setup for Legal Eval (GCP project: `legaleval`)

One-time manual steps in Firebase / Google Cloud consoles. These cannot be automated from this repo.

## 1. Add Firebase to the existing GCP project

1. Open [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project** → **Add Firebase to an existing Google Cloud project**.
3. Select **`legaleval`** (same project as Cloud Run / Artifact Registry).
4. Complete the wizard (Analytics optional).

Using the same GCP project keeps billing, IAM, and Cloud Run deployment in one place.

## 2. Register the web app

1. Firebase Console → **Project settings** → **Your apps** → **Add app** → **Web** (`</>`).
2. Register app name (e.g. `legal-eval-ui`).
3. Copy the `firebaseConfig` values into `legal-eval-ui/.env.local` (see `.env.local.example`).

## 3. Enable sign-in providers

Firebase Console → **Build** → **Authentication** → **Sign-in method**:

- Enable **Email/Password**
- Enable **Google** (set support email; add authorized domains: `localhost`, your production domain)

## 4. Authorized domains

Authentication → **Settings** → **Authorized domains**:

- `localhost` (dev)
- Your Cloud Run / custom UI hostname in production

## 5. API backend (legal-eval-api on Cloud Run)

The API verifies Firebase **ID tokens** with `firebase-admin` using **Application Default Credentials** (the Cloud Run service account). No JSON key file is required on Cloud Run when Firebase is enabled on the same GCP project.

Set on Cloud Run (optional override):

```bash
FIREBASE_PROJECT_ID=legaleval
```

Local API dev:

```bash
gcloud auth application-default login
export FIREBASE_PROJECT_ID=legaleval
```

## 6. UI session cookies (optional local dev)

The UI sets an httpOnly `__session` cookie via `/api/auth/session` for middleware route protection. That route uses `firebase-admin` with ADC locally, or `FIREBASE_SERVICE_ACCOUNT_JSON` if ADC is unavailable.

## 7. Deploy checklist

- [ ] Firebase enabled on `legaleval`
- [ ] Email + Google providers enabled
- [ ] Web app config in UI env vars
- [ ] `FIREBASE_PROJECT_ID=legaleval` on API Cloud Run service
- [ ] Authorized domains include production UI URL
