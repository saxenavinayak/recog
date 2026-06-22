# Recog Roadmap

## What This Project Is

Recog is a self-hosted identity layer for home cameras.

The first useful version should answer:

- "Did I see Johnny at the front door?"
- "Was there an unknown person at the driveway?"
- "Have I seen this same unknown person before?"

This is not trying to be Frigate, Scrypted, or a full NVR. Those systems can provide images/video. Recog should focus on identity, embeddings, clustering, events, and alerts.



1. Get the data model right.
2. Make offline image recognition work.
3. Store real events.
4. Cluster unknown people.
5. Add RTSP after the offline path is solid.
6. Add API/UI once the backend behavior makes sense.

## Phase 1: Clean Up The Database Foundation

### T-001: Remove Import-Time Table Creation

Right now `models/recog_models.py` creates tables when the file is imported. Remove that.

Done when:
- Importing models does not touch the database.
- Table creation only happens through an explicit script, command, or migration.

### T-002: Add A Simple Database Config Helper

Create one place that builds the database URL.

Done when:
- The app can read `DATABASE_URL`.
- Existing `POSTGRES_USER`, `POSTGRES_PW`, `POSTGRES_HOST`, and `POSTGRES_PORT` can still work if you want to keep them.
- Missing config gives a useful error.

### T-003: Add Alembic

Set up migrations so schema changes are tracked.

Done when:
- `uv run alembic upgrade head` works.
- There is an initial migration.
- The migration enables `pgvector`.

### T-004: Replace Prototype Models With Core Models

Replace the current prototype tables with the real first version.

Models:
- `Camera`
- `Frame`
- `FaceDetection`
- `Person`
- `PersonEmbedding`
- `RecognitionEvent`
- `Alert`

Done when:
- Each model exists in SQLAlchemy.
- A migration creates the tables.
- `Person` has many `PersonEmbedding` rows.
- `RecognitionEvent` can store `known`, `unknown`, or `uncertain`.

### T-005: Add A Tiny Seed Script

Create a script that inserts a couple of useful dev rows.

Example:
- Camera: `Front Door`
- Person: `Johnny`

Done when:
- You can run one command to seed local data.
- Running it twice does not create duplicates.

## Phase 2: Make Offline Image Recognition Work

### T-006: Create A CLI Entry Point

Add a real command surface instead of running scripts by editing files.

Example commands for now:

```bash
uv run recog --help
uv run recog person create "Johnny"
uv run recog analyze-image ./some-image.jpg
```

Done when:
- `uv run recog --help` works.
- Commands do not run face recognition at import time.

### T-007: Extract Face Detection Into A Reusable Function

Move the InsightFace logic out of `scripts/ingest_images.py`.

Create something like:

```python
analyze_image(path) -> list[DetectedFace]
```

Each detected face should include:
- bounding box
- embedding
- detection score if available

Done when:
- You can analyze one image without writing to the database.
- Bad image paths fail cleanly.

### T-008: Add `person create`

Create known people from the CLI.

Example:

```bash
uv run recog person create "Johnny"
```

Done when:
- The command creates a `Person`.
- It prints the created person id/name.
- Duplicate names are handled clearly.

### T-009: Add Reference Images For A Person

Add images that teach the system what a person looks like.

Example:

```bash
uv run recog person add-images Johnny ./photos/johnny
```

Done when:
- The command accepts a file or folder.
- It detects faces.
- It stores one `PersonEmbedding` per accepted face.
- Images with no face are skipped with a useful message.

### T-010: Store Frames And Face Detections

When an image is analyzed, store what image was analyzed and what faces were found.

Done when:
- Each analyzed image creates a `Frame`.
- Each face creates a `FaceDetection`.
- The detection stores bounding box and embedding.

### T-011: Compare One Face Against Known People

Write the matching logic.

Input:
- one face embedding
- all stored person embeddings

Output:
- best person match
- similarity score
- decision: `known`, `unknown`, or `uncertain`

Done when:
- The logic works without InsightFace or the database.
- There are tests for obvious match, obvious non-match, and uncertain match.

### T-012: Add `analyze-image`

Analyze a new image and store recognition results.

Example:

```bash
uv run recog analyze-image ./doorbell/frame.jpg
```

Done when:
- The command detects faces.
- It compares them against known people.
- It creates `RecognitionEvent` rows.
- The terminal output shows person/decision/score.

### T-013: Add Threshold Config

Make similarity thresholds configurable.

Example:
- `known_threshold = 0.75`
- `uncertain_threshold = 0.60`

Done when:
- Scores above the known threshold become `known`.
- Scores between thresholds become `uncertain`.
- Scores below the uncertain threshold become `unknown`.

## Phase 3: Cluster Unknown People

### T-014: Add Unknown Cluster Models

Add tables for recurring unknown people.

Models:
- `UnknownCluster`
- `UnknownClusterMember`

Done when:
- Unknown clusters can contain many face detections or recognition events.
- Clusters have a status like `active`, `ignored`, or `promoted`.

### T-015: Save Unknown Faces For Clustering

Make sure unknown recognition events keep enough data to cluster later.

Done when:
- Unknown events have embeddings available.
- Known people are not included in clustering by default.

### T-016: Add `unknown cluster`

Group unknown faces using HDBSCAN or DBSCAN.

Example:

```bash
uv run recog unknown cluster
```

Done when:
- Similar unknown faces get assigned to the same cluster.
- Noise/outliers do not break the command.
- Running it twice does not create duplicate memberships.

### T-017: Pick A Representative Face For Each Cluster

Choose one face image/embedding to represent each unknown cluster.

Done when:
- Each cluster has a representative detection.
- A one-member cluster still works.
- The representative is stable when inputs do not change.

### T-018: Promote Unknown Cluster To Person

Turn an unknown cluster into a known person.

Example:

```bash
uv run recog unknown promote 12 --name "Delivery Driver"
```

Done when:
- A `Person` is created.
- Cluster embeddings become `PersonEmbedding` rows.
- The cluster is marked as promoted.

### T-019: Ignore Bad Unknown Clusters

Sometimes a cluster is junk: blurry face, poster, bad detection, etc.

Done when:
- You can mark a cluster as ignored.
- Ignored clusters do not show up in future active cluster lists.

## Phase 4: Add RTSP After Offline Recognition Works

### T-020: Add Camera Commands

Create and list cameras from the CLI.

Example:

```bash
uv run recog camera create "Front Door" "rtsp://..."
uv run recog camera list
```

Done when:
- Cameras are stored in the database.
- RTSP URLs are not printed in full.
- Cameras can be enabled or disabled.

### T-021: Sample One Frame From A Camera

Write the smallest possible RTSP frame sampler.

Done when:
- Given one camera, the app can grab one frame.
- The frame is saved or passed into the existing image pipeline.
- Connection failures do not crash unclearly.

### T-022: Run Recognition On Sampled Frames

Connect RTSP sampling to the offline recognition path.

Done when:
- A sampled frame creates a `Frame`.
- Faces create `FaceDetection` rows.
- Matches create `RecognitionEvent` rows.

### T-023: Add A Simple Camera Worker

Loop over enabled cameras and sample every N seconds.

Done when:
- The worker processes enabled cameras.
- Sample interval is configurable.
- Logs show what the worker is doing.

### T-024: Suppress Duplicate Events

Avoid creating noisy events every few seconds for the same person.

Done when:
- The same person at the same camera inside a cooldown window is suppressed.
- Unknown events can also be suppressed.
- Suppressed events are either not stored or clearly marked.

## Phase 5: Add Alerts

### T-025: Create Alerts From Recognition Events

Generate alert rows from important recognition events.

Done when:
- Known person events can create alerts.
- Unknown person events can create alerts.
- Alert rows link back to recognition events.

### T-026: Add Console Alerts

Start with the simplest notifier: print/log alerts.

Example:

```text
Johnny is at Front Door.
Unknown person detected at Driveway.
```

Done when:
- Alerts are printed in a readable format.
- Sent alerts are marked as sent.

### T-027: Add Webhook Alerts

Send alerts to a configured webhook URL.

Done when:
- The webhook receives event/person/camera/score data.
- Failed requests mark the alert as failed.
- The webhook URL is configurable.

### T-028: Add Alert Cooldowns

Prevent notification spam.

Done when:
- Repeated alerts inside a cooldown window are suppressed.
- Cooldown behavior is easy to configure.

## Phase 6: Add A Small API

### T-029: Add FastAPI Skeleton

Create the smallest API app.

Done when:
- The API starts locally.
- `/health` returns OK.
- Database sessions work inside routes.

### T-030: Add People Endpoints

Endpoints:
- `POST /persons`
- `GET /persons`
- `POST /persons/{id}/images`

Done when:
- You can create/list people over HTTP.
- You can upload reference images for a person.

### T-031: Add Events Endpoint

Endpoint:
- `GET /events`

Done when:
- You can list recent recognition events.
- Events include camera, person/decision, score, and timestamp.

### T-032: Add Unknown Cluster Endpoints

Endpoints:
- `GET /unknown-clusters`
- `POST /unknown-clusters/{id}/promote`
- `POST /unknown-clusters/{id}/ignore`

Done when:
- You can review unknown clusters over HTTP.
- You can promote or ignore them.

### T-033: Add Camera Endpoints

Endpoints:
- `POST /cameras`
- `GET /cameras`

Done when:
- You can create/list cameras over HTTP.
- RTSP URLs are redacted in responses.

## Phase 7: Add A Minimal UI

### T-034: Create A Basic UI Shell

Add a small web UI with navigation.

Screens:
- People
- Events
- Unknowns
- Cameras

Done when:
- The UI runs locally.
- It can call the API.

### T-035: Build People Screen

Done when:
- You can see people.
- You can create a person.
- You can upload reference images.

### T-036: Build Events Screen

Done when:
- You can see recent recognition events.
- Known, unknown, and uncertain events are easy to distinguish.

### T-037: Build Unknowns Screen

Done when:
- You can see unknown clusters.
- You can promote a cluster to a person.
- You can ignore a bad cluster.

### T-038: Build Cameras Screen

Done when:
- You can list cameras.
- You can add a camera.
- You can enable/disable a camera.

## Phase 8: Integrations Later

### T-039: Try Frigate Snapshot Integration

Use Frigate as a source of snapshots instead of building motion detection.

Done when:
- A Frigate event can trigger image recognition.
- Sample payloads are documented.

### T-040: Try Home Assistant Alerts

Send alerts in a way Home Assistant can consume.

Done when:
- Home Assistant can receive known/unknown person events.
- There is a small example automation.

## First Real Milestone

The first serious milestone is:

> Given 10 photos of Johnny and one test image from a door camera, recog stores a recognition event saying Johnny was detected with confidence X.

That milestone requires:

- T-001 through T-013

Do not start RTSP, alerts, API, or UI until this works from the CLI.

## Suggested Build Order

1. Database cleanup: T-001 to T-005
2. Offline recognition: T-006 to T-013
3. Unknown clustering: T-014 to T-019
4. RTSP: T-020 to T-024
5. Alerts: T-025 to T-028
6. API: T-029 to T-033
7. UI: T-034 to T-038
8. Integrations: T-039 to T-040

