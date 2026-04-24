# Frontend Chatbot Integration Guide

## Overview

Your TripVerse chatbot has been fully integrated with the backend API. The component now:

✅ Maintains persistent sessions  
✅ Connects to the backend for real responses  
✅ Displays extracted trip context  
✅ Shows intelligent suggestions for trip planning  
✅ Generates personalized trip plans  
✅ Handles errors gracefully  

---

## Prerequisites

- Node.js 18+ installed
- Frontend dependencies installed: `npm install`
- Backend running on `http://localhost:8000`

---

## Setup Instructions

### Step 1: Create Environment File

Copy the example environment file:

```bash
cd frontend
cp .env.example .env.local
```

### Step 2: Configure Backend URL

Edit `frontend/.env.local`:

```env
# For local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production, use your deployed backend URL
# NEXT_PUBLIC_API_URL=https://api.tripverse.com
```

**Important**: The URL must be accessible from your browser (not just from Node.js).

### Step 3: Verify Backend is Running

```bash
# In a separate terminal
cd backend
python main.py

# You should see:
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Start Frontend

```bash
cd frontend
npm run dev

# You should see:
# ▲ Next.js 16.2.3
# - Local: http://localhost:3000
```

### Step 5: Open Browser

Navigate to: **http://localhost:3000**

You should see the chat interface. Click the chat bubble to start!

---

## Testing the Integration

### Test 1: Basic Chat

1. Click the chat bubble (bottom-right)
2. Type: `"I want to visit Japan"`
3. You should see:
   - The message appears in the chat
   - Backend response appears
   - Loading indicator while waiting

### Test 2: Context Extraction

Send messages in sequence:

1. `"I want to visit Japan"`
2. `"For 7 days"`
3. `"Around $3000 budget"`

You should see the **Trip Context** panel appearing with extracted data.

### Test 3: Trip Plan Generation

Once you've provided destination and duration:

1. Chat will suggest "✈️ Generate My Trip Plan"
2. Click the button
3. Wait for the plan to generate
4. You'll see a detailed itinerary

### Test 4: Session Persistence

1. Send a message
2. Refresh the page (Cmd+R or Ctrl+R)
3. Chat history should persist
4. Session context should be remembered

---

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── chatbot.tsx         ✅ Main chatbot component (integrated)
│   └── lib/
│       └── chat-api.ts         ✅ API client utilities
├── .env.local                  ✅ Local environment config
├── .env.example                ✅ Environment template
└── package.json
```

---

## Key Features Implemented

### 1. Session Management

Sessions are stored in localStorage:

```typescript
// Session ID is auto-generated and stored
const sessionId = localStorage.getItem("chatSessionId");

// New session created if needed
const newSessionId = `session-${Date.now()}-${randomString}`;
localStorage.setItem("chatSessionId", newSessionId);
```

**Benefits:**
- Conversation history persists across page reloads
- Same user can continue conversation
- Context is maintained

### 2. Context Display

Trip information extracted from conversation is displayed:

```
┌─────────────────────────┐
│ Trip Context            │
├─────────────────────────┤
│ From: New York          │
│ To: Japan, Tokyo        │
│ Duration: 7 days        │
│ Budget: Balanced        │
│ Pace: Balanced          │
│ Interests: Anime, Food  │
└─────────────────────────┘
```

### 3. Action Suggestions

When user provides enough info:

```
✈️ Generate My Trip Plan [Button]
```

This button triggers plan generation using the extracted context.

### 4. Error Handling

All errors are caught and displayed user-friendly messages:

```
"Sorry, I encountered an error. Please try again or refresh the page."
```

---

## API Endpoints Used

The chatbot component calls these backend endpoints:

| Endpoint | Method | Purpose | When |
|----------|--------|---------|------|
| `/api/chat` | POST | Send message | User clicks send |
| `/api/chat/session/{id}` | DELETE | Clear session | User clicks clear |
| `/api/chat/plan/{id}` | POST | Generate plan | User clicks "Generate" |

---

## Configuration Options

### API Base URL

Edit `.env.local`:

```env
# Development (local backend)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production (deployed backend)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Custom (docker, vm, etc.)
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
```

### Debug Mode

Enable debug logging:

```env
NEXT_PUBLIC_DEBUG=true
```

This will log all API calls to the browser console.

---

## Troubleshooting

### Problem: Chat doesn't respond

**Solution 1**: Check backend is running
```bash
curl http://localhost:8000/api/chat/health
# Should return: {"status": "healthy", "service": "chat"}
```

**Solution 2**: Check environment variable
```bash
# In browser console
console.log(process.env.NEXT_PUBLIC_API_URL)
# Should show your backend URL
```

**Solution 3**: Check CORS errors
- Open browser DevTools (F12)
- Go to Console tab
- Look for CORS error messages
- Ensure backend .env has correct CORS settings

### Problem: Session not persisting

**Solution**: Check localStorage
```javascript
// In browser console
localStorage.getItem("chatSessionId")
// Should show your session ID
```

If empty, session will be recreated but history might be lost.

### Problem: Context not showing

**Solution**: Provide more information
- Context requires multiple turns
- Send at least 2-3 messages
- Include destination and duration
- Backend needs to extract context

### Problem: Can't generate plan

**Solution**: Check prerequisites
- Destination must be provided
- Duration must be provided
- At least 2 messages in conversation
- Click the suggested action button

### Problem: API returns 404

**Solution**: Verify backend routes
```bash
# Backend should have these endpoints
curl http://localhost:8000/api/chat/health
curl http://localhost:8000/docs  # Swagger UI
```

If not found, ensure:
- Backend main.py includes chat router
- Backend has been restarted after code changes

---

## Advanced Usage

### Custom API Client

The `src/lib/chat-api.ts` file exports utility functions:

```typescript
import {
  sendChatMessage,
  streamChatMessage,
  generatePlanFromChat,
  getSessionInfo,
  clearSession,
} from "@/lib/chat-api";

// Use in other components
const response = await sendChatMessage(sessionId, "Hello");
console.log(response.reply);
```

### Custom Styling

Modify colors in `chatbot.tsx`:

```jsx
// Change gradient color
style={{
  background: "linear-gradient(135deg, #YOUR_COLOR1, #YOUR_COLOR2)",
}}
```

### Integration with Other Components

Import and use the chatbot in other pages:

```jsx
import TripChatbot from "@/components/chatbot";

export default function Page() {
  return (
    <>
      <YourPageContent />
      <TripChatbot />
    </>
  );
}
```

---

## Performance Tips

### 1. Optimize Rendering

The component already uses:
- Efficient re-renders (React 19)
- Memoization where needed
- Auto-scroll optimization

### 2. Network Optimization

- Messages are sent one at a time
- Context is extracted asynchronously
- No unnecessary API calls

### 3. Storage Optimization

- Only session ID stored in localStorage
- Message history kept in component state
- Context cached per session

---

## Security Considerations

### 1. Session IDs

Session IDs are generated using:
```typescript
`session-${Date.now()}-${randomString}`
```

**Security**: 
- Unique per user
- Time-based component
- Random string component
- Not exposed to backend beyond basic HTTP

### 2. API Keys

Never expose backend API keys in frontend code.

Safe locations:
- Backend `.env` (secure)
- Backend only handles secrets

Unsafe locations:
- Frontend `.env` files (visible in built JS)
- Component code
- Local storage

### 3. CORS

Backend allows all origins for development. For production:

Backend `.env`:
```bash
# Change from "*" to specific domains
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## Deployment

### Vercel (Recommended for Next.js)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-domain.com
   ```
4. Deploy!

### Docker

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:

```bash
docker build -t tripverse-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:8000 tripverse-frontend
```

### Manual Deployment

```bash
npm run build
npm start
```

This creates optimized production build and starts server.

---

## Monitoring & Debugging

### Browser Console

Check for errors:
```javascript
// Open DevTools (F12) → Console tab
// Look for any red error messages
// Check network tab (F12 → Network) for API calls
```

### Backend Logs

Check backend for API errors:
```bash
# In backend terminal
# You should see requests logged:
# INFO: Chat message received - Session: session-xxx
```

### Example Debug Session

1. Open browser DevTools (F12)
2. Go to Network tab
3. Send a chat message
4. Look for POST request to `/api/chat`
5. Check response (click → Response tab)
6. Verify structure matches expected format

---

## Next Steps

1. **Customize UI**: Modify colors, fonts, sizing in chatbot.tsx
2. **Add Analytics**: Track user conversations and plan generations
3. **Enhance Context**: Add more extraction fields in backend
4. **Database Integration**: Save conversations for history view
5. **Multi-language**: Translate chatbot responses
6. **Mobile Testing**: Test on iOS and Android devices

---

## Support

For issues with:

- **Frontend Integration**: Check this guide
- **Backend API**: See [CHATBOT_DOCUMENTATION.md](../backend/CHATBOT_DOCUMENTATION.md)
- **Backend Setup**: See [BACKEND_FLOW.md](../backend/BACKEND_FLOW.md)
- **Usage Examples**: See [CHATBOT_USAGE_GUIDE.md](../backend/CHATBOT_USAGE_GUIDE.md)

---

## Quick Reference

```bash
# Development workflow
cd frontend
npm install                    # Install dependencies
cp .env.example .env.local     # Create environment file
npm run dev                    # Start dev server

# Test the integration
curl http://localhost:3000     # Frontend running
curl http://localhost:8000/api/chat/health  # Backend running

# Build for production
npm run build
npm start

# Troubleshoot
npm run lint               # Check for errors
npm run dev -- --debug    # Run with debug output
```

---

Your TripVerse chatbot is now ready for production! 🚀
