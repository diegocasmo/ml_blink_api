# ML-Blink API

This document lists all the endpoints defined by the resources the ML-Bink API exposes.

## Resources:

### Users
  - Description: An API user which can log in/out of the API, create, and read resources.
  - Endpoints:
    - `POST /users`:
      - Requires authentication: no
      - Schema validation: [User](https://github.com/diegocasmo/ml_blink_api/blob/master/ml_blink_api/models/user.py#L4)

### Sessions
  - Description: Sessions are used by the ML-Blink API to authenticate users. Once a user is successfully created, these endpoints can be used to log/in out of the API.
  - Endpoints:
    - `POST /sessions`:
      - Requires authentication: no
    - `DELETE /sessions`:
      - Requires authentication: yes

### Matchings
  - Description: An ML-Blink mission matching details.
  - Endpoints:
    - `GET /matchings`:
      - Requires authentication: no
    - `POST /matchings`:
      - Requires authentication: yes
      - Schema validation: [Matching](https://github.com/diegocasmo/ml_blink_api/blob/master/ml_blink_api/models/matching.py#L4)
        - note the `user_id` attribute is automatically added by the API to the matching, since only an authenticated user can access this endpoint
