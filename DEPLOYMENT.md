# Deployment Guide

## 🚀 Production Deployment Options

### Option 1: Netlify (Frontend) + Railway/Render (Backend)

#### Frontend (Netlify):
1. Push code to GitHub
2. Connect Netlify to your GitHub repo
3. Set build settings:
   - Build command: `cd frontend && npm run build`
   - Publish directory: `frontend/dist`
4. Set environment variables:
   - `VITE_API_BASE_URL`: Your backend URL

#### Backend (Railway/Render):
1. Connect to GitHub repo
2. Set root directory to `backend`
3. Set environment variables:
   - `DATABASE_URL`: Your database connection string
   - `JWT_SECRET_KEY`: Strong random secret
   - `CORS_ORIGINS`: Your frontend domain

### Option 2: Vercel (Full Stack)
1. Push to GitHub
2. Import project to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically

### Option 3: Docker (Self-hosted)
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Environment Variables

### Frontend (.env.local):
```
VITE_API_BASE_URL=http://localhost:8000
```

### Backend:
```
DATABASE_URL=sqlite:///./data/prod.db
JWT_SECRET_KEY=your-super-secret-key-here
CORS_ORIGINS=https://your-frontend-domain.com
```

## 📋 Pre-deployment Checklist

- [ ] Update API URLs in config
- [ ] Set strong JWT secret key
- [ ] Configure CORS origins
- [ ] Test authentication flow
- [ ] Run database migrations
- [ ] Test all CRUD operations
- [ ] Verify timetable generation
- [ ] Check responsive design
- [ ] Test error handling

## 🔒 Security Considerations

1. **JWT Secret**: Use a strong, random secret key
2. **CORS**: Restrict to your domain only
3. **HTTPS**: Always use HTTPS in production
4. **Database**: Use proper database in production (not SQLite for high traffic)
5. **Environment Variables**: Never commit secrets to Git

## 📊 Monitoring

- Set up error tracking (Sentry)
- Monitor API performance
- Set up database backups
- Monitor authentication failures
