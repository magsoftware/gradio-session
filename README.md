# Gradio Session



## Architecture

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
