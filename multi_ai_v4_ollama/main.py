#!/usr/bin/env python3
from multi_ai_v4_ollama.orchestrator.human_loop_orchestrator import HumanLoopOrchestrator

def main():
    try:
        goal = input("🎯 Sprint hedefi: ")
    except KeyboardInterrupt:
        return
    h = HumanLoopOrchestrator()
    h.run(goal)

if __name__ == "__main__":
    main()
