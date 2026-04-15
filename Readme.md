# Reputation GNN

A sample project for **bot detection in a social network graph** stored in **Neo4j**, trained with **Graph Neural Networks (GNNs)**, and exposed through a **FastAPI REST API**.

## Overview

This repository is split into three main packages:

- **Ingest**: generates and ingests synthetic data into Neo4j, simulating an Instagram-like social network.
- **Brain**: builds the training graph and trains GNN models for account classification.
- **API**: exposes CRUD operations over the graph and provides a prediction endpoint to infer whether an account is a bot or a person.

The project also includes:

- **Redis** for caching entities and predictions.
- **Docker Compose** to run infrastructure and batch jobs.
- **Model artifact persistence** through a shared volume, decoupling training from serving.

---

## Architecture

```text
Neo4j  <----  Ingest
  ^
  |           Brain (train / test)
  |                |
  |                v
  +---------- API + Redis
                    |
                    v
         entity and prediction cache
```

### General flow

1. **Ingest** generates synthetic accounts, follow relationships, and attributes such as `posts`, `verified`, and `user_type`.
2. The data is stored in **Neo4j**.
3. **Brain** extracts the graph from Neo4j, transforms it into `torch-geometric` format, and trains a GNN.
4. The trained model is stored as a **model artifact** (`model.pt` + `metadata.json`) in a shared directory.
5. **API** loads that artifact, exposes CRUD endpoints, and supports inference for new accounts.
6. **Redis** caches entity reads and predictions to reduce repeated access and recomputation.

---

## Project structure

```text
src/
  app/       # REST API, services, Redis cache, endpoints and schemas
  brain/     # training, testing, graph loaders and trainers
  core/      # domain, persistence, ML, graph, settings and logging
  ingest/    # synthetic data simulation and ingestion into Neo4j

deployment/
  Dockerfiles for api, ingest, train and test

docker-compose.yaml
pyproject.toml
```

### Packages

#### `src/ingest`
Responsible for generating and ingesting a synthetic social network into Neo4j.

Main responsibilities:
- create accounts with different profiles (`BOT`, `PERSON`, `INFLUENCER`)
- generate post counts
- decide whether an account is verified
- generate `followers` / `following` relationships
- persist everything into Neo4j

Main script:

```bash
ingest-data
```

#### `src/brain`
Responsible for training and evaluating GNN models.

Main responsibilities:
- read people and relationships from Neo4j
- build training, validation, and test graphs
- train different GNN models
- apply early stopping
- save the model as a reusable artifact
- evaluate accuracy on a test subgraph

The training package currently supports two model architectures controlled by `BRAIN_MODEL_NAME`:
- `gcn` → trains a **GCN** model
- `sage` → trains a **GraphSAGE** model

It also supports two training strategies controlled by `BRAIN_TYPE_TRAINER`:
- `full` → trains on the full graph
- `sampling` → trains using neighborhood sampling

Main scripts:

```bash
train-model
test-model
```

#### `src/app`
Responsible for exposing the business functionality through FastAPI.

Main responsibilities:
- CRUD operations over graph entities
- prediction of a person type from attributes and relationships
- health checks
- caching entities and predictions in Redis
- hot-reload / model switching

---

## Domain

The main domain entity is a person in the social network.

### `Person`
Base attributes:
- `name`
- `user_type`
- `posts`
- `n_followers`
- `n_following`
- `verified`

### `PersonWithRelations`
Extends `Person` with:
- `followers`
- `following`

### `PersonPredict`
Inference result:
- `name`
- `user_type`
- `confidence`

---

## Persistence

### Neo4j
Neo4j is the main database in the system.

It is used to:
- store people
- store follow relationships
- retrieve subgraphs for training
- serve CRUD queries

### Redis
Redis is used as a cache for:
- frequently accessed people
- repeated predictions for the same input

The prediction hash is built from:
- the person's attributes
- followers' attributes
- following's attributes

This avoids recomputing identical predictions.

---

## Machine Learning

### Features
The current node features are:

- `n_followers`
- `n_following`
- `posts`
- `verified`

These features are transformed into tensors for `torch-geometric`.

### Labels
The final classification served by the API is **bot vs person**.

Although the domain includes `INFLUENCER`, the current training output is configured with `output_channels = 2`, so the current classification pipeline is set up as a binary problem.

### Model artifact
The model is stored as an artifact on disk with two files:

```text
/artifacts/
  model.pt
  metadata.json
```

`metadata.json` stores at least:
- `model_name`
- `input_dim`
- `hidden_dim`
- `output_dim`

This allows reconstructing the model without relying on duplicated runtime configuration.

---

## REST API

The FastAPI application is mounted under:

```text
/api
```

And the main versioned routes are under:

```text
/api/v1
```

### Health

```http
GET /api/health/
```

Returns the status of:
- Redis
- Neo4j
- loaded model

### People

#### Create a person

```http
POST /api/v1/person/
```

#### List people

```http
GET /api/v1/person/?offset=0&limit=20&type_person=BOT
```

#### Get person by name

```http
GET /api/v1/person/{name}
```

#### Update person

```http
PATCH /api/v1/person/{name}
```

#### Delete person

```http
DELETE /api/v1/person/{name}
```

### Prediction

#### Predict person type

```http
POST /api/v1/predict
```

#### Change the loaded model

```http
POST /api/v1/predict/change_model
```

This allows the API to reload a new model artifact without rebuilding the image.

---

## Configuration

The project uses `pydantic-settings` and environment variables.

### Shared variables

#### Neo4j
```env
URI_NEO4J=bolt://neo4j:password@neo4j:7687
```

#### Logging
```env
APP_NAME=bot_detector
```

### API
```env
APP_HOST_REDIS=redis
APP_PORT_REDIS=6379
APP_DB_REDIS=0
APP_MODEL_PATH=/artifacts
```

### Training
```env
BRAIN_MODEL_NAME=sage
BRAIN_MODEL_PATH=/artifacts
BRAIN_HIDDEN_CHANNELS=32
BRAIN_NUM_FEATURES=4
BRAIN_OUT_CHANNELS=2
BRAIN_EPOCHS=400
BRAIN_LEARNING_RATE=0.01
BRAIN_RATIO_VALIDATION=0.2
BRAIN_RATIO_TEST=0.1
BRAIN_NUM_NEIGHBORS=[25,15]
BRAIN_BATCH_SIZE=128
BRAIN_TYPE_TRAINER=sampling
BRAIN_EARLY_STOPPING_PATIENCE=10
BRAIN_EARLY_STOPPING_DELTA=0.001
```

#### Training options

`BRAIN_MODEL_NAME` selects the model architecture:
- `gcn` → Graph Convolutional Network (GCN)
- `sage` → GraphSAGE

`BRAIN_TYPE_TRAINER` selects the training strategy:
- `full` → full-graph training
- `sampling` → mini-batch training with neighborhood sampling

### Ingest
```env
INGEST_N_ACCOUNTS=100
INGEST_P_BOTS=0.3
INGEST_P_INFLUENCERS=0.2
INGEST_MEAN_POSTS=400
INGEST_MAX_POSTS_INFLUENCERS=1500
INGEST_MEAN_POSTS_BOTS=15
INGEST_PERCENTAGE_VERIFIED_PERSON=0.3
```

---

## Local installation

### Requirements

- Python **3.13+**
- `uv`
- Docker and Docker Compose
- Neo4j
- Redis

### Install dependencies

Base dependencies:

```bash
uv sync --frozen
```

API:

```bash
uv sync --extra api --frozen
```

Ingest:

```bash
uv sync --extra ingest --frozen
```

Training:

```bash
uv sync --extra train --frozen
```

> For training with `NeighborSampler`, the training container installs `pyg-lib` explicitly. When running locally, you may need to install the proper `pyg-lib` wheel for your PyTorch version.

---

## Running with Docker Compose

### Start infrastructure and API

```bash
docker compose up -d neo4j redis api
```

### Run ingestion

```bash
docker compose run --rm ingest
```

### Train a model

```bash
docker compose run --rm train-model
```

### Test a model

```bash
docker compose run --rm test-model
```

---

## Artifact volume

The trained model is stored in the shared volume:

```yaml
volumes:
  model_artifacts:
```

- `train-model` writes to `/artifacts`
- `api` mounts `/artifacts` as read-only
- `test-model` can read the same artifact

This prevents coupling the training image to the API runtime image.

---

## Available scripts

Defined in `pyproject.toml`:

```toml
[project.scripts]
ingest-data = "ingest.main:main"
train-model = "brain.main:train"
test-model = "brain.main:test"
```

---

## Usage examples

### Create a person

```bash
curl -X POST http://localhost/api/v1/person/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "alice",
    "user_type": "PERSON",
    "posts": 123,
    "verified": false,
    "followers": [],
    "following": []
  }'
```

### Predict whether a person is a bot or a person

```bash
curl -X POST http://localhost/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "name": "candidate_1",
    "user_type": "PERSON",
    "posts": 40,
    "n_followers": 500,
    "n_following": 300,
    "verified": false,
    "followers": [],
    "following": [],
    "followers_db": [],
    "following_db": []
  }'
```

---

## Current strengths

- Clear separation between ingestion, training, and serving.
- Graph persistence with Neo4j.
- Redis-based caching for reads and predictions.
- Training decoupled through Docker Compose jobs.
- Model persistence as a reusable artifact.
- Runtime model reload from the API.

---

## Recommended improvements

- Document the exact label contract used by the model.
- Version model artifacts (`/artifacts/current`, `/artifacts/runs/...`).
- Split health, readiness, and capabilities.
- Add automated tests for API, repositories, and ML pipeline.
- Add evaluation metrics beyond accuracy.
- Normalize and document environment variables more consistently.

---

## Project status

The project is a solid functional prototype for:

- synthetic social graph generation,
- GNN-based classification,
- graph CRUD and prediction serving.

It is a strong base to evolve into a more production-ready system with:
- model versioning,
- better evaluation metrics,
- observability,
- automated tests,
- more robust deployment.

