import os
import subprocess

from helpers.functions import get_selected_columns

from .pep_client_base import PepClientBase


class PepClientDocker(PepClientBase):
    """
    A class for handling Docker operations related to PEP CLI commands in production or acceptance environments.

    Attributes:
        production_docker_image (str): Docker image URL for production environment.
        acceptance_docker_image (str): Docker image URL for acceptance environment.
    """
    production_docker_image = "gitlabregistry.pep.cs.ru.nl/pep-public/core/hb-prod:latest"
    acceptance_docker_image = "gitlabregistry.pep.cs.ru.nl/pep-public/core/hb-acc:latest"

    def _check_pepcli_path(self, pepcli_exec):
        """
        Checks the existence of the PEP CLI executable.

        Args:
            pepcli_exec (str): The path to the PEP CLI executable.

        Raises:
            FileNotFoundError: If the PEP CLI executable is not found.
        """
        if not os.path.isfile(pepcli_exec):
            raise FileNotFoundError(f"PEP CLI executable not found at {pepcli_exec}. Please ensure it is installed correctly.")

    def _build_base_command(self):
        """
        Builds the base command for executing Docker commands with the selected PEP CLI image.
        """
        self.base_command = "docker run -it --rm "
        self.pepcli_selected_image_path = ""

        if self.production:
            self.pepcli_selected_image_path = self.production_docker_image
        else:
            self.pepcli_selected_image_path = self.acceptance_docker_image

        if self.auth_method == "token":
            self.base_command += f" -v \"{self.pep_token_filepath}:/token:ro\""
        else:
            raise ModuleNotFoundError("Logon is not available in Docker environment")

        self.base_command += f" {self.pepcli_selected_image_path} bash -c"

    def _command(self, command):
        """
        Execute the Docker command with the specified PEP CLI command and handle authentication.

        Args:
            command (str): The PEP CLI command to execute.

        Returns:
            tuple: A tuple containing the command output and the exit code.

        Raises:
            ModuleNotFoundError: If the logon authentication method is specified.
        """
        full_command = f'{self.base_command} "/app/pepcli --client-working-directory /config  --oauth-token /token {command}"'
        result = []

        if self.auth_method == "logon":
            raise ModuleNotFoundError("Logon is not available in Docker environment")
        else:
            result, exit_code = self._command_auth_method_token(full_command)

        return self.pep_command_parser(result, exit_code)

    def pep_pull(self, command, target_folder=""):
        """
        Executes a PEP CLI pull command in Docker to download files to a specified folder.

        Args:
            command (str): The PEP CLI pull command.
            target_folder (str): The target folder to download the files to.

        Yields:
            str: Output lines from the PEP CLI process.

        Returns:
            int: The exit code from the PEP CLI process.
        """
        selected_columns = get_selected_columns()
        command = ''
        if selected_columns:
            command += ' ' + ' '.join(f'-c {column}' for column in selected_columns)

        full_command = f'{self.base_command} "cd /output && /app/pepcli --client-working-directory /config  --oauth-token /token {command}"'

        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="utf-8", bufsize=1, universal_newlines=True)

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
