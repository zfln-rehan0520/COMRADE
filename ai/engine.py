import os
import subprocess
import threading
import time

import ollama


class ComradeAI:
    def __init__(self, model_name="qwen2.5:1.5b"):
        self.model_name = model_name
        self.system_prompt = (
            "You are the COMRADE AI Core, an offline, zero-knowledge intelligence assistant "
            "integrated into a secure cyber-operations environment. Provide concise, "
            "accurate, and technically rigorous support. All operations are local-first."
        )
        self.conversation_history = []
        self._initialize_system_context()

        # Boot Ollama in the background so the caller doesn't have to wait on it.
        threading.Thread(target=self._boot_local_engine, daemon=True).start()

    def _boot_local_engine(self):
        """Checks Ollama is installed and running, and pulls the model if it's missing."""
        print("[SYSTEM]: Booting local AI inference engine...")

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        try:
            subprocess.run(["ollama", "--version"], capture_output=True, check=True, startupinfo=startupinfo)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("[SYSTEM ERROR]: Ollama binary not found. Install it from https://ollama.com")
            return

        try:
            ollama.list()
        except Exception:
            print("[SYSTEM]: Daemon offline, starting it now...")
            try:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    startupinfo=startupinfo,
                )
                time.sleep(3)
            except Exception as e:
                print(f"[SYSTEM ERROR]: Daemon failed to start -> {e}")
                return

        try:
            available = ollama.list()
            installed_models = []

            # Handle both the newer Ollama SDK's Model objects and raw dicts.
            raw_models = getattr(available, "models", available.get("models", []) if isinstance(available, dict) else [])

            for m in raw_models:
                if isinstance(m, dict):
                    name = m.get("model") or m.get("name")
                else:
                    name = getattr(m, "model", getattr(m, "name", None))
                if name:
                    installed_models.append(str(name))

            if self.model_name not in installed_models and f"{self.model_name}:latest" not in installed_models:
                print(f"[SYSTEM]: Model '{self.model_name}' missing, pulling now...")
                subprocess.run(["ollama", "pull", self.model_name], capture_output=True, startupinfo=startupinfo)
                print(f"[SYSTEM]: Model '{self.model_name}' ready.")
            else:
                print("[SYSTEM]: AI engine ready.")
        except Exception as e:
            print(f"[SYSTEM ERROR]: Model check failed -> {e}")

    def _initialize_system_context(self):
        self.conversation_history.append({"role": "system", "content": self.system_prompt})

    def ask(self, prompt, system_context=None):
        if system_context:
            self.conversation_history[0]["content"] = system_context

        self.conversation_history.append({"role": "user", "content": prompt})

        try:
            return self._standard_reply()
        except Exception:
            self.conversation_history.pop()  # keep the history consistent after a failed call
            return (
                "[AI Engine Error]: Connection refused.\n\n"
                "If this is your first time booting, the system is likely still downloading "
                f"the model '{self.model_name}' in the background. Please wait a moment and try again."
            )

    def _standard_reply(self):
        response = ollama.chat(model=self.model_name, messages=self.conversation_history)

        if isinstance(response, dict):
            reply = response["message"]["content"]
        else:
            reply = response.message.content

        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def wipe_memory(self):
        self.conversation_history = []
        self._initialize_system_context()
