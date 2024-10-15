import os
import re
import subprocess

from helpers.functions import get_selected_columns

from .pep_client_base import PepClientBase


class PepClientSingularity(PepClientBase):
    """
    A class used to handle Singularity container operations for PEP client tools in different environments.
    """

    # Define paths for the Singularity images in production and acceptance environments
    production_singularity_image_path = os.path.join(os.getcwd(), "client.sif")  # Update this with the actual path to your Singularity image
    production_singularity_image_path = re.sub(r'project_\w+', 'project', production_singularity_image_path)  # For HPC use
    acceptation_singularity_image_path = ""

    def _check_pepcli_path(self, pepcli_exec):
        """
        Check if the PEP CLI executable is present at the specified path.

        Args:
            pepcli_exec (str): Path to the PEP CLI executable.

        Raises:
            FileNotFoundError: If the PEP CLI executable is not found.
        """
        if not os.path.isfile(pepcli_exec):
            raise FileNotFoundError(f"PEP CLI executable not found at {pepcli_exec}. Please ensure it is installed correctly.")

    def _build_base_command(self):
        """
        Construct the base command for running the PEP CLI within a Singularity container.

        Returns:
            str: The base command to execute PEP CLI within the Singularity container.
        """
        self.pepcli_selected_image_path = ""
        if self.production:
            singularity_base_command = f"singularity exec \"{self.production_singularity_image_path}\" \"/app/pepcli\" --client-working-directory \"/config\""
            self.pepcli_selected_image_path = self.production_singularity_image_path
        else:
            singularity_base_command = f"singularity exec \"{self.acceptation_singularity_image_path}\" \"/app/pepcli\" --client-working-directory \"/config\""
            self.pepcli_selected_image_path = self.acceptation_singularity_image_path

        # Check if the PEP CLI executable exists at the specified path
        self._check_pepcli_path(self.pepcli_selected_image_path)

        if self.auth_method == "token":
            return f"{singularity_base_command} --oauth-token \"{self.pep_token_filepath}\""
        else:
            return singularity_base_command

    def pep_pull(self, command):
        """
        Execute a PEP command using the Singularity container and return the process output.

        Args:
            command (str): The PEP command to execute.

        Returns:
            int: The return code of the subprocess executing the PEP command.
        """
        command = f"{self.base_command} {command}"

        selected_columns = get_selected_columns()
        if selected_columns:
            command += ' ' + ' '.join(f'-c {column}' for column in selected_columns)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="ISO-8859-1", shell=True, bufsize=1, universal_newlines=True)

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
