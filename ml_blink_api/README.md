# ML-Blink API

This document lists all the endpoints defined by the resources the ML-Bink API exposes.

## Resources:

### Users
  - Description: A user who can log in/out of the API, create, and read resources from it.
  - Endpoints:
    - `POST /users`: create a user
      - Requires authentication: no
      - Schema validation: [User](https://github.com/diegocasmo/ml_blink_api/blob/master/ml_blink_api/models/user.py)
        - Note: As of now, the API only supports creating a single user, which must have the same email as the `TEMP_TEST_USER_EMAIL` environmental variable.

### Missions
  - Description: An ML-Blink mission details.
  - Endpoints:
    - `GET /missions`: get all missions
      - Requires authentication: no
    - `POST /missions`: create a mission
      - Requires authentication: no
      - Schema validation: [Mission](https://github.com/diegocasmo/ml_blink_api/blob/master/ml_blink_api/models/mission.py)
        - Note: the `user_id` attribute is automatically added by the API to the mission. The `user_id` will for now always be equal to the temporary test user `_id`.

### Sessions (temporarily disabled until the sign up/in features are implemented in ML-Blink UI)
  - Description: Sessions are used by the ML-Blink API to authenticate users. Once a user is successfully created, these endpoints can be used to sign in/out of the API.
  - Endpoints:
    - `POST /sessions`: create a session
      - Requires authentication: no
    - `DELETE /sessions`: delete a session
      - Requires authentication: yes
