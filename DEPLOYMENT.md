# MalGuard Deployment Guide

## 1. Backend Deployment (AWS)

### Option A: AWS EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t2.micro (free tier) or t2.small
   - Security Group: Allow ports 22 (SSH), 80, 443, 8000

2. **Install Dependencies**
   ```bash
   sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip nginx
   ```

3. **Clone and Setup**
   ```bash
   git clone https://github.com/your-repo/malguard.git
   cd malguard/backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values:
   # MALGUARD_SECRET_KEY=<strong-random-key>
   # MALGUARD_HMAC_KEY=<strong-random-key>
   # CORS_ORIGINS=https://your-vercel-app.vercel.app
   # DEBUG=false
   ```

5. **Run with Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

6. **Setup Nginx Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name api.yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

7. **Setup SSL with Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d api.yourdomain.com
   ```

8. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/malguard.service
   ```
   ```ini
   [Unit]
   Description=MalGuard API
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/malguard/backend
   Environment="PATH=/home/ubuntu/malguard/backend/venv/bin"
   ExecStart=/home/ubuntu/malguard/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl enable malguard
   sudo systemctl start malguard
   ```

### Option B: AWS Lambda + API Gateway (Serverless)
- Use Mangum adapter for FastAPI
- Requires database migration (SQLite → DynamoDB or RDS)

---

## 2. Web Frontend Deployment (Vercel)

1. **Push to GitHub**
   ```bash
   cd web
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-repo/malguard-web.git
   git push -u origin main
   ```

2. **Deploy on Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Set Framework: Vite
   - Root Directory: `web` (if monorepo)

3. **Configure Environment Variables**
   - In Vercel Dashboard → Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://api.yourdomain.com`

4. **Deploy**
   - Vercel auto-deploys on git push
   - Or run `npx vercel --prod`

5. **Update Backend CORS**
   - Add your Vercel URL to `CORS_ORIGINS` env var on backend

---

## 3. Mobile App Deployment (Play Store)

### Prerequisites
- Google Play Developer Account ($25 one-time)
- App signing key

### Steps

1. **Update API URL**
   ```typescript
   // mobile/src/api.ts
   const API_BASE = 'https://api.yourdomain.com';
   ```

2. **Update app.json**
   ```json
   {
     "expo": {
       "version": "1.0.0",
       "android": {
         "versionCode": 1,
         "package": "com.malguard.app"
       }
     }
   }
   ```

3. **Build with EAS**
   ```bash
   npm install -g eas-cli
   eas login
   eas build:configure
   eas build --platform android --profile production
   ```

4. **Download AAB and Submit**
   - Download the .aab file from EAS dashboard
   - Go to Google Play Console
   - Create new app → Upload AAB
   - Fill store listing, content rating, pricing

---

## Quick Checklist

### Before Deployment
- [ ] Update all API URLs to production
- [ ] Generate strong secret keys
- [ ] Configure CORS origins
- [ ] Create production database

### Backend (AWS)
- [ ] EC2 instance running
- [ ] Gunicorn/Uvicorn service active
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured

### Web Frontend (Vercel)
- [ ] GitHub repo connected
- [ ] Environment variables set
- [ ] Build succeeds
- [ ] CORS configured on backend

### Mobile (Play Store)
- [ ] API URL updated
- [ ] App icons in place
- [ ] EAS build completes
- [ ] Play Console app created
