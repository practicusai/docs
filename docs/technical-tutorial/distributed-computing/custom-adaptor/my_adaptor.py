import practicuscore as prt
from practicuscore.dist_job import SparkAdaptor

class MySparkAdaptor(SparkAdaptor):
    @property
    def _run_cluster_coordinator_command(self) -> str:
        old_command = super()._run_cluster_coordinator_command

        # Change the command as needed
        new_command = old_command + " # add your changes here"
        
        return new_command

    @property
    def _run_cluster_agent_command(self) -> str:
        old_command = super()._run_cluster_agent_command

        new_command = old_command + " # add your changes here"
        
        return new_command
