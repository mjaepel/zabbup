import datetime
import io
from pathlib import Path

from minio import Minio
from minio.commonconfig import ENABLED, GOVERNANCE
from minio.lifecycleconfig import AbortIncompleteMultipartUpload, LifecycleConfig, NoncurrentVersionExpiration
from minio.lifecycleconfig import Filter as LCFilter
from minio.lifecycleconfig import Rule as LCRule
from minio.retention import Retention
from minio.versioningconfig import VersioningConfig

from modules.config import config
from modules.crypto import encrypt
from modules.logger import get_logger
from modules.models import ExportObjectList


def export_s3(data: ExportObjectList) -> None:
    logger = get_logger()

    if config.outputs.s3.enable:
        if config.general.dryrun:
            logger.info("Dryrun enabled, skipping s3 export")
        else:
            logger.info("Writing to S3")

            s3_client = Minio(
                endpoint=config.outputs.s3.url,
                access_key=config.outputs.s3.access_key,
                secret_key=config.outputs.s3.secret_key,
            )

            s3_bucket_versioningconfig = s3_client.get_bucket_versioning(config.outputs.s3.bucket)
            if s3_bucket_versioningconfig.status != "Enabled":
                logger.warning(f"S3[{config.outputs.s3.bucket}]: bucket versioning is not enabled")
                logger.info(f"S3[{config.outputs.s3.bucket}]: Enabling bucket versioning")
                s3_client.set_bucket_versioning(config.outputs.s3.bucket, VersioningConfig(ENABLED))
            else:
                logger.info(f"S3[{config.outputs.s3.bucket}]: bucket versioning is enabled")

            lifecycle_config = LifecycleConfig(
                [
                    LCRule(
                        rule_id="zabbup-delete-old-backups",
                        status="Enabled",
                        abort_incomplete_multipart_upload=AbortIncompleteMultipartUpload(days_after_initiation=1),
                        # rule_filter=LCFilter(prefix=config.outputs.s3.bucket_path),
                        # rule_filter=LCFilter(prefix="/"),
                        rule_filter=LCFilter(prefix=""),
                        # expiration=Expiration(days=config.outputs.s3.lifecycle.days),
                        noncurrent_version_expiration=NoncurrentVersionExpiration(noncurrent_days=config.outputs.s3.lifecycle.days),
                    ),
                ],
            )

            s3_client.set_bucket_lifecycle(config.outputs.s3.bucket, lifecycle_config)

            for exportdata in data:
                export_dir = Path(config.outputs.s3.bucket_path) / Path(exportdata.type)
                export_filename = Path(f"{exportdata.name_sanitized}_{exportdata.id}.{config.zabbix.export_format}")
                export_path = export_dir / export_filename

                logger.debug(f"S3[{config.outputs.s3.bucket}]: Uploading file {export_path}")

                if config.inputs.model_dump()[exportdata.type]["encryption"]:
                    s3_data = encrypt(
                        content=exportdata.data,
                        key=config.general.encryption_key,
                        deterministic=config.inputs.model_dump()[exportdata.type]["encryption_deterministic"]
                    )
                else:
                    s3_data = exportdata.data.encode()

                s3_retention_rule = Retention(
                    GOVERNANCE,
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=config.outputs.s3.retention.days),
                )
                s3_client.put_object(
                    bucket_name=config.outputs.s3.bucket,
                    object_name=str(export_path),
                    data=io.BytesIO(s3_data),
                    length=len(s3_data),
                    retention=s3_retention_rule,
                )


    else:
        logger.debug("S3 output disabled")
