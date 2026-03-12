```
 Flow

 Browser (login page)          IdP Backend              Mobile App
 / Demo Click
     |                            |                            |
     |-- GET /authorize --------->|                            |
     |                            |-- create challenge in DB   |
     |<-- HTML with QR code ------|                            |
     |                            |                            |
     |-- poll GET /challenge/{id}/status -->|                  |
     |<-- {"status": "pending"} --|                            |
     |                            |                            |
     |   [User clicks QR / mobile app scans]                   |
     |                            |<-- POST /challenge/{id}/submit
     |                            |    (signed_challenge + cert OR
 demo mode)
     |                            |-- verify → create auth code|
     |                            |-- mark challenge completed |
     |                            |                            |
     |-- poll GET /challenge/{id}/status -->|                  |
     |<-- {"status":"completed", "redirect_url":"..."}         |
     |                            |                            |
     |-- browser redirects to redirect_uri?code=...&state=...  |

 Demo mode: Clicking the QR code POSTs to
 /challenge/{id}/demo-submit (no signature/cert needed). The user
 is identified by login_hint stored on the challenge.
 ```