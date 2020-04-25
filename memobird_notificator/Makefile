all: upload_config run cat_log

make_config_dir:
	mkdir -p /etc/memobird_notificator/

upload_config:
	cp config/* /etc/memobird_notificator/

run:
	python3 .

cat_log:
	cat /etc/memobird_notificator/logfile.log

rm_log:
	rm /etc/memobird_notificator/logfile.log
	