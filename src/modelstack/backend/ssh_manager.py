# [10000] Beacon intent: SSH connection management for RunPod

import re
import threading
from pathlib import Path
from typing import Callable, Optional

import paramiko


# [100] Subsystem intent: SSH connection string parser

class SSHConnectionInfo:

    # [010] Method intent: initialize connection info from parsed string

    def __init__(self, user: str, host: str, port: int, key_path: Path):

        # [001] store connection parameters
        self.user = user
        self.host = host
        self.port = port
        self.key_path = key_path
        # [-----END [001]-----]

    # [-----END [010]-----]


    # [020] Method intent: parse RunPod SSH connection string

    @staticmethod
    def from_ssh_string(ssh_string: str) -> "SSHConnectionInfo":

        # [001] strip and normalize input
        ssh_string = ssh_string.strip()
        if ssh_string.startswith("$ "):
            ssh_string = ssh_string[2:]
        # [-----END [001]-----]

        # [002] extract port if present
        port = 22
        port_match = re.search(r"-p\s+(\d+)", ssh_string)
        if port_match:
            port = int(port_match.group(1))
        # [-----END [002]-----]

        # [003] extract key path if present
        key_path = Path.home() / ".ssh" / "id_ed25519"
        key_match = re.search(r"-i\s+(\S+)", ssh_string)
        if key_match:
            raw_path = key_match.group(1)
            if raw_path.startswith("~"):
                raw_path = str(Path.home() / raw_path[2:])
            key_path = Path(raw_path)
        # [-----END [003]-----]

        # [004] extract user and host
        user_host_match = re.search(r"(\S+)@(\S+)", ssh_string)
        if not user_host_match:
            raise ValueError(f"Could not parse user@host from: {ssh_string}")
        user = user_host_match.group(1)
        host = user_host_match.group(2)
        # [-----END [004]-----]

        # [005] return parsed connection info
        return SSHConnectionInfo(user, host, port, key_path)
        # [-----END [005]-----]

    # [-----END [020]-----]

# [-----END [100]-----]


# [200] Subsystem intent: SSH session manager

class SSHManager:

    # [010] Method intent: initialize manager

    def __init__(self):

        # [001] set up initial state
        self.connection_info: Optional[SSHConnectionInfo] = None
        self.client: Optional[paramiko.SSHClient] = None
        self._streams: dict[str, threading.Thread] = {}
        self._stream_stop_flags: dict[str, threading.Event] = {}
        # [-----END [001]-----]

    # [-----END [010]-----]


    # [020] Method intent: establish SSH connection

    def connect(self, ssh_string: str) -> None:

        # [001] parse connection string
        self.connection_info = SSHConnectionInfo.from_ssh_string(ssh_string)
        # [-----END [001]-----]

        # [002] configure and connect paramiko client
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.connection_info.host,
            port=self.connection_info.port,
            username=self.connection_info.user,
            key_filename=str(self.connection_info.key_path),
            timeout=15,
        )
        # [-----END [002]-----]

    # [-----END [020]-----]


    # [030] Method intent: disconnect and clean up

    def disconnect(self) -> None:

        # [001] stop all running streams
        for name in list(self._stream_stop_flags.keys()):
            self.stop_stream(name)
        # [-----END [001]-----]

        # [002] close SSH client
        if self.client:
            self.client.close()
            self.client = None
        # [-----END [002]-----]

    # [-----END [030]-----]


    # [040] Method intent: run a single command and return output

    def run_command(self, command: str, timeout: int = 30) -> tuple[str, str, int]:

        # [001] validate connection
        if not self.client:
            raise RuntimeError("Not connected. Call connect() first.")
        # [-----END [001]-----]

        # [002] execute and collect output
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        return out, err, exit_code
        # [-----END [002]-----]

    # [-----END [040]-----]


    # [050] Method intent: start a long-running process with streaming output

    def start_stream(
        self,
        name: str,
        command: str,
        on_output: Callable[[str], None],
        on_exit: Optional[Callable[[int], None]] = None,
    ) -> None:

        # [001] validate connection and prevent duplicate streams
        if not self.client:
            raise RuntimeError("Not connected. Call connect() first.")
        if name in self._streams and self._streams[name].is_alive():
            raise RuntimeError(f"Stream '{name}' is already running.")
        # [-----END [001]-----]

        # [002] set up stop flag and transport channel
        stop_flag = threading.Event()
        self._stream_stop_flags[name] = stop_flag
        transport = self.client.get_transport()
        channel = transport.open_session()
        channel.exec_command(command)
        # [-----END [002]-----]

        # [003] define stream reader thread function
        def reader():
            try:
                while not stop_flag.is_set():
                    if channel.recv_ready():
                        data = channel.recv(4096).decode("utf-8", errors="replace")
                        if data:
                            on_output(data)
                    if channel.recv_stderr_ready():
                        data = channel.recv_stderr(4096).decode("utf-8", errors="replace")
                        if data:
                            on_output(data)
                    if channel.exit_status_ready():
                        exit_code = channel.recv_exit_status()
                        if on_exit:
                            on_exit(exit_code)
                        break
                    stop_flag.wait(0.1)
            finally:
                channel.close()
                self._streams.pop(name, None)
                self._stream_stop_flags.pop(name, None)
        # [-----END [003]-----]

        # [004] start reader thread
        thread = threading.Thread(target=reader, name=f"stream-{name}", daemon=True)
        thread.start()
        self._streams[name] = thread
        # [-----END [004]-----]

    # [-----END [050]-----]


    # [060] Method intent: stop a running stream

    def stop_stream(self, name: str) -> None:

        # [001] signal stop and wait for thread
        flag = self._stream_stop_flags.get(name)
        if flag:
            flag.set()
        thread = self._streams.get(name)
        if thread and thread.is_alive():
            thread.join(timeout=5)
        # [-----END [001]-----]

    # [-----END [060]-----]


    # [070] Method intent: check if connection is active

    def is_connected(self) -> bool:

        # [001] verify client and transport are alive
        if not self.client:
            return False
        transport = self.client.get_transport()
        return transport is not None and transport.is_active()
        # [-----END [001]-----]

    # [-----END [070]-----]

# [-----END [200]-----]