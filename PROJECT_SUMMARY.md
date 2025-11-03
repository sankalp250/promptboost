# PromptBoost - Project Summary

## What This Project Does

**PromptBoost** is an AI-powered prompt enhancement tool that helps users improve their prompts for better AI interactions. It works by:

### Core Functionality

1. **Prompt Enhancement** (`!!e` trigger)
   - Users copy text and add `!!e` at the end
   - The system detects this, sends it to a server
   - Server uses LLM (Groq/Gemini) to enhance the prompt
   - Enhanced prompt replaces clipboard content
   - Transforms vague prompts into detailed, actionable prompts

2. **Reroll/Alternative Enhancements** (Keyboard: `Ctrl+Shift+R`)
   - After getting an enhancement, user can request a different version
   - System marks previous as "rejected"
   - Gets a new enhancement with different wording/structure
   - Uses higher temperature (0.9) for more variation

3. **Feedback System**
   - Users can reject enhancements (Ctrl+Shift+X)
   - Tracks user preferences for ML model training
   - Collects data to improve enhancement quality

4. **Quality Filter**
   - ML model predicts if enhancement will be accepted (probability)
   - Retries up to 3 times if quality is low (< 0.60)
   - Saves results for analytics

### Architecture

**Client Side:**
- Windows desktop app (tray icon)
- Monitors clipboard for `!!e` suffix
- Keyboard shortcuts for feedback/reroll
- Sends requests to server API

**Server Side:**
- FastAPI backend
- LangGraph workflow for enhancement
- LLM integration (Groq primary, Gemini fallback)
- ML quality prediction model
- Database for caching and analytics

### Current Features

✅ Clipboard monitoring for `!!e` enhancement
✅ Keyboard shortcut for reroll (`Ctrl+Shift+R`)
✅ Keyboard shortcut for rejection (`Ctrl+Shift+X`)
✅ Quality-based retry mechanism
✅ State management (session tracking)
✅ Database caching (temporarily disabled for data collection)
✅ ML preference model for quality prediction

## What Needs Improvement

### Critical Issues

1. **`!!d` Clipboard Trigger Not Working** ❌
   - Current implementation unreliable
   - **SOLUTION**: Use keyboard shortcut instead (Ctrl+Shift+R) - DONE ✅

2. **State Persistence**
   - Sometimes loses track of original prompt
   - Need better error handling

### Features to Add

1. **User Interface**
   - GUI window for viewing history
   - Settings panel for customization
   - Show enhancement before applying

2. **Analytics Dashboard**
   - View enhancement history
   - Acceptance/rejection rates
   - Quality metrics

3. **Enhanced Reroll**
   - Multiple reroll strategies (conservative vs creative)
   - Side-by-side comparison
   - Save favorite versions

4. **Better Prompt Context Detection**
   - Detect more programming languages
   - Domain-specific personas
   - Multi-language support

5. **Performance**
   - Faster response times
   - Better caching strategy
   - Request queuing

6. **User Experience**
   - Progress indicators
   - Undo functionality
   - Keyboard shortcut customization
   - Multiple enhancement templates

7. **Data Collection**
   - Better feedback mechanisms
   - A/B testing different prompts
   - Learning from user edits

8. **Deployment**
   - Cloud deployment option
   - Mobile app version
   - Browser extension
   - API for third-party integration

### Technical Debt

- Clean up excessive debugging code
- Improve error handling
- Add comprehensive tests
- Better logging system
- Configuration management

