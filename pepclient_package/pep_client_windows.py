import os
import subprocess
import tempfile
import platform

from .pep_client_base import PepClientBase


class PepClientWindows(PepClientBase):
    """
    A class to interact with the PEP command line interface on Windows systems.

    Attributes:
        production_cli (str): Path to the production version of the PEP CLI executable.
        acceptation_cli (str): Path to the acceptance testing version of the PEP CLI executable.
    """
    def __init__(self, pep_token_filepath="", production=True, auth_method="token"):
        """
        Initializes the PepClientWindows class by setting up the CLI paths and
        passing initialization data to the PepClientBase class.

        Args:
            pep_token_filepath (str): The file path to the authentication token.
            production (bool): Flag to indicate if the production environment should be used.
            auth_method (str): The authentication method to use ("token" or "logon").
        """
        self.production_cli = os.path.join(os.environ['PROGRAMFILES'], "PEP-Client (hb prod)", "pepcli.exe")
        self.acceptation_cli = os.path.join(os.environ['PROGRAMFILES'], "PEP-Client (hb acc)", "pepcli.exe")
        super().__init__(pep_token_filepath=pep_token_filepath, production=production, auth_method=auth_method)

    def _check_pepcli_path(self, pepcli_exec):
        """
        Check if the PEP CLI executable exists at the specified path.

        Args:
            pepcli_exec (str): The path to the PEP CLI executable.

        Raises:
            FileNotFoundError: If the PEP CLI executable is not found.
        """
        if not os.path.isfile(pepcli_exec):
            raise FileNotFoundError(f"PEP CLI executable not found at {pepcli_exec}. Please ensure it is installed correctly.")

    def _build_base_command(self):
        """
        Build the base command for interacting with the PEP CLI based on the mode of operation (production or acceptance).

        Returns:
            str: The base command to run the PEP CLI.
        """
        if self.production:
            pepcli_exec = self.production_cli
        else:
            pepcli_exec = self.acceptation_cli

        self._check_pepcli_path(pepcli_exec)

        if self.auth_method == "token":
            return f"\"{pepcli_exec}\" --oauth-token \"{self.pep_token_filepath}\""
        else:
            return f"\"{pepcli_exec}\""

    def pep_logon(self):
        """
        Log on to the PEP system using the browser. This will open a browser login.
        """
        command = ""

        if self.production:
            command = self.production_cli.replace('pepcli.exe', 'pepLogon.exe')
        else:
            command = self.acceptation_cli.replace('pepcli.exe', 'pepLogon.exe')

        subprocess.run(command, cwd=self.temp_dir_logon.name)

    def pep_pull(self, command):
        """
        Execute a PEP pull command to retrieve data.

        Args:
            command (str): The PEP pull command to execute.

        Yields:
            str: Output lines from the command execution.

        Returns:
            int: The return code of the process.
        """
        command = f"{self.base_command} {command}"

        with tempfile.TemporaryDirectory() as tempdir:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, bufsize=1, universal_newlines=True, cwd=tempdir)

            while True:
                if not process.stdout:
                    break

                output_line = process.stdout.readline()
                if output_line == '' and process.poll() is not None:
                    break
                if output_line:
                    yield output_line.strip()
            rc = process.poll()
        return rc
