# Zabbup - Configuration backup utility for Zabbix entities

* Features
  * Backups via Zabbix API configuration.export of
    * Hosts
    * Host groups
    * Templates
    * Template groups
    * Maps
    * Mediatypes
    * Images
  * Export to
    * Remote git repository
    * S3 compatible API
  * Encryption
    * optional with deterministic encryption results. WARNING: less secure!
      * With non-deterministic encryption the output files will change each time. This will create a lot of changes in backup storage (e.g. Git)
      * You have to decide what you want to protect against with encryption and whether the benefit of taking up less space overweighs the greater need for protection.

* ToDo
  * Documentation :D
  * S3 lifecycle and retention policys are buggy
  * tool for listing backups
  * tool for restoring backups
  * additional backup inputs:
    * Actions
    * Authentication
    * Autoregistration
    * Connectors
    * Correlation
    * Dashboard
    * Global Macro
    * Housekeeper
    * Proxy
    * Proxy group
    * Regular expression
    * Report
    * Role
    * Script
    * Service
    * Settings
    * SLA
    * Task
    * User
    * User directory
    * User group
