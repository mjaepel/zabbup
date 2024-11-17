from modules.config import config
from modules.models import ExportObjectList
from modules.crypto import encrypt
from modules.logger import GetLogger
import git
import tempfile
import os


def Git(data: ExportObjectList):
    logger = GetLogger()

    if config.outputs.git.enable:
        if config.general.dryrun:
            logger.info("Dryrun enabled, skipping git export")
            return
        else:
            logger.info("Exporting to git")
            with tempfile.TemporaryDirectory() as tmpdirname:
                repo = git.Repo.clone_from(
                    config.outputs.git.repo, tmpdirname, depth=1, sparse=True
                )
                repo.git.rm("-r", "--sparse", ".")

                for exportdata in data:
                    export_dir = os.path.join(tmpdirname, exportdata.type)
                    export_filename = os.path.join(
                        export_dir,
                        f"{exportdata.name_sanitized}_{exportdata.id}.{config.zabbix.export_format}",
                    )

                    os.makedirs(export_dir, exist_ok=True)
                    if config.general.encryption or config.inputs.model_dump()[exportdata.type]["encryption"]:
                        with open(export_filename, "wb") as export_file:
                            export_file.write(encrypt(exportdata.data, config.general.encryption_key))
                    else:
                        with open(export_filename, "w") as export_file:
                            export_file.write(exportdata.data)

                repo.git.add(".", "--sparse")
                repo_changes = repo.git.status("--porcelain")
                if repo_changes:
                    logger.debug(f"Changes to commit: {repo_changes}")
                    repo.git.commit("-m", "Exported data")
                    repo.git.push()
    else:
        logger.debug("Git export disabled")
