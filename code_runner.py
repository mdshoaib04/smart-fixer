import subprocess
import os
import threading
import sys
import uuid
import re
import time

class CodeRunner:
    def __init__(self, socket_io):
        self.socketio = socket_io
        self.active_processes = {}
        self.base_temp_dir = os.path.join(os.getcwd(), 'temp_exec')
        if not os.path.exists(self.base_temp_dir):
            os.makedirs(self.base_temp_dir)
        # Track per-session execution metadata for idle timeout only
        self.session_meta = {}
        # Idle timeout: only kill when NO output AND NO input for this many seconds (2–3 min)
        self.idle_timeout_seconds = 150

    def _detect_html(self, code):
        """Detect if code is HTML - render in iframe, DO NOT send to runner"""
        s = code.strip()
        if not s:
            return False
        lower = s.lower()
        # If code starts with <!DOCTYPE or <html: render directly, never run
        if lower.startswith('<!doctype') or lower.startswith('<html'):
            return True
        # Broader check for other HTML indicators in first 200 chars
        html_indicators = [
            '<!doctype html>', '<html', '<head', '<body', '<div', '<span',
            '<h1', '<h2', '<h3', '<p>', '<script', '<style', '<link',
            '<?xml', '<svg', '<canvas', '<meta', '<title'
        ]
        return any(lower.startswith(ind) or lower[:200].find(ind) >= 0 for ind in html_indicators)

    def _parse_error(self, error_text, language):
        """Parse error and extract line number, message, and suggestion"""
        error_text = error_text.strip()
        if not error_text:
            return None, None, None
        
        line_num = None
        message = error_text
        suggestion = None
        
        # Python errors: File "script.py", line 4, in <module>
        py_match = re.search(r'File\s+["\']?[^"\']+["\']?,\s+line\s+(\d+)', error_text, re.IGNORECASE)
        if py_match:
            line_num = int(py_match.group(1))
            # Use the last non-empty line as the "exact" error (e.g. "SyntaxError: ...")
            lines = [ln.strip() for ln in error_text.splitlines() if ln.strip()]
            if lines:
                message = lines[-1]
        
        # C/C++ errors: main.c:4:5: error: ...
        c_match = re.search(r'(\w+\.(?:c|cpp)):(\d+):(\d+):\s*(error|warning):\s*(.+?)(?:\n|$)', error_text, re.IGNORECASE)
        if c_match:
            line_num = int(c_match.group(2))
            message = c_match.group(5).strip()
        
        # Java errors: Main.java:4: error: ...
        java_match = re.search(r'(\w+\.java):(\d+):\s*error:\s*(.+?)(?:\n|$)', error_text, re.IGNORECASE)
        if java_match:
            line_num = int(java_match.group(2))
            message = java_match.group(3).strip()
        
        # Use STRICT, simple suggestion rules
        lowered = error_text.lower()
        if 'syntaxerror' in lowered:
            suggestion = "Check missing colon/semicolon"
        elif 'valueerror' in lowered and 'unpack' in lowered:
            suggestion = "Enter both values separated by space"
        
        return line_num, message, suggestion

    def run_code(self, session_id, language, code):
        print("[RUNNER] Request received")
        session_id = str(session_id)
        print(f"[RUNNER] Language selected: {language}")
        
        # Detect HTML/CSS/JS/JSP BEFORE execution
        if self._detect_html(code):
            print("[RUNNER] Detected HTML/CSS/JS - rendering instead of executing")
            self.socketio.emit('render_html', {'content': code}, room=session_id)
            return
        
        run_id = str(uuid.uuid4())[:8]
        session_dir = os.path.join(self.base_temp_dir, f"{session_id}_{run_id}")
        os.makedirs(session_dir, exist_ok=True)
        # Best-effort sandbox: restrict permissions on the temp directory
        try:
            os.chmod(session_dir, 0o700)
        except Exception:
            # On some platforms (e.g. Windows) chmod is limited – ignore failures
            pass

        lang_lower = language.lower()
        if lang_lower in ['html', 'html5', 'htm', 'css', 'javascript (web)', 'jsp']:
            self.socketio.emit('render_html', {'content': code}, room=session_id)
            return

        filename, compile_cmd, run_cmd = self._get_commands(language)
        
        if not filename:
            self.socketio.emit('code_output', {'output': f"Error: Language '{language}' is not supported yet.\n"}, room=session_id)
            self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
            return

        # STRICT Windows fix: run compiled exe by full absolute path (avoids WinError 2)
        if lang_lower in ['c', 'cpp', 'c++']:
            exe_path = os.path.join(session_dir, "main.exe")
            run_cmd = [exe_path]

        file_path = os.path.join(session_dir, filename)
        print(f"[RUNNER] Writing file: {file_path}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
             self.socketio.emit('code_output', {'output': f"Error writing file: {e}\n"}, room=session_id)
             self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
             return

        # For C / C++, inject a tiny helper that disables stdio buffering so
        # prompts like `printf("Enter name: ");` flush immediately when piped.
        if lang_lower in ['c', 'cpp', 'c++'] and compile_cmd:
            try:
                nobuf_path = os.path.join(session_dir, 'nobuf.c')
                with open(nobuf_path, 'w', encoding='utf-8') as nb:
                    nb.write(
                        '#include <stdio.h>\n'
                        'void init_stdout(void) __attribute__((constructor));\n'
                        'void init_stdout(void) { setvbuf(stdout, NULL, _IONBF, 0); }\n'
                    )
                # Insert helper translation unit after the source file argument.
                # Example: ['gcc', 'main.c', '-o', 'main.exe']
                # becomes: ['gcc', 'main.c', 'nobuf.c', '-o', 'main.exe']
                if len(compile_cmd) >= 3:
                    compile_cmd = compile_cmd[:2] + ['nobuf.c'] + compile_cmd[2:]
            except Exception as e:
                # If helper injection fails, continue with normal compilation
                print(f"[RUNNER] Failed to inject nobuf helper: {e}")

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
                    timeout=15  # Allow slower compiles (up to 15s)
                )
                print(f"[RUNNER] Compilation return code: {result.returncode}")
                if result.returncode != 0:
                    print(f"[RUNNER] Compilation Failed: {result.stderr}")
                    error_text = result.stderr or result.stdout or "Unknown compilation error"
                    line_num, error_msg, suggestion = self._parse_error(error_text, language)
                    
                    if line_num:
                        formatted_error = f"Error (line {line_num}): {error_msg}\n"
                    else:
                        formatted_error = f"Compilation Error:\n{error_text}\n"
                    
                    self.socketio.emit('code_output', {'output': formatted_error, 'type': 'error'}, room=session_id)
                    
                    if suggestion:
                        self.socketio.emit('code_suggestion', {'suggestion': suggestion}, room=session_id)
                    
                    self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
                    return
            except subprocess.TimeoutExpired:
                print("[RUNNER] Compilation Timed Out")
                self.socketio.emit('code_output', {'output': "Error: Compilation timed out.\n", 'type': 'error'}, room=session_id)
                self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
                return
            except Exception as e:
                print(f"[RUNNER] Compilation Exception: {e}")
                self.socketio.emit('code_output', {'output': f"System Error during compilation: {e}\n", 'type': 'error'}, room=session_id)
                self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)
                return

        # Execution
        print(f"[RUNNER] Run command: {run_cmd}")
        try:
            env = os.environ.copy()
            if 'python' in lang_lower:
                # Force unbuffered Python execution
                env['PYTHONUNBUFFERED'] = '1'

            stderr_capture = bytearray()

            process = subprocess.Popen(
                run_cmd,
                cwd=session_dir,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,  # Unbuffered at OS level – we handle our own buffering
                text=False,  # Binary mode for byte-by-byte reading
                env=env
            )

            print(f"[RUNNER] Process started PID: {process.pid}")
            self.active_processes[session_id] = process

            # Track last output or input for idle timeout only
            self.session_meta[session_id] = {
                'last_activity': time.time(),
            }

            t_stdout = threading.Thread(
                target=self._stream_reader,
                args=(process.stdout, session_id, 'stdout', None),
            )
            t_stderr = threading.Thread(
                target=self._stream_reader,
                args=(process.stderr, session_id, 'stderr', stderr_capture),
            )
            t_watch = threading.Thread(
                target=self._watch_process,
                args=(session_id, process, language, stderr_capture, t_stdout, t_stderr),
            )

            t_stdout.daemon = True
            t_stderr.daemon = True
            t_watch.daemon = True

            t_stdout.start()
            t_stderr.start()
            t_watch.start()
            print("[RUNNER] Streaming output thread started")

        except Exception as e:
            print(f"[RUNNER] Execution Start Error: {e}")
            self.socketio.emit('code_output', {'output': f"Execution Error: {e}\n", 'type': 'error'}, room=session_id)
            self.socketio.emit('process_finished', {'status': 'error'}, room=session_id)

    def send_input(self, session_id, input_text):
        print(f"[RUNNER] Input received for {session_id}: {input_text}")
        session_id = str(session_id)
        if session_id in self.active_processes:
            process = self.active_processes[session_id]
            if process.poll() is None:
                try:
                    if process.stdin:
                        process.stdin.write((input_text + "\n").encode())
                        process.stdin.flush()
                        meta = self.session_meta.get(session_id)
                        if meta is not None:
                            meta['last_activity'] = time.time()
                except Exception as e:
                    print(f"Input Write Error: {e}")

    def _stream_reader(self, pipe, session_id, stream_type, capture_buffer):
        """
        Stream output byte-by-byte for real-time display.

        This avoids readline() so prompts like `print("Enter name: ", end="")`
        are sent to the client immediately, even without a trailing newline.
        """
        try:
            while True:
                char = pipe.read(1)
                if not char:
                    break

                # Capture raw bytes for later error parsing if requested
                if capture_buffer is not None:
                    capture_buffer += char

                # Decode a single character (or partial UTF-8) and emit it
                try:
                    data = char.decode('utf-8', errors='replace')
                except Exception as e:
                    print(f"[RUNNER] Decode error ({stream_type}): {e}")
                    data = '?'

                meta = self.session_meta.get(session_id)
                if meta is not None:
                    meta['last_activity'] = time.time()

                self.socketio.emit(
                    'code_output',
                    {'output': data, 'type': stream_type, 'session_id': session_id},
                    room=session_id,
                )
        except Exception as e:
            print(f"[RUNNER] Stream reader error for session {session_id}: {e}")
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    def _watch_process(self, session_id, process, language, stderr_capture, t_stdout, t_stderr):
        """
        Monitor the child process. Idle timeout only: kill if NO output AND NO input
        for idle_timeout_seconds. Never kill while waiting for user input.
        """
        try:
            while True:
                if process.poll() is not None:
                    break

                meta = self.session_meta.get(session_id) or {}
                now = time.time()
                last_activity = meta.get('last_activity', now)

                # Idle timeout: only kill when no output AND no input for 2–3 min
                if (
                    self.idle_timeout_seconds is not None
                    and now - last_activity > self.idle_timeout_seconds
                ):
                    try:
                        process.kill()
                    except Exception:
                        pass
                    timeout_msg = (
                        f"\nExecution idle timed out after "
                        f"{self.idle_timeout_seconds} seconds (no output, no input).\n"
                    )
                    self.socketio.emit(
                        'code_output',
                        {
                            'output': timeout_msg,
                            'type': 'error',
                            'session_id': session_id,
                        },
                        room=session_id,
                    )
                    break

                time.sleep(0.1)
        finally:
            try:
                t_stdout.join(timeout=1)
            except Exception:
                pass
            try:
                t_stderr.join(timeout=1)
            except Exception:
                pass

            status = 'success' if process.returncode == 0 else 'error'
            print(f"[RUNNER] Process finished with status: {status}, code: {process.returncode}")
            print("[RUNNER] Process finished")
            
            # Parse stderr for runtime errors if process failed
            if process.returncode != 0:
                try:
                    error_text = (stderr_capture or b'').decode('utf-8', errors='replace')
                    if error_text.strip():
                        line_num, error_msg, suggestion = self._parse_error(error_text, language)
                        if line_num:
                            formatted_error = f"\nError (line {line_num}): {error_msg}\n"
                        else:
                            formatted_error = f"\nRuntime Error:\n{error_text}\n"
                        
                        self.socketio.emit(
                            'code_output',
                            {'output': formatted_error, 'type': 'error', 'session_id': session_id},
                            room=session_id,
                        )
                        
                        if suggestion:
                            self.socketio.emit('code_suggestion', {'suggestion': suggestion}, room=session_id)
                except Exception:
                    pass
            
            self.socketio.emit('process_finished', {'status': status}, room=session_id)
            if session_id in self.active_processes:
                del self.active_processes[session_id]
            # Clean up sandbox metadata
            if session_id in self.session_meta:
                del self.session_meta[session_id]

    def _get_commands(self, language):
        lang = language.lower().strip()
        if lang == 'c':
            return 'main.c', ['gcc', 'main.c', '-o', 'main.exe'], None  # run_cmd set by caller
        elif 'cpp' in lang or 'c++' in lang:
            return 'main.cpp', ['g++', 'main.cpp', '-o', 'main.exe'], None  # run_cmd set by caller
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
