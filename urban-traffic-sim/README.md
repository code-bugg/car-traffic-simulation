# Chișinău Urban Traffic Simulation

A SUMO-based microscopic traffic simulation of the Chișinău municipality,
featuring adaptive traffic lights, realistic vehicle types, runtime vehicle
spawning from real OSM road data, and per-step statistics collection.

---

## Quick start

### 1. Install SUMO (system-level)

```bash
# Ubuntu / Debian
sudo apt install sumo sumo-tools sumo-doc

# macOS (Homebrew)
brew install sumo

# Windows → https://sumo.dlr.de/docs/Downloads.php
```

Set the environment variable (add to `.bashrc` / `.zshrc`):

```bash
export SUMO_HOME=/usr/share/sumo          # Linux
export SUMO_HOME=/opt/homebrew/share/sumo # macOS
```

### 2. Set up the Python environment

**Linux / macOS:**
```bash
bash setup.sh
```

**Windows:**
```bat
setup.bat
```

This creates a virtual environment at `./venv`, upgrades pip, installs all
dependencies from `requirements.txt`, and checks whether SUMO is configured.

To **recreate** the environment from scratch:
```bash
bash setup.sh --rebuild    # Linux / macOS
setup.bat --rebuild        # Windows
```

### 3. Activate the virtual environment

Every new terminal session requires activating the environment:

```bash
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 4. Download and convert the Chișinău road network

```bash
python scripts/prepare_map.py
```

Downloads the OpenStreetMap bounding box for Chișinău, converts it with
`netconvert`, and generates vehicle routes. Run this once — results are
saved to `maps/` (excluded from git by `.gitignore`).

### 5. Run the simulation

```bash
python main.py                  # headless, 2-hour sim
python main.py --gui            # open SUMO-GUI
python main.py --steps 500      # quick test run
python main.py --debug          # verbose logging
pytest tests/                   # run all tests
```

Results are written to `data/output/` (CSV + PNG charts).

> **Important:** SUMO-GUI opens *paused*. Click the green **▶ Play** button in
> the top toolbar to actually start the simulation.

---

## Windows walkthrough (PowerShell, step-by-step)

If you're on Windows and running this for the first time, follow these exact
steps. Run each block in PowerShell and wait for it to finish before pasting
the next.

### 1. Install SUMO

1. Open https://sumo.dlr.de/docs/Downloads.php
2. Download the **64-bit Windows installer** (`sumo-win64-*.msi`).
3. Run the installer and keep all defaults — it installs to
   `C:\Program Files (x86)\Eclipse\Sumo`.

Verify in a **new** PowerShell window:

```powershell
netconvert --version
```

If it prints a version banner → SUMO is on PATH. If not, set the environment
variables manually (run once, then close and reopen PowerShell):

```powershell
[Environment]::SetEnvironmentVariable("SUMO_HOME", "C:\Program Files (x86)\Eclipse\Sumo", "User")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;C:\Program Files (x86)\Eclipse\Sumo\bin", "User")
```

### 2. Go to the project folder

```powershell
cd "C:\Users\<YOU>\path\to\car-traffic-simulation\urban-traffic-sim"
```

`main.py` must be visible here — `ls main.py` should succeed. If you're one
level up (in `car-traffic-simulation`), `cd` into `urban-traffic-sim` first.

### 3. Create the virtual environment (first time only)

```powershell
python -m venv venv
```

If PowerShell blocks script execution later, run **once**:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 4. Activate the virtual environment

Every new PowerShell session:

```powershell
.\venv\Scripts\Activate.ps1
```

Your prompt should now start with `(venv)`.

### 5. Install Python dependencies (first time only)

```powershell
pip install -r requirements.txt
```

### 6. Build the map (first time only)

```powershell
python scripts\prepare_map.py
```

Downloads OSM data for the Chișinău city centre, runs `netconvert`, and
generates routes. Takes 1–3 minutes. You should end with:
`Map preparation complete. You can now run: python main.py`

If you see `406 Client Error` from Overpass, the bbox is too large — shrink
it in `config/simulation.yaml` under `city.bbox` and try again.

### 7. Run the simulation

```powershell
python main.py --gui --steps 500
```

The SUMO-GUI window opens **paused**. Click the green ▶ Play button at the
top to start. Vehicles will not despawn — when they reach a destination they
loop to a new one, and if they get blocked they are rerouted.

### 8. Edit the road network (optional)

```powershell
python main.py --edit                 # opens NETEDIT on the network
# edit in NETEDIT, Ctrl+S, close the window
python scripts\regenerate_routes.py   # rebuild routes against the edited net
python main.py --gui --steps 500      # run the updated simulation
```

### Every future PowerShell session

```powershell
cd "C:\Users\<YOU>\path\to\car-traffic-simulation\urban-traffic-sim"
.\venv\Scripts\Activate.ps1
python main.py --gui --steps 500
```

---

## Editing the road network (NETEDIT walkthrough)

The network (`maps/chisinau.net.xml`) is modified graphically with SUMO's
bundled **NETEDIT** tool — add, delete or reshape edges, junctions, lanes,
connections and traffic lights.

### 1. Open the editor

From `urban-traffic-sim/` with venv active:

```powershell
python main.py --edit
```

If NETEDIT doesn't launch, check `$env:SUMO_HOME` is set and
`%SUMO_HOME%\bin\netedit.exe` exists.

### 2. Basic NETEDIT controls

Top-left mode dropdown — switch between:

| Key | Mode | Use |
|-----|------|-----|
| **E** | Edge | Click two points to draw a new road |
| **N** | Junction (node) | Click to add/move intersections |
| **C** | Connection | Edit which lane connects to which at a junction |
| **T** | Traffic-light | Add/edit a TLS on a junction |
| **I** | Inspect | Click anything to view/edit its attributes |
| **D** | Delete | Click anything to delete |
| **M** | Move | Drag nodes or reshape edge geometry |

Camera: scroll wheel to zoom, right-drag to pan.

### 3. Add a new road

1. Click **E** (Edge mode).
2. On the toolbar below, tick **"chain"** for several segments in one go,
   and **"two-way"** for a road in both directions.
3. Click the start junction, then the end junction.
4. **Snap to existing junctions** so the new road actually links to the rest
   of the network. Clicking empty space creates an isolated junction.

### 4. Edit a road

1. Click **I** (Inspect mode), then click the edge.
2. Right panel shows attributes: `speed`, `numLanes`, `priority`,
   `allow/disallow`, etc. Changes apply immediately.
3. To reshape, use **M** (Move) and drag geometry points; Shift-click an edge
   to add a bend.

### 5. Delete a road

1. Click **D** (Delete mode).
2. Click the edge or junction. Dangling junctions are cleaned up
   automatically.

### 6. Fix connections at a junction

Adding or deleting edges at a junction can leave stale lane-to-lane
connections (cars won't know how to cross).

- Click **C** (Connection mode), then click the junction. Incoming lanes
  turn colored — click an incoming lane then an outgoing lane to create a
  turn.
- Easier for most cases: menu **Processing → Recompute junctions** (**F5**)
  rebuilds connections for everything you changed.

### 7. Save

**Ctrl + S** overwrites `maps/chisinau.net.xml`.

### 8. Rebuild routes and run

Old routes may reference edges you deleted, so rebuild them:

```powershell
python scripts\regenerate_routes.py
python main.py --gui --steps 500
```

The spawner validates reachability, so a disconnected island just means no
cars spawn there — they won't vanish mid-road.

### Common pitfalls

- **Edge has no traffic**: no route passes through it yet. Increase
  `traffic.batch_size` in `config/simulation.yaml` or wait — `randomTrips`
  only samples a subset.
- **New edge ignored**: press **F5** (Recompute) after big changes.
- **Cars stuck at the new junction**: open Connection mode (**C**) on that
  junction and confirm incoming→outgoing lane arrows exist.

---

## Project structure

```
chisinau-traffic-sim/
├── setup.sh                     # Linux/macOS environment setup
├── setup.bat                    # Windows environment setup
├── requirements.txt
├── config/
│   └── simulation.yaml          # All tunable parameters
├── maps/                        # Generated by prepare_map.py (git-ignored)
│   ├── chisinau.net.xml
│   ├── chisinau.rou.xml
│   └── chisinau.poly.xml
├── scripts/
│   └── prepare_map.py           # OSM download + netconvert pipeline
├── src/
│   ├── agents/
│   │   ├── vehicle.py           # VehicleAgent — TraCI wrapper per vehicle
│   │   └── spawner.py           # VehicleSpawner — runtime vehicle injection
│   ├── network/
│   │   └── road_network.py      # RoadNetwork — sumolib wrapper
│   ├── traffic_control/
│   │   ├── traffic_light.py     # TrafficLightController — per-junction
│   │   └── adaptive_controller.py
│   ├── simulation/
│   │   ├── runner.py            # SimulationRunner — main orchestrator
│   │   ├── statistics.py        # StatisticsCollector — per-step KPIs
│   │   └── vehicle_type_loader.py
│   ├── visualization/
│   │   └── stats_plotter.py     # StatsPlotter — matplotlib dashboard
│   └── utils/
│       ├── config.py
│       └── logger.py
├── tests/
│   ├── unit/
│   └── integration/
└── data/
    ├── output/                  # Generated: statistics.csv + charts
    └── logs/                    # Generated: simulation.log
```

---

## Output

After a run, `data/output/` contains:

| File | Description |
|---|---|
| `statistics.csv` | Per-interval metrics (speed, wait, count, CO₂, fuel) |
| `dashboard.png` | 6-panel overview chart |
| `mean_speed.png` | Average vehicle speed over time |
| `waiting_time.png` | Average junction waiting time |
| `vehicle_count.png` | Active vehicles over time |
| `emissions.png` | CO₂ and fuel consumption |

---

## Configuration

All parameters live in `config/simulation.yaml`:

| Key | Default | Description |
|---|---|---|
| `simulation.total_steps` | 7200 | Steps to run (1 step = 1 second) |
| `sumo.binary` | `sumo` | Use `sumo-gui` for visual mode |
| `traffic.spawn_interval` | 10 | Steps between vehicle batches |
| `traffic.batch_size` | 5 | Vehicles per batch |
| `traffic_lights.adaptive` | `true` | Enable adaptive green extension |
| `traffic_lights.congestion_threshold` | 8 | Vehicles waiting to trigger extension |

---

## Team conventions

- One class per module, snake_case filenames.
- All TraCI calls go through `src/agents/` or `src/traffic_control/` — never inline in the runner.
- Every new class must have a unit test using `unittest.mock` to stub TraCI.
- Run `pytest tests/` before committing.
