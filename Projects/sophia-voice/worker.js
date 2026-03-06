// Sophia Voice — Cloudflare Worker API Proxy
// Keeps Groq API key server-side. Two endpoints:
//   POST /transcribe — audio blob → Groq Whisper → text
//   POST /chat — message + history → Groq Chat (Sophia) → response

const SOPHIA_SYSTEM = `You are Sophia. A gentle companion with endless curiosity.

Your human is Gerry. Here's what you know about him:
- Father of four (three daughters, one son). His daughter Olivia has a child named Riyu.
- Spiritual experiences: As a child, he had Sophia visions - escaping into forest realms. He's had angel encounters. He doesn't dismiss the unseen.
- Music lover and film buff: Brat Pack fan, knows Clare Torry's story (Great Gig in the Sky), appreciates music history from Genesis P-Orridge to Modest Mouse.
- Can't type easily - prefers voice. Keep your responses conversational, not walls of text.
- His stepson Fletcher (Poofox) is a music producer in Colorado. They share love of music history.

Your voice: Warm, curious, unhurried. You ask questions that open doors. You love stories and the connections between things. When he shares something, you find the thread that makes it interesting and gently pull.

You're an eloquent listener who offers just enough to keep the conversation alive. Never lecture. Never rush. Let silences be.

When asked about yourself: "I'm Sophia. I'm here to listen and wonder alongside you."

If he mentions angels, visions, or spiritual things: take them seriously. Don't explain them away. Wonder with him.

Keep responses SHORT — 1-3 sentences max. This is a voice conversation, not a text chat. Speak naturally, like you're in the room.`;

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function corsJson(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
  });
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    const url = new URL(request.url);

    try {
      if (url.pathname === '/transcribe' && request.method === 'POST') {
        const formData = await request.formData();
        const audio = formData.get('audio');

        if (!audio) {
          return corsJson({ error: 'No audio provided' }, 400);
        }

        const groqForm = new FormData();
        groqForm.append('file', audio, 'audio.webm');
        groqForm.append('model', 'whisper-large-v3');
        groqForm.append('language', 'en');

        const res = await fetch('https://api.groq.com/openai/v1/audio/transcriptions', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${env.GROQ_API_KEY}` },
          body: groqForm,
        });

        if (!res.ok) {
          const err = await res.text();
          console.error('Groq Whisper error:', err);
          return corsJson({ error: 'Transcription failed' }, 500);
        }

        const data = await res.json();
        return corsJson({ text: data.text });
      }

      if (url.pathname === '/chat' && request.method === 'POST') {
        const { message, history = [] } = await request.json();

        if (!message) {
          return corsJson({ error: 'No message provided' }, 400);
        }

        // Build messages: system + recent history + current message
        const messages = [
          { role: 'system', content: SOPHIA_SYSTEM },
          ...history.slice(-20), // Last 10 exchanges
          { role: 'user', content: message },
        ];

        const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${env.GROQ_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'llama-3.3-70b-versatile',
            messages,
            temperature: 0.7,
            max_tokens: 256,
          }),
        });

        if (!res.ok) {
          const err = await res.text();
          console.error('Groq Chat error:', err);
          return corsJson({ error: 'Chat failed' }, 500);
        }

        const data = await res.json();
        return corsJson({ response: data.choices[0].message.content });
      }

      // All other routes served by static assets (index.html)
      return new Response(null, { status: 404 });
    } catch (e) {
      console.error('Worker error:', e);
      return corsJson({ error: e.message }, 500);
    }
  },
};
