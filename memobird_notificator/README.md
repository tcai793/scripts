requirement:
    python3 memobird_agent requests exchangelib transmissionrpc croniter
    
install:
    crontab -e

    * * * * * cd /install_path && python3 .