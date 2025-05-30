# Gradio Session



## Session Store Structure

Session Store structure:

┌──────────────────────────────┐
│    InMemorySessionStore      │
│     (self._store: dict)      │
└──────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────┐
│   session_id (str)     |         session data          │
├────────────────────────┬───────────────────────────────┤
│      "abc123"          │    {"data": {...},            |
|                        |     "username": user1         │
│                        │     "expire_at": <timestamp>} │
├────────────────────────┼───────────────────────────────┤
│      "xyz789"          │    {"data": {...},            │
|                        |     "username": user2         │
│                        │     "expire_at": <timestamp>} │
└────────────────────────┴───────────────────────────────┘

Each "data" dict inside looks like:

       data = {
           "custom1": { ... }  ← any session-specific data
           "custom2": { ... }  ← any session-specific data
       }


## Architecture with Redis

                       ┌────────────────────┐
                       │      User          │
                       └────────┬───────────┘
                                │
                      HTTP/WebSocket
                                │
                       ┌────────▼─────────┐
                       │   Load Balancer  │  ◄──── Sticky Sessions (optional)
                       └─────┬──────┬─────┘
                             │      │
                    ┌────────▼┐  ┌──▼────────┐
                    │ Gradio  │  │  Gradio   │  ◄──── Stateless (does not use in-memory gr.State)
                    │Instance │  │ Instance  │
                    └─────────┘  └───────-───┘
                          │            │
                          └────┬───────┘
                               │
                  ┌────────────▼────────────┐
                  │         Redis           │  ◄──── Stores user session/state
                  └─────────────────────────┘

                  ┌────────────┐   ┌────────────┐
                  │  Backend   │   │  Model API │  ◄──── Optional: model serving
                  └────────────┘   └────────────┘

                  ┌──────────────────────────────┐
                  │     Object Storage (S3, etc.)│  ◄──── Stores files, logs, data
                  └──────────────────────────────┘


## Architecture with Celery Task Queue

                       ┌────────────────────┐
                       │       User         │
                       └────────┬───────────┘
                                │
                          HTTP/WebSocket
                                │
                       ┌────────▼─────────┐
                       │   Load Balancer  │
                       └─────┬──────┬─────┘
                             │      │
                    ┌────────▼┐  ┌──▼────────┐
                    │ Gradio  │  │  Gradio   │  ◄──── Stateless UI
                    │Instance │  │ Instance  │
                    └────┬────┘  └────┬───-──┘
                         │            │
               Submit task to         │
                 Celery queue         │
                         ▼            ▼
                    ┌────────────────────┐
                    │     Redis (Broker) │  ◄──── Task queue broker + session store
                    └─────────┬──────────┘
                              │
                      ┌───────▼────────┐
                      │   Celery Worker│  ◄──── Background processing
                      └───────┬────────┘
                              │
                        Call model / API
                              │
                     ┌────────▼────────┐
                     │   Model Server  │
                     └─────────────────┘
                              │
                      Save result / data
                              ▼
                  ┌──────────────────────-────┐
                  │  Object Storage (e.g. S3) │
                  └─────────────────────-─────┘
