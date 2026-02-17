import subprocess
import os
import threading
import sys
import uuid

class CodeRunner:
    def __init__(self, socket_io):
        self.socketio = socket_io
        self.active_processes = {}
        self.base_temp_dir = os.path.join(os.getcwd(), 'temp_exec')
        if not os.path.exists(self.base_temp_dir):
            os.makedirs(self.base_temp_dir)

    def run_code(self, session_id, language, code):
        print("[RUNNER] Request received")
        session_id = str(session_id)
        print(f"[RUNNER] Language selected: {language}")
        run_id = str(uuid.uuid4())[:8]
        session_dir = os.path.join(self.base_temp_dir, f"{session_id}_{run_id}")
        os.makedirs(session_dir, exist_ok=True)

        lang_lower = language.lower()
        if lang_lower in ['html', 'html5', 'htm', 'css', 'javascript (web)', 'jsp']:
            self.socketio.emit('render_html', {'content': code}, room=session_id)
            return

        filename, compile_cmd, run_cmd = self._get_commands(language)
        
        if not filename:
            self.socketio.emit('code_output', {'output': f"Error: Language '{language}' is not supported yet.\n"}, room=session_id)
            self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
            return

        file_path = os.path.join(session_dir, filename)
        print(f"[RUNNER] Writing file: {file_path}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
             self.socketio.emit('code_output', {'output': f"Error writing file: {e}\n"}, room=session_id)
             self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
             return

        # Compilation
        if compile_cmd:
            print(f"[RUNNER] Compile command: {compile_cmd}")
            try:
                result = subprocess.run(
                    compile_cmd,
                    cwd=session_dir,
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=5  # Timeout for compilation
                )
                print(f"[RUNNER] Compilation return code: {result.returncode}")
                if result.returncode != 0:
                    print(f"[RUNNER] Compilation Failed: {result.stderr}")
                    self.socketio.emit(
                        'code_output',
                        {'output': f"Compilation Error:\n{result.stderr}\n{result.stdout}\n"},
                        room=session_id
                    )
                    self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
                    return
            except subprocess.TimeoutExpired:
                print("[RUNNER] Compilation Timed Out")
                self.socketio.emit(
                    'code_output',
                    {'output': "Error: Compilation timed out.\n"},
                    room=session_id
                )
                self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
                return
            except Exception as e:
                print(f"[RUNNER] Compilation Exception: {e}")
                self.socketio.emit(
                    'code_output',
                    {'output': f"System Error during compilation: {e}\n"},
                    room=session_id
                )
                self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
                return

        # Execution
        print(f"[RUNNER] Run command: {run_cmd}")
        try:
            env = os.environ.copy()
            if 'python' in lang_lower:
                env['PYTHONUNBUFFERED'] = '1'

            process = subprocess.Popen(
                run_cmd,
                cwd=session_dir,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env
            )

            print(f"[RUNNER] Process started PID: {process.pid}")
            self.active_processes[session_id] = process

            t_stdout = threading.Thread(target=self._stream_reader, args=(process.stdout, session_id))
            t_stderr = threading.Thread(target=self._stream_reader, args=(process.stderr, session_id))
            t_watch = threading.Thread(target=self._watch_process, args=(session_id, process))

            t_stdout.daemon = True
            t_stderr.daemon = True
            t_watch.daemon = True

            t_stdout.start()
            t_stderr.start()
            t_watch.start()
            print("[RUNNER] Streaming output thread started")

        except Exception as e:
            print(f"[RUNNER] Execution Start Error: {e}")
            self.socketio.emit('code_output', {'output': f"Execution Error: {e}\n"}, room=session_id)
            self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)

    def send_input(self, session_id, input_text):
        print(f"[RUNNER] Input received for {session_id}: {input_text}")
        session_id = str(session_id)
        if session_id in self.active_processes:
            process = self.active_processes[session_id]
            if process.poll() is None:
                try:
                    process.stdin.write(input_text + "\n")
                    process.stdin.flush()
                except Exception as e:
                    print(f"Input Write Error: {e}")

    def _stream_reader(self, pipe, session_id):
        try:
            for line in iter(pipe.readline, ''):
                if not line:
                    break
                data = line
                print(f"[RUNNER] Output emitted: {repr(data)}")
                self.socketio.emit('code_output', {'output': data}, room=session_id)
        except Exception as e:
            print(f"[RUNNER] Stream reader error for session {session_id}: {e}")
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    def _watch_process(self, session_id, process):
        try:
            process.wait()
        finally:
            status = 'success' if process.returncode == 0 else 'error'
            print(f"[RUNNER] Process finished with status: {status}, code: {process.returncode}")
            print("[RUNNER] Process finished")
            self.socketio.emit('process_finished', {'status': status}, room=session_id)
            if session_id in self.active_processes:
                del self.active_processes[session_id]

    def _get_commands(self, language):
        lang = language.lower().strip()
        if lang == 'c':
            return 'main.c', ['gcc', 'main.c', '-o', 'main.exe'], ['.\\main.exe']
        elif 'cpp' in lang or 'c++' in lang:
            return 'main.cpp', ['g++', 'main.cpp', '-o', 'main.exe'], ['.\\main.exe']
        elif 'python' in lang:
            return 'script.py', None, [sys.executable, '-u', 'script.py']
        elif 'java' in lang:
            return 'Main.java', ['javac', 'Main.java'], ['java', 'Main']
        elif 'javascript' in lang:
            return 'script.js', None, ['node', 'script.js']
        elif 'php' in lang:
            return 'script.php', None, ['php', 'script.php']
        elif 'r' in lang:
            return 'script.R', None, ['Rscript', 'script.R']

        return None, None, None
