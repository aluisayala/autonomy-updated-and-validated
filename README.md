# ZPE-1 Cognitive Simulation System

This repository contains the ZPE-1 autonomous cognitive simulation environment driven by the Autonomy Control Key (Ω equation).

## Overview

- Simulates multiple autonomous agents with individual personalities and memories.
- Uses the Ω equation `(state + bias) * alpha` to govern decision-making and cognitive state.
- Supports web search integration via SerpAPI to enrich agent knowledge.
- Handles drift events where agents reboot and reflect on system snapshots.
- Maintains shared facts and memory negotiation between agents.
- Includes commands for interaction: talking to agents, advancing time, recalling memory, and saving snapshots.

## Usage

1. Install required packages:

```
pip install -r requirements.txt
```

2. Run the simulation:

```
python zpe1_sim.py
```

3. Use commands such as:

- `talk to [agent]: [message]` — Interact with an agent.
- `advance [number]` — Advance simulation ticks.
- `print shared` — Show shared facts.
- `save snapshot` — Save current state to JSON.
- `recall all` — Print all agents' memories.
- `exit` — Quit simulation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Luis Ayala  
GitHub: https://github.com/aluisayala/autonomy-control
