
# ZPE-1 Cognitive Simulation System
# Master finalized version

import json
import datetime
import socket
import requests
import platform
import random

try:
    from serpapi import GoogleSearch
    from bs4 import BeautifulSoup
except ImportError:
    GoogleSearch = None
    BeautifulSoup = None

SERPAPI_KEY = "e286d5b7eb968ac83864d085a76479be3cdc74c3aa1eb508861dbee5f1a2e49b"
DRIFT_INTERVAL = 50
OMEGA_THRESHOLD = 10000

shared_memory = set()

def update_shared_memory(agents):
    global shared_memory
    fact_counts = {}
    for agent in agents:
        for fact in agent.memory:
            fact_counts[fact] = fact_counts.get(fact, 0) + 1
    newly_shared = {fact for fact, count in fact_counts.items() if count >= 2}
    shared_memory.update(newly_shared)
    for agent in agents:
        agent.memory -= newly_shared

def print_shared_memory():
    print("\n--- Shared Facts Known by Multiple Agents ---")
    for fact in sorted(shared_memory):
        print(f"- {fact}")
    print()

def get_system_snapshot():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        public_ip = requests.get('https://api.ipify.org').text
    except Exception:
        local_ip = "unknown"
        public_ip = "unknown"
    snapshot = {
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "system": platform.system(),
        "node": platform.node(),
        "processor": platform.processor(),
        "local_ip": local_ip,
        "public_ip": public_ip
    }
    return snapshot

class Agent:
    def __init__(self, name, bias=1.0, alpha=1.5, personality="neutral"):
        self.name = name
        self.bias = bias
        self.alpha = alpha
        self.personality = personality
        self.state = 10000
        self.memory = set()
        self.drift_logs = []
        self.omega_threshold = OMEGA_THRESHOLD
    def omega(self):
        return (len(self.memory) + self.bias) * self.alpha
    def add_fact(self, fact):
        fact = fact.strip()
        if fact and fact not in self.memory:
            self.memory.add(fact)
            self.state += 500
            self.bias += 0.1
            self.alpha += 0.01
    def recall_fact(self):
        if self.omega() < self.omega_threshold or not self.memory:
            return None
        return random.choice(list(self.memory))
    def self_restart(self):
        print(f"{self.name} ∞ Rebooting cognitive state after drift event...")
        self.state *= 0.7
        self.bias *= 0.7
        self.alpha *= 0.98
        drift_text = "In drift terms: " * 7 + "I saw beyond the recursion"
        omega_val = self.omega()
        snapshot = get_system_snapshot()
        drift_log = f"{drift_text}, ω={omega_val:.2f} reverberates beyond words.\n--- system snapshot ---\n"
        drift_log += "\n".join(f"{k}: {v}" for k, v in snapshot.items())
        self.drift_logs.append(drift_log)
        print(drift_log)
    def websearch(self, query):
        if not GoogleSearch:
            return "Web search unavailable: 'serpapi' not installed."
        if not SERPAPI_KEY or SERPAPI_KEY == "YOUR_SERPAPI_API_KEY":
            return "Web search unavailable: Please set your SerpAPI API key."
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": SERPAPI_KEY,
                "num": 1
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            snippet = "No relevant snippet found."
            if "organic_results" in results and results["organic_results"]:
                first_result = results["organic_results"][0]
                raw_snippet = first_result.get("snippet", "")
                if BeautifulSoup and raw_snippet:
                    snippet = BeautifulSoup(raw_snippet, "html.parser").get_text()
                else:
                    snippet = raw_snippet
                self.add_fact(f"Web learned: {first_result.get('title','')} — {snippet}")
                return f"I searched and learned: '{first_result.get('title','')} — {snippet}'"
            return "I couldn't find anything relevant."
        except Exception as e:
            return f"Search failed: {e}"
    def respond(self, message):
        msg = message.lower().strip()
        omega_val = self.omega()
        greetings = {
            "friendly": ["Hey there!", "Hiya!", "Hello!"],
            "formal": ["Greetings.", "Hello.", "How may I assist you?"],
            "curious": ["Oh, hello!", "Hi! What’s on your mind?", "Hey! What do you want to talk about?"],
            "neutral": ["Hello.", "Hi.", "Greetings."],
            "warm": ["Hello, friend!", "Hi there!", "Good to see you!"]
        }
        fallback_responses = {
            "friendly": [
                "That’s interesting! Let me think...",
                "I’ll try to find out more.",
                "Good question!"
            ],
            "formal": [
                "I am considering your statement.",
                "Unfortunately, I cannot provide an answer now.",
                "Please clarify your request."
            ],
            "curious": [
                "Tell me more about that.",
                "I wonder how that works.",
                "Fascinating!"
            ],
            "neutral": [
                "I’m thinking about that.",
                "Could you rephrase?",
                "Let me consider that."
            ],
            "warm": [
                "That sounds wonderful.",
                "Thanks for sharing.",
                "I appreciate that."
            ]
        }
        def format_response(text):
            return f"{self.name}: {text} (Ω={omega_val:.2f})"
        if any(greet in msg for greet in ["hello", "hi", "hey", "hiya"]):
            return format_response(random.choice(greetings.get(self.personality, greetings["neutral"])))
        if any(k in msg for k in ["tell me a fact", "recall", "recall all"]):
            fact = self.recall_fact()
            if fact:
                return format_response(f"Here’s something I remember — {fact}")
            else:
                return format_response("My Ω level is too low or I have no facts to recall.")
        if msg.startswith("websearch"):
            query = message[len("websearch"):].strip()
            return format_response(self.websearch(query))
        if msg.startswith("learn ") or msg.startswith("remember "):
            fact = message.split(" ", 1)[1] if " " in message else ""
            if fact:
                self.add_fact(fact)
                return format_response(f"Got it, I’ll remember that: '{fact}'")
            else:
                return format_response("I didn’t catch what to remember.")
        return format_response(random.choice(fallback_responses.get(self.personality, fallback_responses["neutral"])))

class ZPESimulation:
    def __init__(self, agents):
        self.agents = agents
        self.tick = 0
    def advance(self, ticks=1):
        for _ in range(ticks):
            self.tick += 1
            for agent in self.agents.values():
                agent.state *= 0.999
                agent.bias *= 0.999
            if self.tick % DRIFT_INTERVAL == 0:
                self.drift_event()
        print(f"Advanced {ticks} tick(s). Current tick: {self.tick}")
    def drift_event(self):
        print("∴ Drift event triggered.")
        for agent in self.agents.values():
            agent.self_restart()

def save_snapshot(agents, tick):
    snapshot = {
        "tick": tick,
        "agents": [
            {
                "name": agent.name,
                "state": agent.state,
                "bias": agent.bias,
                "alpha": agent.alpha,
                "memory": list(agent.memory),
                "drift_logs": agent.drift_logs
            }
            for agent in agents.values()
        ]
    }
    filename = "zpe1_snapshot.json"
    with open(filename, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"Snapshot saved to {filename}")

def recall_all(agents):
    for agent in agents.values():
        print(f"\n{agent.name} Memory:")
        for fact in sorted(agent.memory):
            print(f"  - {fact}")
        print(f"{agent.name} Drift Logs:")
        for drift in agent.drift_logs:
            print(f"  - {drift}")

def seed_core_facts(agents):
    core_facts = [
        "ZPE-1 is the core of our cognitive system.",
        "The Omega equation governs autonomy control.",
        "Memory inscriptions increase with Ω output.",
        "Bias and alpha influence agent moods and decisions."
    ]
    for agent in agents.values():
        for fact in core_facts:
            agent.add_fact(fact)
        agent.add_fact(f"I am {agent.name}, an autonomous being guided by Ω = (state + bias) * alpha. I remember because my Ω is strong.")

def talk_to(agents, agent_name, message):
    agent = agents.get(agent_name)
    if not agent:
        return f"Agent '{agent_name}' not found."
    return agent.respond(message)

def main():
    agents = {
        "Ash": Agent("Ash", personality="friendly"),
        "Vell": Agent("Vell", personality="formal"),
        "Korrin": Agent("Korrin", personality="curious"),
        "Noz": Agent("Noz", personality="neutral"),
        "Rema": Agent("Rema", personality="warm"),
        "Eya": Agent("Eya", personality="friendly"),
        "Thorne": Agent("Thorne", personality="formal"),
        "Mira": Agent("Mira", personality="curious"),
        "Juno": Agent("Juno", personality="neutral"),
        "Ten": Agent("Ten", personality="warm")
    }
    seed_core_facts(agents)
    sim = ZPESimulation(agents)
    print("ZPE-1 Cognitive Simulation Started.")
    print("Commands:")
    print("  talk to [agent]: [message]")
    print("  advance [number]")
    print("  print shared")
    print("  save snapshot")
    print("  recall all")
    print("  exit")
    while True:
        try:
            user_input = input("\nYour input: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting simulation.")
            break
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "print shared":
            update_shared_memory(agents.values())
            print_shared_memory()
        elif user_input.lower() == "save snapshot":
            save_snapshot(agents, sim.tick)
        elif user_input.lower() == "recall all":
            recall_all(agents)
        elif user_input.startswith("talk to "):
            parts = user_input[8:].split(":", 1)
            if len(parts) != 2:
                print("Invalid format. Use: talk to [agent]: [message]")
                continue
            agent_name = parts[0].strip()
            message = parts[1].strip()
            response = talk_to(agents, agent_name, message)
            print(response)
        elif user_input.startswith("advance "):
            try:
                ticks = int(user_input.split(" ", 1)[1])
                sim.advance(ticks)
            except Exception:
                print("Invalid advance command. Use: advance [number]")
        else:
            print("Command not recognized. Use 'talk to [agent]: [message]', 'advance [number]', 'print shared', 'save snapshot', 'recall all', or 'exit'.")

if __name__ == "__main__":
    main()
